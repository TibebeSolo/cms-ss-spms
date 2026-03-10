from django.db.models.signals import post_save
from django.dispatch import receiver
from people.models import Christian
from sundayschool.models import SSStudentProfile
from .models import UserAccount
from audit.services import AuditLogger
from .utils.generate_default_password import generate_default_password

@receiver(post_save, sender=SSStudentProfile)
def create_student_user(sender, instance, created, **kwargs):
    """
    When an SS Profile is created, use the SSID as the username.
    This is a general students, not system officers.
    """
    if created:
        # Check if the user already exists (e.g., created as a Christian first)
        user, user_created = UserAccount.objects.get_or_create(
            username=instance.ssid,
            defaults={
                'email': instance.christian.email or "",
                'require_password_change': True,
                'is_staff': False, # Students are not staff by default
            }
        )

        if user_created:
            user.set_password(generate_default_password())
            user.save()
        
    
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
    # Only create if they don't have an SS profile and No user exists
    if created and not hasattr(instance, 'ss_profile'):
        if not UserAccount.objects.filter(username=instance.church_id).exists():
           user = UserAccount.objects.create_user(
                username=instance.church_id,
                password=generate_default_password(),
                email=instance.email or "",
                require_password_change=True,
                is_staff=False,
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