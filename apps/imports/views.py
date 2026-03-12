from django.shortcuts import render
from django.http import HttpResponse
from .services import DataImportService # The service you already have

@login_required
def hx_upload_attendance_modal(request):
    """GET: Shows the upload file modal."""
    return render(request, 'apps/imports/fragments/modal_upload_attendance.html')

@login_required
@require_POST
def process_attendance_import(request):
    file_obj = request.FILES.get('attendance_file')
    
    # 1. Extract context from the form
    import_context = {
        'class_group_id': request.POST.get('class_group_id'),
        'eth_date': {
            'day': request.POST.get('import_day'),
            'month': request.POST.get('import_month'),
            'year': request.POST.get('import_year'),
        }
    }

    try:
        # 2. Start the import with context
        run = DataImportService.start_import(
            user=request.user,
            file_obj=file_obj,
            import_type='ATTENDANCE',
            source='Mobile_App_Export',
            context=import_context # Pass the selected Grade/Date
        )
        
        # 3. Return success and refresh dashboard
        return HttpResponse(headers={'HX-Refresh': 'true'})
    except Exception as e:
        return HttpResponse(f'<div class="alert alert-danger">{str(e)}</div>')