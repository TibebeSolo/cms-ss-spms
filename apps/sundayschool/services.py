from .models import (
    SSStudentProfile, AttendanceSession, AttendanceRecord, 
    StudentStatus, ClassGroup, AttendanceApproval
)
from people.services import EthiopianDateService
from audit.services import AuditLogger
from people.models import Christian, ConfessionFather
from identity.models import UserAccount, UserRole, Role
from django.db import transaction
from django.conf import settings
from django.utils import timezone

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
    def initialize_session(class_group_id, eth_date_dict, creator_user):
        """
        Initializes a session and creates blank records for all students in that group.
        """
        class_group = ClassGroup.objects.get(id=class_group_id)
        
        # 1. Create the Session
        session = AttendanceSession.objects.create(
            class_group=class_group,
            attendance_date_eth_year=eth_date_dict['year'],
            attendance_date_eth_month=eth_date_dict['month'],
            attendance_date_eth_day=eth_date_dict['day'],
            status='DRAFT',
            created_by=creator_user
        )

        # 2. Get all ACTIVE students in this class
        students = SSStudentProfile.objects.filter(
            grade=class_group.grade, 
            section=class_group.section,
            is_active=True
        )

        # 3. Bulk create records (Default: ABSENT as per requirements)
        records = [
            AttendanceRecord(
                attendance_session=session,
                ss_student_profile=student,
                status='ABSENT',
                created_by=creator_user
            ) for student in students
        ]
        AttendanceRecord.objects.bulk_create(records)       

        AuditLogger.log(
            actor=creator_user,
            action_type="ATTENDANCE_SESSION_INITIALIZED",
            entity=session,
            metadata={
                "group_id": class_group_id,
                "date": eth_date_dict,
                "students_count": len(records)
            }
        )
        return session
    
    @staticmethod
    def update_single_record(record_id, new_status, actor_user):
        """HTMX target: Updates one student's status instantly."""
        record = AttendanceRecord.objects.get(id=record_id)
        
        # RBAC Check: Cannot edit if session is PENDING or APPROVED
        if record.attendance_session.status != 'DRAFT':
            raise PermissionError("Cannot edit a locked session.")

        before_status = record.status
        record.status = new_status
        record.save()

        AuditLogger.log(
            actor=actor_user,
            action_type="ATTENDANCE_RECORD_UPDATE",
            entity=record,
            metadata={
                "before": before_status,
                "after": new_status,
                "session_id": record.attendance_session_id,
            }
        )

        return record
    
    @staticmethod
    @transaction.atomic
    def submit_for_approval(session, expert_user):
        """
        Transition session from DRAFT to PENDING_APPROVAL
        """
        if session.status != 'DRAFT':
            raise ValueError("Only draft sessions can be submitted.")
            
        session.status = 'PENDING_APPROVAL'
        session.save()
        
        # Create the initial Approval record
        AttendanceApproval.objects.create(
            attendance_session=session,
            submitted_by=expert_user
        )

        # Log the submission
        AuditLogger.log(
            actor=expert_user,
            action_type="ATTENDANCE_SESSION_SUBMITTED",
            entity=session,
            metadata={
                "date": session.attendance_date_eth_day,
                "month": session.attendance_date_eth_month,
                "year": session.attendance_date_eth_year
            }
        )

    @staticmethod
    @transaction.atomic
    def final_approve(session, approver_user, comment):
        """
        Finalizes the session, setting status to APPROVED and recording the approver.
        """
        if session.status != 'PENDING_APPROVAL':
            raise ValueError("Session is not in a pending state.")
            
        session.status = 'APPROVED'
        session.save()
        
        approval = session.approval # Accessing OneToOneField
        approval.approved_by = approver_user
        approval.approved_at = timezone.now()
        approval.comment = comment
        approval.save()

        # Log the approval
        AuditLogger.log(
            actor=approver_user,
            action_type="ATTENDANCE_SESSION_APPROVED",
            entity=session,
            metadata={
                "comment": comment,
                "date" : approval.approved_at,
                "day": session.attendance_date_eth_day,
                "month": session.attendance_date_eth_month,
                "year": session.attendance_date_eth_year
            }
        )

# Brifge Class between Sunday School and Imports APPs; For Attendnce Import
class AttendanceImportService:
    @staticmethod
    @transaction.atomic
    def process_file_row(session, row_data, actor_user):
        """
        Parses a single row from the CSV/Excel.
        row_data format: {'ssid': 'SS16001', 'status': 'Present', 'note': '...'}
        """
        try:
            student = SSStudentProfile.objects.get(ssid=row_data['ssid'])
            
            # Map mobile status strings to our internal codes
            status_map = {
                'Present': 'PRESENT',
                'Absent': 'ABSENT',
                'Late': 'LATE',
                'Excused': 'EXCUSED'
            }
            db_status = status_map.get(row_data['status'], 'ABSENT')

            before_status = "UNKNOWN" # Import context doesn't always have before status
            
            # Create or Update the record
            record, created = AttendanceRecord.objects.update_or_create(
                attendance_session=session,
                ss_student_profile=student,
                defaults={
                    'status': db_status,
                    'note': row_data.get('note', ''),
                    'created_by': actor_user
                }
            )

            # Log the import Update
            AuditLogger.log(
                actor=actor_user,
                action_type="ATTENDANCE_RECORD_UPDATE",
                entity=record,
                metadata={
                    "before": before_status,
                    "after": db_status,
                    "source": "IMPORT"
                }
            )
        except SSStudentProfile.DoesNotExist:
            raise ValueError(f"Student SSID {row_data['ssid']} not found.")

# Student Registration Service
class StudentRegistrationService:
    @staticmethod
    @transaction.atomic
    def register_new_student(christian_data, ss_data, role, actor_user):
        """
        Unified service to register a student and optionally elevate them to an Officer.
        """
        # 1. Create Christian record with all personal and address info
        christian = Christian.objects.create(**christian_data)
        
        # 2. Get default status for new students
        default_status = StudentStatus.objects.filter(is_default=True).first()
        if not default_status:
            default_status, _ = StudentStatus.objects.get_or_create(name="Active", is_default=True)

        # 3. Handle Confession Father (Manual Entry)
        confession_father = None
        cf_name = ss_data.get('confession_father_name')
        if cf_name:
            confession_father, created = ConfessionFather.objects.get_or_create(
                full_name=cf_name,
                defaults={'phone': 'N/A', 'servant_church': 'N/A', 'residence': 'N/A'}
            )

        # 4. Create SSStudentProfile
        student = SSStudentProfile.objects.create(
            christian=christian,
            grade=ss_data['grade'],
            section=ss_data['section'],
            joined_year_eth=ss_data['joined_year_eth'],
            confession_father=confession_father,
            student_status=default_status,
            registration_state='ACTIVE' # Defaulting to ACTIVE for this direct registration
        )

        # 5. Handle Contact Person
        contact_data = ss_data.get('contact_person')
        if contact_data and contact_data.get('full_name'):
            from people.models import RelationshipType, ContactPerson
            rel_type, _ = RelationshipType.objects.get_or_create(name=contact_data.get('relationship', 'Parent'))
            contact = ContactPerson.objects.create(
                full_name=contact_data['full_name'],
                relationship_type=rel_type,
                phone=contact_data['phone'],
                address=contact_data['address'],
                linked_christian=christian
            )
            # Create the link
            from .models import StudentContactLink
            StudentContactLink.objects.create(
                ss_student_profile=student,
                contact_person=contact,
                is_primary=True
            )
        
        # 4. SSID is auto-generated in the model's save() method.
        # Calling save again just in case, though first create() should have handled it.
        # But wait, save() in models.py requires student.ssid to be empty to generate.
        # The logic in models.py:
        # if not self.ssid:
        #     ssid, roll, year = StudentService.generate_ssid(self)
        
        # Audit Log for registration
        AuditLogger.log(
            actor=actor_user,
            action_type="STUDENT_REGISTERED",
            entity=student,
            metadata={
                "ssid": student.ssid, 
                "name": f"{christian.first_name} {christian.father_name}", 
                "joined_year": student.joined_year_eth
            }
        )

        # 5. IF a Role is selected -> It's an Officer
        temp_pwd = None
        if role:
            # Generate a 12-char random password
            temp_pwd = UserAccount.objects.make_random_password(length=12)
            user = UserAccount.objects.create_user(
                username=student.ssid, # Login with SSID
                password=temp_pwd,
                email=christian.email or "",
                first_name=christian.first_name,
                last_name=christian.father_name,
                is_staff=True
            )
            user.requires_password_change = True
            user.save()
            
            UserRole.objects.create(user=user, role=role)
            
            # Log the officer promotion
            AuditLogger.log(
                actor=actor_user,
                action_type="OFFICER_ACCOUNT_CREATED",
                entity=user,
                metadata={"role": role.name, "username": user.username}
            )
        
        return student, temp_pwd