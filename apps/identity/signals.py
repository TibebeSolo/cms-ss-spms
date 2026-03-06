from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.people.models import Christian
from apps.sundayschool.models import SSStudentProfile
from .models import UserAccount
from apps.audit.services import AuditLogger

@receiver(post_save, sender=SSStudentProfile)
def create_student_user(sender, instance, created, **kwargs):
    """
    When an SS Profile is created, use the SSID as the username.
    """
    if created:
        UserAccount.objects.create_user(
            username=instance.ssid,
            password="TemporaryPassword123!", # Should be forced to change
            email=instance.christian.email or ""
        )
    
    AuditLogger.log(
        actor=instance.user,
        action_type="PARISH_SS_STUDENT_CREATED",
        entity=instance,
        metadata={
            "username": instance.username,
            "email": instance.email
        }
    )

@receiver(post_save, sender=Christian)
def create_parish_member_user(sender, instance, created, **kwargs):
    """
    For non-SS members, use the Church ID as the username.
    Only create if they don't have an SS profile coming.
    """
    if created and not hasattr(instance, 'ss_profile'):
        UserAccount.objects.create_user(
            username=instance.church_id,
            password="TemporaryPassword123!",
            email=instance.email or ""
        )

    AuditLogger.log(
        actor=instance.user,
        action_type="PARISH_CHRISTIAN_CREATED",
        entity=instance,
        metadata={
            "username": instance.username,
            "email": instance.email
        }
    )