from django.db import models

class Parish(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    diocese_name = models.CharField(max_length=255)
    church_abbrev = models.CharField(max_length=10, help_text="Used for ID generation")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SundaySchool(models.Model):
    parish = models.OneToOneField(Parish, on_delete=models.CASCADE, related_name='sunday_school')
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=10, help_text="Used for SSID/MZID generation")
    phone = models.CharField(max_length=20)
   
    # Branding - State of the Art Technique: Store Hex/HSL
    primary_color = models.CharField(max_length=7, default="#162736", help_text="Hex code for primary brand")
    secondary_color = models.CharField(max_length=7, default="#FCEB9E", help_text="Hex code for secondary brand")
    
    # Multi-Logo Strategy
    primary_logo = models.ImageField(upload_to='org/logos/', null=True, blank=True, help_text="Full logo for headers")
    symbol_logo = models.ImageField(upload_to='org/logos/', null=True, blank=True, help_text="Small symbol for sidebar/favicon")
    
    is_active = models.BooleanField(default=True)
    
    # Social links as a simple JSON or separate model; implementation_plan 2.1 says SocialLink
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class SocialLink(models.Model):
    sunday_school = models.ForeignKey(SundaySchool, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=50) # e.g., Facebook, Telegram
    url = models.URLField()

    def __str__(self):
        return f"{self.platform}: {self.url}"
