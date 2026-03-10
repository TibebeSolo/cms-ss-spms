from django.urls import path
from . import views

app_name = 'sundayschool'

urlpatterns = [
    # ... other paths ...
    path('register/', views.student_registration_view, name='student-register'),
    path('students/', views.student_list_view, name='student-list'), # Placeholder for list
]