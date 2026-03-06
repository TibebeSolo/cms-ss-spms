from django.db import models
from django.conf import settings

class GeneratedReport(models.Model):
    REPORT_TYPES = [
        ('ATTENDANCE_MONTHLY', 'Monthly Attendance'),
        ('STUDENT_PROFILE', 'Student Profile Summary'),
        ('MEZEMRAN_ROSTER', 'Mezemran Roster'),
    ]
    
    report_type = models.CharField(max_length=50, choices=REPORT_TYPES)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    generated_at = models.DateTimeField(auto_now_add=True)
    
    # Store parameters used (e.g., {'month': 5, 'year': 2016, 'grade': 1})
    parameters = models.JSONField(default=dict)
    
    # Path to the file if we decide to cache it, otherwise leave blank for on-the-fly
    file_path = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.report_type} by {self.generated_by} at {self.generated_at}"