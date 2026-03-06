import csv
import io
from django.utils import timezone
from django.db import transaction
from .models import ImportRun, ImportRowError
from apps.audit.services import AuditLogger # From Step 5

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
        
        counts = {'total': 0, 'success': 0, 'errors': 0}
        
        try:
            # 2. Process Rows (Example for CSV)
            decoded_file = file_obj.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(decoded_file))
            
            for row_idx, row in enumerate(reader, start=1):
                counts['total'] += 1
                try:
                    with transaction.atomic():
                        DataImportService._process_row(import_type, row)
                        counts['success'] += 1
                except Exception as e:
                    counts['errors'] += 1
                    ImportRowError.objects.create(
                        import_run=run,
                        row_number=row_idx,
                        error_code="PROCESSING_ERROR",
                        message=str(e),
                        raw_payload=str(row)
                    )

            # 3. Finalize
            run.status = 'COMPLETED' if counts['errors'] == 0 else 'COMPLETED_WITH_ERRORS'
            run.summary_counts = counts
            run.finished_at = timezone.now()
            run.save()

            # 4. Audit
            AuditLogger.log(user, f"IMPORT_{import_type}", run, metadata=counts)

        except Exception as fatal_error:
            run.status = 'FAILED'
            run.summary_counts = counts
            run.save()
            raise fatal_error

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