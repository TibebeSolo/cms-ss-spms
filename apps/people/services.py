import datetime
from django.db import transaction
from django.conf import settings
from audit.services import AuditLogger
from ethioqen.calendar_conversion import (
    convert_ethiopian_to_gregorian, 
    convert_gregorian_to_ethiopian
)

class EthiopianDateService:
    @staticmethod
    def ethiopian_to_gregorian(date_str):
        """Converts YYYY-MM-DD Ethiopian string to Gregorian date object"""
        try:
            y, m, d = [int(p) for p in date_str.split('-')]
            g_y, g_m, g_d = convert_ethiopian_to_gregorian(y, m, d)
            return datetime.date(g_y, g_m, g_d)
        except Exception:
            return None

    @staticmethod
    def get_current_eth_year():
        """Returns the current Ethiopian year based on today's Gregorian date"""
        today = datetime.date.today()
        e_y, e_m, e_d = convert_gregorian_to_ethiopian(today.year, today.month, today.day)
        return e_y

    @staticmethod
    def validate_ethiopian_date_str(date_str):
        """Used by the save() methods to ensure string format is correct"""
        try:
            parts = date_str.split('-')
            return len(parts) == 3
        except:
            return False

class ChristianService:
    @staticmethod
    @transaction.atomic
    def generate_church_id(instance):
        from .models import Christian
        
        # Get prefix from settings (e.g., 'AB')
        prefix = getattr(settings, 'CHURCH_ABBREV', 'CH')
        year = EthiopianDateService.get_current_eth_year()
        year_yy = str(year)[-2:]
        
        # Lock rows for the current year to ensure serial roll assignment
        last_rec = Christian.objects.filter(
            record_entry_year_eth=year
        ).select_for_update().order_by('-christian_roll_number').first()
        
        roll = (last_rec.christian_roll_number + 1) if last_rec else 1
        generated_id = f"{prefix}{year_yy}{roll:05d}"

        AuditLogger.log(
            actor=instance.user,
            action_type="CHRISTIAN_ID_GENERATED",
            entity=instance,
            metadata={
                "christian_id": generated_id,
                "christian_name": instance.first_name + " " + instance.father_name,
                "roll_number": roll,
                "entry_year": year
            }
        )
        
        return generated_id, roll, year