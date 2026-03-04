import datetime
from django.db import transaction, models
from ethioqen.calendar_conversion import convert_gregorian_to_ethiopian
from django.conf import settings
from org.models import SundaySchool, Parish

def get_ethiopian_year_from_gregorian(date_val=None):
    if date_val is None:
        date_val = datetime.date.today()
    
    eth_date = convert_gregorian_to_ethiopian(date_val.year, date_val.month, date_val.day)
    return eth_date[0]

@transaction.atomic
def generate_ssid(ss_profile):
    """
    Format: {SSAbbrev}{YY}{RRR} (3-digit roll, resets yearly)
    """
    ss = SundaySchool.objects.first() # In MVP we assume one SS per instance
    if not ss or not ss.abbreviation:
        raise ValueError("Sunday School abbreviation not configured")
    
    year_eth = ss_profile.joined_year_eth
    # Get last SSID for this year to determine roll
    ss_prefix = ss.abbreviation
    year_prefix = str(year_eth)[-2:] # last 2 digits
    
    from sundayschool.models import SSStudentProfile
    
    # We use a simple count or max-id-based approach within the atomic transaction
    # For high concurrency, a separate counter model is better, but this works for MVP
    latest = SSStudentProfile.objects.filter(
        joined_year_eth=year_eth
    ).order_by('-ss_roll_number').first()
    
    next_roll = (latest.ss_roll_number + 1) if latest else 1
    
    # Update profile
    ss_profile.ss_roll_number = next_roll
    ss_profile.ssid = f"{ss_prefix}{year_prefix}{str(next_roll).zfill(3)}"
    ss_profile.save()
    return ss_profile.ssid

@transaction.atomic
def generate_christian_id(christian_profile, entry_year_eth):
    """
    Format: {ChurchAbbrev}{YY}{RRRRR} (5-digit roll, resets yearly)
    """
    parish = Parish.objects.first()
    if not parish or not parish.church_abbrev:
        raise ValueError("Parish church abbreviation not configured")
    
    year_prefix = str(entry_year_eth)[-2:]
    church_prefix = parish.church_abbrev
    
    from people.models import Christian
    
    # Find latest record for this year to determine next roll
    latest = Christian.objects.filter(
        record_entry_year_eth=entry_year_eth
    ).order_by('-christian_roll_number').first()
    
    next_roll = (latest.christian_roll_number + 1) if latest else 1
    
    christian_profile.christian_roll_number = next_roll
    christian_profile.record_entry_year_eth = entry_year_eth
    christian_profile.church_id = f"{church_prefix}{year_prefix}{str(next_roll).zfill(5)}"
    christian_profile.save()
    return christian_profile.church_id

@transaction.atomic
def generate_mezemran_id(membership):
    """
    Format: {SSAbbrev}MZ{YY}{RRR} (3-digit roll, resets yearly)
    """
    ss = SundaySchool.objects.first()
    year_eth = membership.mezmur_entry_year_eth
    year_prefix = str(year_eth)[-2:]
    ss_prefix = ss.abbreviation
    
    from melody.models import MezemranMembership
    
    latest = MezemranMembership.objects.filter(
        mezmur_entry_year_eth=year_eth
    ).order_by('-mezemran_roll_number').first()
    
    next_roll = (latest.mezemran_roll_number + 1) if latest else 1
    
    membership.mezemran_roll_number = next_roll
    membership.mezemran_id = f"{ss_prefix}MZ{year_prefix}{str(next_roll).zfill(3)}"
    membership.save()
    return membership.mezemran_id
