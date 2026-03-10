from django.contrib import admin
from .models import ImportRun, ImportRowError, ImportLog

# Register your models here.
admin.site.register(ImportRun)
admin.site.register(ImportRowError)
admin.site.register(ImportLog)
