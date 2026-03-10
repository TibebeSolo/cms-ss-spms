from django.core.management.base import BaseCommand
from identity.models import Permission
from identity.permissions_registry import AppPermissions

class Command(BaseCommand):
    help = 'Syncs permissions from registry to the database'

    def handle(self, *args, **options):
        choices = AppPermissions.as_choices()
        count = 0
        for code, description in choices:
            obj, created = Permission.objects.update_or_create(
                code=code,
                defaults={'description': description}
            )
            if created:
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully synced {count} new permissions.'))