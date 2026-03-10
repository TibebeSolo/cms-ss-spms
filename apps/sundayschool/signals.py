from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SSStudentProfile
from identity.models import UserAccount

# @receiver(post_save, sender=SSStudentProfile)
# def create_student_user(sender, instance, created, **kwargs):
#     if created:
#         # Per requirement: Use SSID as username for students
#         UserAccount.objects.create_user(
#             username=instance.ssid,
#             password="TemporaryPassword123!", # Should be changed on first login
#             is_active=True
#         )