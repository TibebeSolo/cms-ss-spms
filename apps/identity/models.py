from django.contrib.auth.models import AbstractUser
from django.db import models
from .models_auth import AuthEventLog

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
