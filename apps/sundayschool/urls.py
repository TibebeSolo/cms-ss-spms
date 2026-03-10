from django.urls import path
from . import views

app_name = 'sundayschool'

urlpatterns = [
    # The flow: search christian -> click register -> this URL loads the form
    path('register/form/<int:christian_id>/', views.StudentRegisterView.as_view(), name='student-register'),
    
    # Students List view
    path('students/', views.StudentListView.as_view(), name='student-list'),
]