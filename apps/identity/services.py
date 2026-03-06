from django.utils import timezone
from datetime import timedelta

class AuthService:
    LOCKOUT_THRESHOLD = 7
    LOCKOUT_DURATION_MINUTES = 30

    @staticmethod
    def handle_login_failure(user):
        user.failed_login_count += 1

        AuditLogger.log(
            actor=user,
            action_type="LOGIN_FAILURE",
            entity=user,
            metadata={
                "username": user.username,
                "ip_address": user.ip_address,
                "failed_login_count": user.failed_login_count,
            }
        )

        if user.failed_login_count >= AuthService.LOCKOUT_THRESHOLD:
            user.locked_until = timezone.now() + timedelta(minutes=AuthService.LOCKOUT_DURATION_MINUTES)

            AuditLogger.log(
                actor=user,
                action_type="ACCOUNT_LOCKED",
                entity=user,
                metadata={
                    "username": user.username,
                    "ip_address": user.ip_address,
                    "failed_login_count": user.failed_login_count,
                    "locked_until": user.locked_until
                }
            )

        user.save()

    @staticmethod
    def handle_login_success(user):
        user.failed_login_count = 0
        user.locked_until = None
        user.save()