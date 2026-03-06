from django.utils import timezone
from datetime import timedelta
import string
import secrets
from .models import UserAccount, Role, UserRole

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

# Service for provisioning new users
class UserProvisioningService:
    @staticmethod
    def create_officer_account(username, email, role_name):
        """
        Creates a user with a secure random temporary password.
        """
        # Generate random 10-character password
        alphabet = string.ascii_letters + string.digits
        temp_password = ''.join(secrets.choice(alphabet) for i in range(10))
        
        user = UserAccount.objects.create_user(
            username=username,
            email=email,
            password=temp_password,
            requires_password_change=True # Ensures the workflow triggers
        )
        
        # Assign Role
        role = Role.objects.get(name=role_name)
        UserRole.objects.create(user=user, role=role)
        
        # In a real scenario, you'd send this temp_password via Email/SMS
        # For now, we return it so the SysAdmin can copy it manually
        return user, temp_password