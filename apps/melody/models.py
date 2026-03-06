from django.db import models
from django.conf import settings
from apps.sundayschool.models import SSStudentProfile

class MezemranMembership(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('TERMINATED', 'Terminated'),
    ]

    # Requirement 16: Link to SS Profile
    ss_student_profile = models.ForeignKey(
        SSStudentProfile, 
        on_delete=models.CASCADE, 
        related_name='mezemran_memberships'
        )
    
    # Requirement 16: Mezemran ID
    # ID Format: {SSAbbrev}MZ{YY}{RRR}
    mezmur_entry_year_eth = models.IntegerField()
    mezemran_roll_number = models.IntegerField() # 3-digit zero-padded roll, resets yearly
    mezemran_id = models.CharField(max_length=30, unique=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    is_active = models.BooleanField(default=True)
    
    selected_at = models.DateTimeField()
    selected_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='selected_mezemran')
    selection_reason = models.TextField()
    criteria_used = models.TextField(blank=True)
    
    terminated_at = models.DateTimeField(null=True, blank=True)
    terminated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='terminated_mezemran')
    termination_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.ss_student_profile} - {self.mezemran_id}"

class MezemranChangeRequest(models.Model):
    ACTION_CHOICES = [
        ('SELECT', 'Select'),
        ('TERMINATE', 'Terminate'),
        ('RESELECT', 'Reselect'),
    ]
    STATES = [
        ('DRAFT', 'Draft'),
        ('PENDING_MELODY_EXEC', 'Pending Melody Exec'),
        ('PENDING_LEADER', 'Pending Leader'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    ss_student_profile = models.ForeignKey(SSStudentProfile, on_delete=models.CASCADE)
    target_membership = models.ForeignKey(MezemranMembership, on_delete=models.SET_NULL, null=True, blank=True)
    
    payload = models.JSONField(help_text="Stores reasons, notes, criteria for the change")
    
    drafted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='drafted_mz_changes')
    drafted_at = models.DateTimeField(auto_now_add=True)
    
    melody_exec_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='melody_exec_approved_mz')
    melody_exec_approved_at = models.DateTimeField(null=True, blank=True)
    melody_exec_comment = models.TextField(blank=True)
    
    leader_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leader_approved_mz')
    leader_approved_at = models.DateTimeField(null=True, blank=True)
    leader_comment = models.TextField(blank=True)
    
    state = models.CharField(max_length=20, choices=STATES, default='DRAFT')
