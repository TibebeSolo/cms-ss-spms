from django.db import models
from .services import EthiopianDateService, ChristianService

class RelationshipType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class ConfessionFather(models.Model):
    full_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    servant_church = models.CharField(max_length=255)
    residence = models.TextField()

    def __str__(self):
        return self.full_name

class Christian(models.Model):
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
    ]

    first_name = models.CharField(max_length=100)
    father_name = models.CharField(max_length=100)
    grandfather_name = models.CharField(max_length=100)
    baptismal_name = models.CharField(max_length=100, blank=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, null=True, blank=True)
    
    # Ethiopian Date (confirmed storage pattern)
    dob_eth_year = models.IntegerField(null=True, blank=True)
    dob_eth_month = models.IntegerField(null=True, blank=True)
    dob_eth_day = models.IntegerField(null=True, blank=True)
    dob_greg = models.DateField(null=True, blank=True)
    
    phone = models.CharField(max_length=20, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    
    # Address
    region = models.CharField(max_length=100, blank=True)
    town_city = models.CharField(max_length=100, blank=True)
    kebele = models.CharField(max_length=50, blank=True)
    home_number = models.CharField(max_length=50, blank=True)
    
    photo = models.ImageField(upload_to='people/photos/', null=True, blank=True)
    
    # Church ID tracking
    church_id = models.CharField(max_length=30, unique=True, null=True, blank=True)
    christian_roll_number = models.IntegerField(null=True, blank=True)
    record_entry_year_eth = models.IntegerField(null=True, blank=True)
    
    # Requirement 17: No physical deletion
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.father_name}"

    def save(self, *args, **kwargs):
        # 1. Handle Ethiopian Date Conversion
        if self.dob_eth_year and self.dob_eth_month and self.dob_eth_day:
            eth_date_str = f"{self.dob_eth_year:04d}-{self.dob_eth_month:02d}-{self.dob_eth_day:02d}"
            self.dob_greg = EthiopianDateService.ethiopian_to_gregorian(eth_date_str)
        
        # 2. Handle Custom ID Generation ({ChurchAbbrev}{YY}{RRRRR})
        if not self.church_id:
            # Generate the ID and roll number using the service
            c_id, roll, year_eth = ChristianService.generate_church_id(self)
            self.church_id = c_id
            self.christian_roll_number = roll
            self.record_entry_year_eth = year_eth
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.first_name} {self.father_name} ({self.church_id})"

class ContactPerson(models.Model):
    full_name = models.CharField(max_length=255)
    relationship_type = models.ForeignKey(RelationshipType, on_delete=models.PROTECT)
    phone = models.CharField(max_length=20)
    address = models.TextField()
    linked_christian = models.ForeignKey(
        Christian, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='contacts_of'
    )

    def __str__(self):
        return self.full_name
