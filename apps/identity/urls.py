from .views import login_view, OnboardingPasswordChangeView
from django.urls import path
from . import views

app_name = 'identity'

urlpatterns = [
    path('login/', login_view, name='login'),

    # This matches the 'password_change' name used in our middleware/settings
    path('set-password/', OnboardingPasswordChangeView.as_view(), name='password_change'),

    # Dashboard
    path('admin-dashboard/', views.system_dashboard, name='sys_admin_dashboard'),

    # Role Management
    path('roles/table/', views.role_list_partial, name='role_list_partial'),
    path('roles/create/', views.role_upsert, name='role_create'),
    path('roles/update/<int:pk>/', views.role_upsert, name='role_update'),

    # Officer Management
    # path('officers/create/', views.officer_create, name='officer_create'),
    # path('officers/table/', views.officer_list_partial, name='officer_list')

]
