from django.db import models
from django.conf import settings
from people.models import Christian, ContactPerson
from people.services import EthiopianDateService

# 1. Academic Structure
class StudentStatus(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Grade(models.Model):
    name = models.CharField(max_length=100)
    order_no = models.IntegerField()
    is_custom = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=100)
    is_custom = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ClassGroup(models.Model):
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    meeting_day_of_week = models.IntegerField(
        help_text="0=Monday, 6=Sunday",
        null=True, blank=True
    )
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ('grade', 'section')

    def __str__(self):
        return f"{self.grade} - {self.section}"

# 2. Student Profile
class SSStudentProfile(models.Model):
    REGISTRATION_STATES = [
        ('DRAFT', 'Draft'),
        ('PENDING_HR', 'Pending HR Approval'),
        ('PENDING_LEADER', 'Pending Leader Approval'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Rejected'),
    ]

    christian = models.OneToOneField(
        Christian, 
        on_delete=models.PROTECT, 
        related_name='ss_profile'
        )
        
    # Custom IDs per Requirement
    # Format: {SSAbbrev}{YY}{RRR} (3-digit roll)
    ssid = models.CharField(
        max_length=20, 
        unique=True, 
        editable=False,
        db_index=True
        )
    ss_roll_number = models.PositiveIntegerField(unique=True)
    
    # Ethiopian Year of Joining (entered via UI)
    joined_year_eth = models.IntegerField()

    grade = models.ForeignKey(Grade, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    
    student_status = models.ForeignKey(StudentStatus, on_delete=models.PROTECT)
    registration_state = models.CharField(max_length=20, choices=REGISTRATION_STATES, default='DRAFT')
    profile_update_state = models.CharField(max_length=20, blank=True)
    
    confession_father = models.ForeignKey(
    Christian,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="confessed_students"
)

    # Requirement 17: No physical deletion
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.ssid:
            ssid, roll = StudentService.generate_ssid(
                joined_year=self.joined_year_eth
            )
            self.ssid = ssid
            self.ss_roll_number = roll
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.christian} ({self.ssid})"

class StudentContactLink(models.Model):
    ss_student_profile = models.ForeignKey(SSStudentProfile, on_delete=models.CASCADE, related_name='contact_links')
    contact_person = models.ForeignKey(ContactPerson, on_delete=models.CASCADE)
    is_primary = models.BooleanField(default=False)

    class Meta:
        unique_together = ('ss_student_profile', 'contact_person')

# 3. Workflows
class StudentRegistrationRequest(models.Model):
    ss_student_profile = models.ForeignKey(SSStudentProfile, on_delete=models.CASCADE)
    drafted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='drafted_registrations')
    drafted_at = models.DateTimeField(auto_now_add=True)
    
    hr_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_approved_registrations')
    hr_approved_at = models.DateTimeField(null=True, blank=True)
    hr_comment = models.TextField(blank=True)
    
    leader_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leader_approved_registrations')
    leader_approved_at = models.DateTimeField(null=True, blank=True)
    leader_comment = models.TextField(blank=True)
    
    state = models.CharField(max_length=20, choices=SSStudentProfile.REGISTRATION_STATES, default='DRAFT')

class StudentProfileUpdateRequest(models.Model):
    ss_student_profile = models.ForeignKey(SSStudentProfile, on_delete=models.CASCADE)
    changes_payload = models.JSONField()
    
    drafted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='drafted_profile_updates')
    drafted_at = models.DateTimeField(auto_now_add=True)
    
    hr_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_approved_profile_updates')
    hr_approved_at = models.DateTimeField(null=True, blank=True)
    hr_comment = models.TextField(blank=True)
    
    state = models.CharField(max_length=20, choices=[('PENDING_HR', 'Pending HR'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING_HR')

class GradeSectionChangeRequest(models.Model):
    ss_student_profile = models.ForeignKey(SSStudentProfile, on_delete=models.CASCADE)
    from_grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name='transfers_from')
    from_section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='transfers_from')
    to_grade = models.ForeignKey(Grade, on_delete=models.PROTECT, related_name='transfers_to')
    to_section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='transfers_to')
    
    reason = models.TextField()
    
    drafted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='drafted_gs_changes')
    drafted_at = models.DateTimeField(auto_now_add=True)
    
    hr_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='hr_approved_gs_changes')
    hr_approved_at = models.DateTimeField(null=True, blank=True)
    hr_comment = models.TextField(blank=True)
    
    leader_approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='leader_approved_gs_changes')
    leader_approved_at = models.DateTimeField(null=True, blank=True)
    leader_comment = models.TextField(blank=True)
    
    state = models.CharField(max_length=20, default='DRAFT')

# 4. Attendance
class AttendanceSession(models.Model):
    SCOPE_CHOICES = [
        ('CLASSGROUP', 'Class Group'),
        ('WHOLE_SS', 'Whole Sunday School'),
        ('SPECIAL_EVENT', 'Special Event'),
    ]
    EVENT_TYPES = [
        ('REGULAR', 'Regular'),
        ('SPECIAL', 'Special'),
    ]
    STATES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('PENDING_APPROVAL', 'Pending Approval'),
        ('APPROVED', 'Approved'),
    ]

    session_date_eth_year = models.IntegerField()
    session_date_eth_month = models.IntegerField()
    session_date_eth_day = models.IntegerField()
    session_date_greg = models.DateField()
    
    scope_type = models.CharField(max_length=20, choices=SCOPE_CHOICES)
    class_group = models.ForeignKey(ClassGroup, on_delete=models.SET_NULL, null=True, blank=True)
    
    title = models.CharField(max_length=255, blank=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES, default='REGULAR')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_attendance_sessions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    state = models.CharField(max_length=20, choices=STATES, default='DRAFT')

    def __str__(self):
        return f"{self.session_date_greg} - {self.scope_type}"

    def save(self, *args, **kwargs):
        if self.session_date_eth_year and self.session_date_eth_month and self.session_date_eth_day:
            eth_date_str = f"{self.session_date_eth_year:04d}-{self.session_date_eth_month:02d}-{self.session_date_eth_day:02d}"
            if EthiopianDateService.validate_ethiopian_date_str(eth_date_str):
                self.session_date_greg = EthiopianDateService.ethiopian_to_gregorian(eth_date_str)
        super().save(*args, **kwargs)

class AttendanceRecord(models.Model):
    STATUS_CHOICES = [
        ('PRESENT', 'Present'),
        ('ABSENT', 'Absent'),
        ('LATE', 'Late'),
        ('EXCUSED', 'Excused'),
    ]

    attendance_session = models.ForeignKey(AttendanceSession, on_delete=models.CASCADE, related_name='records')
    ss_student_profile = models.ForeignKey(SSStudentProfile, on_delete=models.CASCADE)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    note = models.TextField(blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='created_attendance_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('attendance_session', 'ss_student_profile')

class AttendanceApproval(models.Model):
    attendance_session = models.OneToOneField(AttendanceSession, on_delete=models.CASCADE, related_name='approval')
    
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='submitted_attendances')
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_attendances')
    approved_at = models.DateTimeField(null=True, blank=True)
    comment = models.TextField()

class AttendanceEditLog(models.Model):
    attendance_record = models.ForeignKey(AttendanceRecord, on_delete=models.CASCADE, related_name='edit_logs')
    edited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='attendance_edits')
    edited_at = models.DateTimeField(auto_now_add=True)
    
    reason_note = models.TextField()
    before_status = models.CharField(max_length=20)
    after_status = models.CharField(max_length=20)
