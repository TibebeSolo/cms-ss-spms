from django.contrib import admin
from .models import MezemranMembership, MezemranChangeRequest

# Register your models here.
admin.site.register(MezemranMembership)
admin.site.register(MezemranChangeRequest)