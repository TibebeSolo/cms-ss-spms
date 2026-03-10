from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from .models import UserAccount, AuthEventLog
from datetime import timedelta
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy

LOCKOUT_THRESHOLD = 7
LOCKOUT_TIME_MINUTES = 30

class OnboardingPasswordChangeView(PasswordChangeView):
    template_name = 'apps/identity/pages/password_change.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        # The moment they successfully change the password, they are "onboarded"
        user = self.request.user
        user.requires_password_change = False
        user.save()
        messages.success(self.request, "Password updated successfully. Welcome to SS-SPMS!")
        return super().form_valid(form)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = UserAccount.objects.filter(username=username).first()
        ip = request.META.get('REMOTE_ADDR')
        ua = request.META.get('HTTP_USER_AGENT', '')
        now = timezone.now()
        if user and user.locked_until and user.locked_until > now:
            AuthEventLog.objects.create(
                user=user,
                username_attempted=username,
                event_type=AuthEventLog.LOCKOUT,
                ip_address=ip,
                user_agent=ua,
            )
            messages.error(request, f"Account locked until {user.locked_until}.")
            return render(request, 'login.html')
        user_auth = authenticate(request, username=username, password=password)
        if user_auth is not None:
            auth_login(request, user_auth)
            user.failed_login_count = 0
            user.locked_until = None
            user.save(update_fields=['failed_login_count', 'locked_until'])
            AuthEventLog.objects.create(
                user=user,
                username_attempted=username,
                event_type=AuthEventLog.LOGIN_SUCCESS,
                ip_address=ip,
                user_agent=ua,
            )
            return redirect('dashboard')
        else:
            if user:
                user.failed_login_count += 1
                if user.failed_login_count >= LOCKOUT_THRESHOLD:
                    user.locked_until = now + timedelta(minutes=LOCKOUT_TIME_MINUTES)
                    AuthEventLog.objects.create(
                        user=user,
                        username_attempted=username,
                        event_type=AuthEventLog.LOCKOUT,
                        ip_address=ip,
                        user_agent=ua,
                    )
                else:
                    AuthEventLog.objects.create(
                        user=user,
                        username_attempted=username,
                        event_type=AuthEventLog.LOGIN_FAILURE,
                        ip_address=ip,
                        user_agent=ua,
                    )
                user.save(update_fields=['failed_login_count', 'locked_until'])
            else:
                AuthEventLog.objects.create(
                    user=None,
                    username_attempted=username,
                    event_type=AuthEventLog.LOGIN_FAILURE,
                    ip_address=ip,
                    user_agent=ua,
                )
            messages.error(request, "Invalid credentials.")
    return render(request, 'apps/identity/pages/login.html')
