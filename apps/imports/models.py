from django.db import models
from django.conf import settings

class ImportRun(models.Model):
    IMPORT_TYPES = [
        ('ATTENDANCE', 'Attendance'),
        ('STUDENTS', 'Students'),
    ]
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('COMPLETED_WITH_ERRORS', 'Completed with Errors'),
    ]

    import_type = models.CharField(max_length=50, choices=IMPORT_TYPES)
    source = models.CharField(max_length=100) # e.g., Firebase
    file_name = models.CharField(max_length=255)
    format = models.CharField(max_length=10) # CSV, Excel
    
    started_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='import_runs')
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='STARTED')
    summary_counts = models.JSONField(default=dict, help_text="e.g., {'total': 100, 'success': 90, 'errors': 10}")

    def __str__(self):
        return f"{self.import_type} - {self.started_at} - {self.status}"

class ImportRowError(models.Model):
    import_run = models.ForeignKey(ImportRun, on_delete=models.CASCADE, related_name='row_errors')
    row_number = models.IntegerField()
    error_code = models.CharField(max_length=50)
    message = models.TextField()
    raw_payload = models.TextField(help_text="The raw row data that failed")

    def __str__(self):
        return f"Row {self.row_number}: {self.error_code}"
