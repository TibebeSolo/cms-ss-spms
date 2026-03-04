import pytest
from org.models import Parish, SundaySchool
from people.models import Christian
from sundayschool.models import SSStudentProfile, Grade, Section, StudentStatus
from melody.models import MezemranMembership
from org.services import generate_ssid, generate_christian_id, generate_mezemran_id

@pytest.fixture
def setup_org(db):
    parish = Parish.objects.create(
        name="Test Parish",
        address="Test Addr",
        phone="0911000000",
        diocese_name="Addis Ababa",
        church_abbrev="CH"
    )
    ss = SundaySchool.objects.create(
        parish=parish,
        name="Test SS",
        abbreviation="SS",
        phone="0911000001"
    )
    return parish, ss

@pytest.mark.django_db
def test_generate_ssid_increment(setup_org):
    parish, ss = setup_org
    grade = Grade.objects.create(name="1", order_no=1)
    section = Section.objects.create(name="A")
    status = StudentStatus.objects.create(name="Active")
    
    christian = Christian.objects.create(first_name="Tibebe", father_name="Solo", grandfather_name="X")
    
    profile1 = SSStudentProfile.objects.create(
        christian=christian,
        joined_year_eth=2016,
        ss_roll_number=0, # placeholder
        grade=grade,
        section=section,
        student_status=status
    )
    
    id1 = generate_ssid(profile1)
    assert id1 == "SS16001"
    
    christian2 = Christian.objects.create(first_name="Abebe", father_name="Beso", grandfather_name="Y")
    profile2 = SSStudentProfile.objects.create(
        christian=christian2,
        joined_year_eth=2016,
        ss_roll_number=0,
        grade=grade,
        section=section,
        student_status=status
    )
    id2 = generate_ssid(profile2)
    assert id2 == "SS16002"

@pytest.mark.django_db
def test_generate_christian_id_increment(setup_org):
    parish, ss = setup_org
    christian = Christian.objects.create(first_name="Tibebe", father_name="Solo")
    
    id1 = generate_christian_id(christian, 2016)
    assert id1 == "CH1600001"
    
    christian2 = Christian.objects.create(first_name="Abebe", father_name="Beso")
    id2 = generate_christian_id(christian2, 2016)
    assert id2 == "CH1600002"

@pytest.mark.django_db
def test_generate_mezemran_id_increment(setup_org):
    parish, ss = setup_org
    grade = Grade.objects.create(name="1", order_no=1)
    section = Section.objects.create(name="A")
    status = StudentStatus.objects.create(name="Active")
    christian = Christian.objects.create(first_name="Tibebe", father_name="Solo")
    
    profile = SSStudentProfile.objects.create(
        christian=christian,
        joined_year_eth=2016,
        ss_roll_number=1,
        grade=grade,
        section=section,
        student_status=status
    )
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    admin = User.objects.create(username="admin")
    
    import datetime
    membership = MezemranMembership.objects.create(
        ss_student_profile=profile,
        mezmur_entry_year_eth=2016,
        mezemran_roll_number=0,
        mezemran_id="",
        selected_at=datetime.datetime.now(),
        selected_by=admin,
        selection_reason="Test"
    )
    
    id1 = generate_mezemran_id(membership)
    assert id1 == "SSMZ16001"
