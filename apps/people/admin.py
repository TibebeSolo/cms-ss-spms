from django.contrib import admin
from .models import Christian, ContactPerson, ConfessionFather, RelationshipType

# Register your models here.
admin.site.register(Christian)
admin.site.register(ContactPerson)
admin.site.register(ConfessionFather)
admin.site.register(RelationshipType)