from django.contrib import admin
from .models import ImportRun, ImportRowError

# Register your models here.
admin.site.register(ImportRun)
admin.site.register(ImportRowError)
