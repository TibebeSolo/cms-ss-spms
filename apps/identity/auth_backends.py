from django.contrib.auth.backends import ModelBackend
from .models import Permission

class SS_SPMS_Backend(ModelBackend):
    def has_perm(self, user_obj, perm, obj=None):
        if not user_obj.is_active:
            return False
        
        # Fetch all codes associated with user's roles
        user_perms = Permission.objects.filter(
            roles__user_roles__user=user_obj
        ).values_list('code', flat=True)

        # System Admin Check (Wildcard)
        if "identity:all" in user_perms:
            return True
            
        return perm in user_perms