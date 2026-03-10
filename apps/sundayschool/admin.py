from django.contrib import admin
from .models import (StudentStatus, Grade, 
                Section, ClassGroup, 
                SSStudentProfile, StudentContactLink, 
                StudentRegistrationRequest, 
                StudentProfileUpdateRequest, 
                GradeSectionChangeRequest,
                AttendanceSession,
                AttendanceRecord,
                AttendanceApproval,
                AttendanceEditLog,
 )

# Register your models here.
admin.site.register(StudentStatus)
admin.site.register(Grade)
admin.site.register(Section)
admin.site.register(ClassGroup)
admin.site.register(SSStudentProfile)
admin.site.register(StudentContactLink)
admin.site.register(StudentRegistrationRequest)
admin.site.register(StudentProfileUpdateRequest)
admin.site.register(GradeSectionChangeRequest)
admin.site.register(AttendanceSession)
admin.site.register(AttendanceRecord)
admin.site.register(AttendanceApproval)
admin.site.register(AttendanceEditLog)