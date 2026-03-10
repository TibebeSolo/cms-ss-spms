from django.shortcuts import redirect
from django.urls import reverse, NoReverseMatch

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # 1. EXCLUDE ADMINS: If user is superuser or staff, don't force them
            if request.user.is_superuser or request.user.is_staff:
                return self.get_response(request)

            # 2. DEFINING ALLOWED PATHS
            # We use a try/except block just in case 'logout' isn't defined yet
            allowed_paths = [reverse('identity:password_change')]
            try:
                allowed_paths.append(reverse('logout'))
            except NoReverseMatch:
                pass

            # 3. REDIRECT LOGIC
            # Only redirect if they actually need a change and aren't already on an allowed path
            if getattr(request.user, 'requires_password_change', False):
                # Don't redirect if it's a static file or an allowed path
                if not any(request.path.startswith(path) for path in allowed_paths) and not request.path.startswith('/static/'):
                    return redirect('identity:password_change')
        
        return self.get_response(request)