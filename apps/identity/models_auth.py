from django.db import models
from django.conf import settings

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

    def __str__(self):
        return f"{self.timestamp} - {self.username_attempted} - {self.event_type}"
