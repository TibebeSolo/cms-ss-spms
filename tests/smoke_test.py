import pytest
from django.conf import settings

@pytest.mark.django_db
def test_settings_loaded():
    assert settings.SECRET_KEY is not None
    assert "identity" in settings.INSTALLED_APPS

def test_basic_addition():
    assert 1 + 1 == 2
