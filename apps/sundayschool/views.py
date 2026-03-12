from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import StudentOfficerRegistrationForm
from .services import StudentRegistrationService
from .services import AttendanceWorkflowService, AttendanceRecord


@login_required
def student_registration_view(request):
    base_template = 'layouts/partial.html' if request.headers.get('HX-Request') else 'layouts/dashboard.html'
    
    # Initialize form with the current user to check permissions in __init__
    if request.method == 'POST':
        form = StudentOfficerRegistrationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            # Extract data for the service
            christian_data = {
                'first_name': form.cleaned_data['first_name'],
                'father_name': form.cleaned_data['father_name'],
                'grandfather_name': form.cleaned_data['grandfather_name'],
                'baptismal_name': form.cleaned_data['baptismal_name'],
                'sex': form.cleaned_data['sex'],
                'email': form.cleaned_data['email'],
                'phone': form.cleaned_data['phone'],
                # Address
                'region': form.cleaned_data['region'],
                'town_city': form.cleaned_data['town_city'],
                'kebele': form.cleaned_data['kebele'],
                'home_number': form.cleaned_data['home_number'],
                'photo': form.cleaned_data.get('photo'),
                # Map date picker fields to Christian model
                'dob_eth_day': request.POST.get('dob_day'), # Fixed: missing prefix in eth_day name
                'dob_eth_month': request.POST.get('dob_month'),
                'dob_eth_year': request.POST.get('dob_year'),
            }
            
            ss_data = {
                'grade': form.cleaned_data['grade'],
                'section': form.cleaned_data['section'],
                'confession_father_name': form.cleaned_data['confession_father_name'],
                'joined_year_eth': form.cleaned_data['joined_year_eth'],
                'contact_person': {
                    'full_name': form.cleaned_data.get('contact_full_name'),
                    'relationship': form.cleaned_data.get('contact_relationship'),
                    'phone': form.cleaned_data.get('contact_phone'),
                    'address': form.cleaned_data.get('contact_address'),
                }
            }
            
            # The role is only present if the user is a System Admin
            role = form.cleaned_data.get('role')

            # Call the unified service
            student, temp_pwd = StudentRegistrationService.register_new_student(
                christian_data=christian_data,
                ss_data=ss_data,
                role=role,
                actor_user=request.user
            )

            if role and temp_pwd:
                # If an officer was created, show the success modal with credentials
                return render(request, 'apps/identity/fragments/officer_success_modal.html', {
                    'ssid': student.ssid,
                    'temp_pwd': temp_pwd,
                    'church_id': student.christian.church_id
                })
            else:
                messages.success(request, f"Student {student.ssid} registered successfully!")
                return redirect('sundayschool:student-list')
    else:
        # Default joined year to current Ethiopian year
        from people.services import EthiopianDateService
        initial_year = EthiopianDateService.get_current_eth_year()
        form = StudentOfficerRegistrationForm(user=request.user, initial={'joined_year_eth': initial_year})

    return render(request, 'apps/sundayschool/pages/registration.html', {
        'form': form,
        'base_template': base_template
    })

# Student List View
@login_required
def student_list_view(request):
    students = Student.objects.all()
    return render(request, 'apps/sundayschool/fragments/student_row.html', {'students': students})

# Attendance Views
@login_required
def attendance_dashboard(request):
    # Fetch recent sessions ordered by date
    sessions = AttendanceSession.objects.select_related('class_group__grade', 'class_group__section').all().order_by('-created_at')[:20]
    return render(request, 'apps/sundayschool/pages/attendance_dashboard.html', {
        'sessions': sessions
    })

@login_required
def attendance_sheet_view(request, session_id):
    """The main page for a specific attendance session."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    records = session.records.select_related('ss_student_profile__christian').all()
    
    # Check if user is an HR Executive for the approval button
    is_executive = request.user.groups.filter(name='HR Executive').exists() or request.user.is_superuser

    return render(request, 'apps/sundayschool/pages/attendance_sheet.html', {
        'session': session,
        'records': records,
        'status_choices': AttendanceRecord.STATUS_CHOICES,
        'per_executive_role': is_executive
    })

@login_required
def hx_new_session_modal(request):
    """Returns the content for the 'Create Session' Modal."""
    class_groups = ClassGroup.objects.filter(is_active=True).select_related('grade', 'section')
    from people.services import EthiopianDateService
    
    context = {
        'class_groups': class_groups,
        'current_eth': {
            'day': 1, # You can implement a helper to get today's exact Eth day
            'month': 1,
            'year': EthiopianDateService.get_current_eth_year()
        }
    }
    return render(request, 'apps/sundayschool/fragments/modal_new_session.html', context)

@login_required
@require_POST
def hx_create_session(request):
    """Processes the modal form to start a new attendance sheet."""
    class_group_id = request.POST.get('class_group')
    
    # Extract Ethiopian date from your global picker names
    eth_date = {
        'day': int(request.POST.get('session_day')),
        'month': int(request.POST.get('session_month')),
        'year': int(request.POST.get('session_year')),
    }
    
    try:
        session = AttendanceWorkflowService.initialize_session(
            class_group_id=class_group_id,
            eth_date_dict=eth_date,
            creator_user=request.user
        )
        # Tell HTMX to redirect the browser to the new sheet
        return HttpResponse(headers={'HX-Redirect': f'/sundayschool/attendance/sheet/{session.id}/'})
    except Exception as e:
        return HttpResponse(f'<div class="alert alert-danger">Error: {str(e)}</div>')

@login_required
@require_POST
def hx_update_record(request, record_id):
    """HTMX: Updates a single student's status (Present/Absent/etc)."""
    record = get_object_or_404(AttendanceRecord, id=record_id)
    new_status = request.POST.get('status')
    
    try:
        updated_record = AttendanceWorkflowService.update_single_record(
            record_id=record_id, 
            new_status=new_status, 
            actor_user=request.user
        )
        # Return ONLY the row content to refresh the UI colors
        return render(request, 'apps/sundayschool/fragments/attendance_row.html', {
            'record': updated_record,
            'session': updated_record.attendance_session,
            'status_choices': AttendanceRecord.STATUS_CHOICES,
            'just_saved': True # Triggers the green checkmark
        })
    except PermissionError:
        return HttpResponseForbidden("This session is locked.")

@login_required
@require_POST
def hx_update_record_note(request, record_id):
    """HTMX: Auto-saves student notes as the officer types."""
    record = get_object_or_404(AttendanceRecord, id=record_id)
    if record.attendance_session.status != 'DRAFT':
        return HttpResponseForbidden()
        
    record.note = request.POST.get('note', '')
    record.save()
    return HttpResponse(status=204) # 204 No Content (tells HTMX it saved successfully)

@login_required
@require_POST
def hx_submit_attendance(request, session_id):
    """HTMX: Submit the entire attendance sheet for approval."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    if session.status != 'DRAFT':
        return HttpResponseForbidden()
    
    # Service logic to change status to PENDING_APPROVAL
    AttendanceWorkflowService.submit_for_approval(
        session,
        request.user
    )

    return HttpResponse(status=204, headers={
        'HX-Refresh': 'true'
    }) # 204 No Content (tells HTMX it saved successfully)

@login_required
def hx_approve_modal(request, session_id):
    """GET: Shows the approval comment modal to the HR Executive."""
    if not request.user.groups.filter(name='HR Executive').exists() and not request.user.is_superuser:
        return HttpResponseForbidden("Only HR Executives can approve sessions.")
    
    session = get_object_or_404(AttendanceSession, id=session_id)
    return render(request, 'apps/sundayschool/fragments/modal_approve_session.html', {'session': session})

@login_required
@require_POST
def hx_approve_attendance(request, session_id):
    """POST: Finalizes the session and locks it forever."""
    session = get_object_or_404(AttendanceSession, id=session_id)
    comment = request.POST.get('comment', 'Approved via system dashboard.')
    
    # Call your existing service
    AttendanceWorkflowService.final_approve(session, request.user, comment)
    
    return HttpResponse(headers={'HX-Refresh': 'true'})