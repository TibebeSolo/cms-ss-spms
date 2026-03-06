from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class UserAccount(AbstractUser):
    """
    Custom user model for SS-SPMS.
    SSID is used as username for students.
    ChurchID is used as username for non-SS Christians.
    """
    failed_login_count = models.PositiveIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Requirement 17: No physical deletion
    is_active = models.BooleanField(default=True)

    # Requirement: Forced onboarding workflow
    requires_password_change = models.BooleanField(default=True)

    def is_locked(self):
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False

    class Meta:
        app_label = "identity"

    def __str__(self):
        return self.username

class Role(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    
    permissions = models.ManyToManyField('Permission', related_name='roles')

    def __str__(self):
        return self.name

class Permission(models.Model):
    code = models.CharField(max_length=100, unique=True)
    description = models.TextField()

    def __str__(self):
        return f"{self.code}: {self.description}"

class UserRole(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')

    class Meta:
        unique_together = ('user', 'role')

class AuthEventLog(models.Model):
    LOGIN_SUCCESS = 'SUCCESS'
    LOGIN_FAILURE = 'FAILURE'
    LOCKOUT = 'LOCKOUT'
    EVENT_TYPES = [
        (LOGIN_SUCCESS, 'Login Success'),
        (LOGIN_FAILURE, 'Login Failure'),
        (LOCKOUT, 'Account Lockout'),
    ]
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    username_attempted = models.CharField(max_length=150)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "identity"

    def __str__(self):
        return f"{self.timestamp} - {self.username_attempted} - {self.event_type}"
