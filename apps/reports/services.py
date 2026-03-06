from sundayschool.models import SSStudentProfile, AttendanceRecord, AttendanceSession
from melody.models import MezemranMembership
from .models import GeneratedReport
from .utils.pdf_engine import EOTCPDFBuilder
from apps.audit.services import AuditLogger
import openpyxl

class AttendanceReportService:
    @staticmethod
    def generate_monthly_pdf(buffer, user, year_eth, month_eth, class_group=None, lang='am'):
        # 1. Fetch sessions
        sessions = AttendanceSession.objects.filter(
            session_date_eth_year=year_eth,
            session_date_eth_month=month_eth,
            state='APPROVED'
        )
        if class_group:
            sessions = sessions.filter(class_group=class_group)

        # 2. Build PDF
        title = f"የወርኃዊ መገኘት ሪፖርት - {month_eth}/{year_eth}" if lang == 'am' else f"Monthly Attendance - {month_eth}/{year_eth}"
        builder = EOTCPDFBuilder(buffer, lang=lang)
        builder.draw_header(title)
        
        # (Table logic would go here using reportlab.platypus.Table)
        
        builder.draw_footer()
        builder.canvas.save()
        
        # 3. Save Record in GeneratedReport
        GeneratedReport.objects.create(
            report_type='ATTENDANCE_MONTHLY',
            generated_by=user,
            parameters={'year': year_eth, 'month': month_eth, 'lang': lang, 'group': class_group.id if class_group else None}
        )

        # 4. Audit Log
        AuditLogger.log(user, 'EXPORT_ATTENDANCE_PDF', 'AttendanceSession', metadata={'year': year_eth})

class MezemranReportingService:
    @staticmethod
    def export_roster_excel(user, lang='am'):
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Mezemran Roster"
        
        # Bilingual Headers
        headers = ["MZ-ID", "Full Name", "Sex", "Grade", "Entry Year"] if lang == 'en' else ["መለያ ቁጥር", "ሙሉ ስም", "ጾታ", "ክፍል", "የገቡበት ዓ.ም"]
        ws.append(headers)
        
        members = MezemranMembership.objects.filter(status='ACTIVE').select_related('ss_student_profile__christian')
        
        for m in members:
            p = m.ss_student_profile.christian
            ws.append([
                m.mezemran_id,
                f"{p.first_name} {p.father_name}",
                p.sex,
                str(m.ss_student_profile.grade),
                m.mezmur_entry_year_eth
            ])
            
        # Record the generation
        GeneratedReport.objects.create(
            report_type='MEZEMRAN_ROSTER',
            generated_by=user,
            parameters={'format': 'excel', 'lang': lang}
        )
        return wb

class StudentReportingService:
    @staticmethod
    def generate_profile_summary_pdf(buffer, user, student, lang='am'):
        """Generates the printable summary for transfers/archiving"""
        builder = EOTCPDFBuilder(buffer, lang=lang)
        title = "የተማሪ ማህደር ማጠቃለያ" if lang == 'am' else "Student Profile Summary"
        builder.draw_header(title, subtitle=f"SSID: {student.ssid}")
        
        # Add Student Data to PDF logic...
        
        builder.draw_footer()
        builder.canvas.save()
        
        GeneratedReport.objects.create(
            report_type='STUDENT_PROFILE',
            generated_by=user,
            parameters={'student_id': student.id, 'lang': lang}
        )