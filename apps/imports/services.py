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
            from sundayschool.services import AttendanceImportBridge
            # 1. Parse rows into a list of dicts
            rows = DataImportService._parse_file_to_list(file_obj)
            
            # 2. Call the bridge
            AttendanceImportService.process_import_run(run, rows, context, user)

            # 4. Audit
            AuditLogger.log(
                actor=user,
                action_type="ATTENDANCE_IMPORT_SUCCESS",
                entity=run,
                metadata={
                    "rows_processed": len(rows),
                    "class_group_id": context.get('class_group_id'),
                    "date": context.get('eth_date')
                }
            )

        

    @staticmethod
    def _process_row(import_type, row):
        """
        Internal logic to route row data to the correct app service.
        """
        if import_type == 'ATTENDANCE':
            # This calls Step 7 (Attendance Service)
            from sundayschool.services import AttendanceService
            AttendanceService.record_from_import(row)
        elif import_type == 'STUDENTS':
            # This calls Step 2 (Registration Service)
            from sundayschool.services import SSDeploymentService
            SSDeploymentService.register_from_import(row)