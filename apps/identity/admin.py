from django.contrib import admin
from .models import UserAccount, Role, Permission, UserRole, AuthEventLog

# Register your models here.
admin.site.register(UserAccount)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(UserRole)
admin.site.register(AuthEventLog)
