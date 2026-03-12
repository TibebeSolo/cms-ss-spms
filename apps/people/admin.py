from django.contrib import admin
from .models import Christian, ContactPerson, RelationshipType

# Register your models here.
admin.site.register(Christian)
admin.site.register(ContactPerson)
admin.site.register(RelationshipType)