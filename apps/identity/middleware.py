from django.shortcuts import redirect
from django.urls import reverse

class ForcePasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # Paths that are allowed even if password change is required
            allowed_paths = [
                reverse('password_change'),
                reverse('logout'),
                '/static/', # Allow CSS/JS to load
            ]
            
            if request.user.requires_password_change and request.path not in allowed_paths:
                return redirect('password_change')
        
        return self.get_response(request)