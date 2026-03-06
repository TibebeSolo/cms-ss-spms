from django.db import transaction
from django.conf import settings
from .models import SSStudentProfile, AttendanceSession, AttendanceRecord, StudentStatus
from apps.people.services import EthiopianDateService
from apps.audit.services import AuditLogger
from apps.people.models import Christian

class StudentService:
    @staticmethod
    @transaction.atomic
    def generate_ssid(instance):
        """
        Format: {SSAbbrev}{YY}{RRR}
        YY: joined_year_eth (last 2 digits)
        RRR: 3-digit roll number scoped to the year
        """
        ss_abbrev = getattr(settings, 'SS_ABBREV', 'SS')
        year = instance.joined_year_eth or EthiopianDateService.get_current_eth_year()
        year_yy = str(year)[-2:]

        # Lock rows for this specific joined year to ensure unique roll assignment
        last_student = SSStudentProfile.objects.filter(
            joined_year_eth=year
        ).select_for_update().order_by('-ss_roll_number').first()

        roll = (last_student.ss_roll_number + 1) if last_student else 1
        
        ssid = f"{ss_abbrev}{year_yy}{roll:03d}"

        AuditLogger.log(
            actor=instance.user,
            action_type="SSID_GENERATED",
            entity=instance,
            metadata={
                "ssid": ssid,
                "christian_name": instance.first_name + " " + instance.father_name,
                "roll_number": roll,
                "entry_year": year
            }
        )

        return ssid, roll, year

# Attendance Service
class AttendanceWorkflowService:
    @staticmethod
    @transaction.atomic
    def initialize_session(group_id, eth_date, user, scope='CLASSGROUP'):
        """
        Creates a session and auto-generates AttendanceRecords for all 
        active students in the targeted group.
        """
        session = AttendanceSession.objects.create(
            session_date_eth_year=eth_date['year'],
            session_date_eth_month=eth_date['month'],
            session_date_eth_day=eth_date['day'],
            scope_type=scope,
            class_group_id=group_id,
            created_by=user,
            state='DRAFT'
        )

        # Fetch active students for this specific group/grade
        # Logic matches students assigned to this ClassGroup
        students = SSStudentProfile.objects.filter(is_active=True)
        if group_id:
            # Assuming a relationship exists between Profile and ClassGroup
            students = students.filter(class_group_id=group_id)

        records = [
            AttendanceRecord(
                attendance_session=session,
                ss_student_profile=student,
                status='ABSENT', # Default to Absent for safety
                created_by=user
            ) for student in students
        ]
        AttendanceRecord.objects.bulk_create(records)

        AuditLogger.log(
            actor=user,
            action_type="ATTENDANCE_SESSION_INITIALIZED",
            entity=session,
            metadata={
                "group_id": group_id,
                "date": eth_date,
                "students_count": len(records)
            }
        )
        return session
    
    @staticmethod
    @transaction.atomic
    def update_record(record_id, new_status, user, reason="Initial Entry"):
        from .models import AttendanceRecord, AttendanceEditLog
        
        record = AttendanceRecord.objects.select_for_update().get(id=record_id)
        before_status = record.status
        
        if before_status != new_status:
            # 1. Update the record
            record.status = new_status
            record.save()
            
            # 2. Log the edit specifically in the AttendanceEditLog
            AttendanceEditLog.objects.create(
                attendance_record=record,
                edited_by=user,
                before_status=before_status,
                after_status=new_status,
                reason_note=reason
            )
            
            # 3. Log in the global AuditLog (Step 5)
            from audit.services import AuditLogger
            AuditLogger.log(user, 'ATTENDANCE_RECORD_UPDATE', record, {
                'before': before_status, 
                'after': new_status
            })
    
    @staticmethod
    @transaction.atomic
    def submit_for_approval(session_id, user):
        from .models import AttendanceSession, AttendanceApproval
        
        session = AttendanceSession.objects.get(id=session_id)
        session.state = 'PENDING_APPROVAL'
        session.save()
        
        AttendanceApproval.objects.create(
            attendance_session=session,
            submitted_by=user
        )

    @staticmethod
    @transaction.atomic
    def final_approve(session_id, approver_user, comment):
        from .models import AttendanceSession, AttendanceApproval
        
        session = AttendanceSession.objects.get(id=session_id)
        approval = session.approval
        
        session.state = 'APPROVED'
        session.save()
        
        approval.approved_by = approver_user
        approval.approved_at = timezone.now()
        approval.comment = comment
        approval.save()

        AuditLogger.log(
            actor=approver_user,
            action_type="ATTENDANCE_SESSION_APPROVED",
            entity=session,
            metadata={
                "comment": comment,
                "date" : approval.approved_at,
            }
        )

# 
class StudentRegistrationService:
    @staticmethod
    @transaction.atomic
    def register_new_student(christian_id, registration_data, actor_user):
        """
        Converts an existing Christian into an SS Student.
        """
        christian = Christian.objects.get(id=christian_id)
        
        # 1. Create Profile
        student = SSStudentProfile(
            christian=christian,
            grade=registration_data['grade'],
            section=registration_data['section'],
            joined_year_eth=registration_data['joined_year_eth'],
            status=StudentStatus.objects.get(is_default=True),
            created_by=actor_user
        )
        
        # 2. SSID is auto-generated in the model's save() or via dedicated service
        # (Referencing your StudentService.generate_ssid logic)
        student.save() 
        
        # 3. Audit Log (Requirement 16)
        AuditLogger.log(
            actor=actor_user,
            action_type="STUDENT_REGISTERED",
            entity=student,
            metadata={"ssid": student.ssid, "name": christian.full_name}
        )
        
        return student