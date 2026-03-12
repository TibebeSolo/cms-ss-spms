from sundayschool.services import AttendanceImportService
import csv
import io
from django.utils import timezone
from django.db import transaction
from .models import ImportRun, ImportRowError
from audit.services import AuditLogger # From Step 5

class DataImportService:
    @staticmethod
    def start_import(user, file_obj, import_type, source):
        # 1. Initialize the Run
        run = ImportRun.objects.create(
            import_type=import_type,
            source=source,
            file_name=file_obj.name,
            format='CSV' if file_obj.name.endswith('.csv') else 'EXCEL',
            started_by=user
        )
        
        if import_type == 'ATTENDANCE':
            # 1. Parse rows into a list of dicts
            rows = DataImportService._parse_file_to_list(file_obj)
            
            # 2. Call the service
            success, errors = AttendanceImportService.process_import_run(run, rows, user)

            # 4. Audit
            AuditLogger.log(
                actor=user,
                action_type="ATTENDANCE_IMPORT_SUCCESS",
                entity=run,
                metadata={
                    "rows_processed": len(rows),
                    "success": success,
                    "errors": errors
                }
            )

    @staticmethod
    def _process_row(import_type, row, user):
        """
        Internal logic to route row data to the correct app service.
        """
        if import_type == 'ATTENDANCE':
            # This is handled in process_import_run for attendance
            pass
        elif import_type == 'STUDENTS':
            from sundayschool.services import StudentRegistrationService
            StudentRegistrationService.register_from_import(row, user)