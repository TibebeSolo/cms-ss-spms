from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import StudentOfficerRegistrationForm
from .services import StudentRegistrationService

@login_required
def student_registration_view(request):
    # Initialize form with the current user to check permissions in __init__
    if request.method == 'POST':
        form = StudentOfficerRegistrationForm(request.POST, user=request.user)
        if form.is_valid():
            # Extract data for the service
            christian_data = {
                'first_name': form.cleaned_data['first_name'],
                'father_name': form.cleaned_data['father_name'],
                'grandfather_name': form.cleaned_data['grandfather_name'],
                'sex': form.cleaned_data['sex'],
                'email': form.cleaned_data['email'],
                # Map date picker fields to Christian model
                'dob_eth_day': request.POST.get('dob_eth_day'),
                'dob_eth_month': request.POST.get('dob_eth_month'),
                'dob_eth_year': request.POST.get('dob_eth_year'),
            }
            
            ss_data = {
                'grade': form.cleaned_data['grade'],
                'section': form.cleaned_data['section'],
                'joined_year_eth': form.cleaned_data['joined_year_eth'],
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

    return render(request, 'apps/sundayschool/pages/registration.html', {'form': form})

# Student List View
@login_required
def student_list_view(request):
    students = Student.objects.all()
    return render(request, 'apps/sundayschool/fragments/student_row.html', {'students': students})