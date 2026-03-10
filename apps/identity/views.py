from .utils.generate_default_password import generate_default_password
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.conf import settings
from django.contrib import messages
from .models import UserAccount, AuthEventLog
from datetime import timedelta
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse_lazy
from .models import Role

# Constants for lockout
LOCKOUT_THRESHOLD = 7
LOCKOUT_TIME_MINUTES = 30

# System Admin views
def is_system_admin(user):
    return user.has_perm('identity:all')

@login_required
@user_passes_test(is_system_admin)
def system_dashboard(request):
    context = {
        'total_officers': UserAccount.objects.filter(is_staff=True).count(),
        'roles_count': Role.objects.count(),
        'recent_logs': AuthEventLog.objects.order_by('-timestamp')[:5],
    }
    return render(request, 'apps/identity/pages/system_admin_dashboard.html', context)

@login_required
@user_passes_test(is_system_admin)
def role_list_partial(request):
    roles = Role.objects.all().prefetch_related('permissions')
    return render(request, 'apps/identity/fragments/role_list.html', {'roles': roles})

@login_required
@user_passes_test(is_system_admin)
def role_upsert(request, pk=None):
    """Handles both Create and Update for Roles"""
    role = get_object_or_404(Role, pk=pk) if pk else None
    
    if request.method == 'POST':
        form = RoleForm(request.POST, instance=role)
        if form.is_valid():
            form.save()
            # Return the updated table via HTMX
            roles = Role.objects.all()
            return render(request, 'apps/identity/fragments/role_list.html', {'roles': roles})
    else:
        form = RoleForm(instance=role)

    # Group permissions for the template (Optional but cleaner)
    all_perms = Permission.objects.all().order_by('code')
    return render(request, 'apps/identity/fragments/role_form.html', {
        'form': form,
        'role': role,
        'all_perms': all_perms
    })

# @login_required
# @user_passes_test(is_system_admin)
# def officer_create(request):
#     if request.method == 'POST':
#         form = OfficerRegistrationForm(request.POST) # Form needs SSID-related fields
#         if form.is_valid():
#             try:
#                 with transaction.atomic():
#                     # 1. Create Christian record (via People logic)
#                     christian = Christian.objects.create(
#                         first_name=form.cleaned_data['first_name'],
#                         father_name=form.cleaned_data['father_name'],
#                         grandfather_name=form.cleaned_data['grandfather_name'],
#                         sex=form.cleaned_data['sex'],
#                         email=form.cleaned_data['email'],
#                         phone=form.cleaned_data['phone'],
#                         address=form.cleaned_data['address'],
#                         date_of_birth=form.cleaned_data['date_of_birth']
#                     )

#                     # 2. Create SS Student Profile (via SundaySchool logic)
#                     # This will trigger SSID generation in the model's save() 
#                     # or you can call StudentService.register_new_student
#                     student = SSStudentProfile.objects.create(
#                         christian=christian,
#                         grade=form.cleaned_data['grade'],
#                         section=form.cleaned_data['section'],
#                         joined_year_eth=form.cleaned_data['joined_year_eth'],
#                         status=StudentStatus.objects.get(is_default=True)
#                     )

#                     # 3. Create UserAccount using SSID as Username
#                     temp_pwd = generate_default_password()
#                     user = UserAccount.objects.create_user(
#                         username=student.ssid, # <--- Requirement: Use SSID
#                         first_name=christian.first_name,
#                         last_name=christian.father_name,
#                         email=christian.email,
#                         password=temp_pwd,
#                         is_staff=True, # Makes them an Officer
#                         requires_password_change=True
#                     )
                    
#                     # 4. Link the System Role
#                     UserRole.objects.create(user=user, role=form.cleaned_data['role'])
                    
#                     return render(request, 'apps/identity/fragments/officer_success_modal.html', {
#                         'user': user,
#                         'temp_pwd': temp_pwd,
#                         'ssid': student.ssid,
#                         'church_id': christian.church_id,
#                         'role': form.cleaned_data['role']
#                     })
#             except Exception as e:
#                 # If anything fails, rollback the transaction
#                 transaction.rollback()
#                 messages.error(request, f"Registration Failed: {str(e)}")
#     else:
#         form = OfficerRegistrationForm()
    
#     return render(request, 'apps/identity/fragments/officer_form_modal.html', {'form': form})

# @login_required
# @user_passes_test(is_system_admin)
# def officer_list_partial(request):
#     # We fetch officers and their roles
#     # Note: We display the 'username' field because that's their SSID
#     officers = UserAccount.objects.filter(is_staff=True).prefetch_related('user_roles__role')
#     return render(request, 'apps/identity/fragments/officer_list_table.html', {'officers': officers})

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
