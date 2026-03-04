from django.db import models
from django.conf import settings

class AuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='audit_actions'
    )
    action_type = models.CharField(max_length=100) # e.g., CREATE, UPDATE, DELETE, APPROVE, EXPORT
    entity_type = models.CharField(max_length=100) # e.g., SSStudentProfile, AttendanceSession
    entity_id = models.CharField(max_length=100, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)
    metadata = models.JSONField(help_text="Stores before/after snapshots or additional context")

    def __str__(self):
        return f"{self.timestamp} - {self.actor} - {self.action_type} - {self.entity_type}"
