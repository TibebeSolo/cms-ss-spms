from django.shortcuts import render, get_object_or_404
from django.views.generic import View
from people.models import Christian
from .models import Grade, Section
from .services import StudentRegistrationService

class StudentRegisterView(View):
    def get(self, request, christian_id):
        christian = get_object_or_404(Christian, id=christian_id)
        context = {
            'christian': christian,
            'grades': Grade.objects.all().order_by('order_no'),
            'sections': Section.objects.all(),
        }
        return render(request, 'apps/sundayschool/fragments/register_form.html', context)

    def post(self, request, christian_id):
        # Extract data from request
        data = {
            'grade_id': request.POST.get('grade'),
            'section_id': request.POST.get('section'),
            'joined_year_eth': request.POST.get('eth_year'), # From our DatePicker
        }
        
        # Service call to handle logic
        student = StudentRegistrationService.register_new_student(
            christian_id, data, request.user
        )
        
        # Return success state (HTMX partial)
        return render(request, 'apps/sundayschool/fragments/registration_success.html', {'student': student})

class StudentListView(View):
    def get(self, request):
        students = SSStudentProfile.objects.all()
        context = {
            'students': students,
        }
        return render(request, 'apps/sundayschool/fragments/student_list.html', context)
