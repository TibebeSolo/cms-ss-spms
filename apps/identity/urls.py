from .views import login_view, OnboardingPasswordChangeView
from django.urls import path

app_name = 'identity'

urlpatterns = [
    path('login/', login_view, name='login'),

    # This matches the 'password_change' name used in our middleware/settings
    path('set-password/', OnboardingPasswordChangeView.as_view(), name='password_change'),
]
