from django.core.management.base import BaseCommand
from identity.models import Role, Permission
from org.models import Parish, SundaySchool
from people.models import RelationshipType
from sundayschool.models import Grade, Section, StudentStatus

class Command(BaseCommand):
    help = 'Seeds initial data for SS-SPMS MVP v1'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding data...')

        # 1. Permissions
        permissions = [
            ('manage_users', 'Manage system users'),
            ('manage_roles', 'Manage roles and permissions'),
            ('create_student', 'Register new students'),
            ('approve_student', 'Approve student registrations'),
            ('view_students', 'View student profiles'),
            ('record_attendance', 'Record student attendance'),
            ('approve_attendance', 'Approve attendance sessions'),
            ('manage_mezemran', 'Manage Melody department membership'),
            ('generate_reports', 'Generate and export reports'),
        ]
        for code, desc in permissions:
            Permission.objects.get_or_create(code=code, defaults={'description': desc})

        # 2. Roles
        roles = [
            ('System Admin', True),
            ('Sunday School HR Executive', False),
            ('Sunday School HR Expert', False),
            ('Melody Department Executive', False),
            ('Melody Department Officer', False),
            ('Sunday School Executives Leader', False),
        ]
        for name, is_system in roles:
            Role.objects.get_or_create(name=name, defaults={'is_system_role': is_system})

        # 3. Relationship Types
        rels = ['Father', 'Mother', 'Guardian', 'Sibling', 'Spouse', 'Other']
        for rel in rels:
            RelationshipType.objects.get_or_create(name=rel)

        # 4. Student Statuses
        statuses = [
            ('Active', True),
            ('Transferred', False),
            ('Not Complete', False),
            ('Undetermined', False),
            ('Elders', False),
        ]
        for name, is_def in statuses:
            StudentStatus.objects.get_or_create(name=name, defaults={'is_default': is_def})

        # 5. Grades
        grades = ['KG'] + [str(i) for i in range(1, 13)]
        for i, name in enumerate(grades):
            Grade.objects.get_or_create(name=name, defaults={'order_no': i})

        # 6. Default Sections
        for name in ['A', 'B', 'C']:
            Section.objects.get_or_create(name=name)

        self.stdout.write(self.style.SUCCESS('Successfully seeded initial data'))
