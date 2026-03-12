from django.urls import path
from . import views

app_name = 'sundayschool'

urlpatterns = [
    # ... other paths ...
    path('register/', views.student_registration_view, name='student-register'),
    path('students/', views.student_list_view, name='student-list'), # Placeholder for list
    
    # Attendance Dashboard and Main Sheet
    path('attendance/', views.attendance_dashboard, name='attendance-dashboard'),
    path('attendance/sheet/<int:session_id>/', views.attendance_sheet_view, name='attendance-sheet'),
    
    # HTMX Actions
    path('attendance/hx/new-session/', views.hx_new_session_modal, name='hx-new-session'),
    path('attendance/hx/create-session/', views.hx_create_session, name='hx-create-session'),
    path('attendance/hx/update-record/<int:record_id>/', views.hx_update_record, name='hx-update-record'),
    path('attendance/hx/update-note/<int:record_id>/', views.hx_update_record_note, name='hx-update-record-note'),
    path('attendance/hx/submit/<int:session_id>/', views.hx_submit_attendance, name='hx-submit-attendance'),
    path('attendance/hx/approve/<int:session_id>/', views.hx_approve_attendance, name='hx-approve-attendance'),
]