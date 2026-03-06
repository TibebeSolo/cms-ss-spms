from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

# A simple inline view for the Dashboard to test the layout immediately
@login_required
def dashboard_view(request):
    from django.shortcuts import render
    return render(request, 'layouts/dashboard.html')

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication Routing
    path('login/', auth_views.LoginView.as_view(
        template_name='apps/identity/pages/login.html',
        redirect_authenticated_user=True
    ), name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(
        next_page='login'
    ), name='logout'),

    # Forced Password Reset / Change (Requirement from Context)
    path('password-change/', auth_views.PasswordChangeView.as_view(
        template_name='apps/identity/pages/password_change.html',
        success_url='/'
    ), name='password_change'),

    # Dashboard / Entry Point
    path('', dashboard_view, name='dashboard'),

    # Modular Apps (Uncomment these as you create the urls.py inside each app)
    # path('people/', include('apps.people.urls', namespace='people')),
    # path('ss/', include('apps.sundayschool.urls', namespace='ss')),
    # path('melody/', include('apps.melody.urls', namespace='melody')),
    # path('identity/', include('apps.identity.urls', namespace='identity')),
]