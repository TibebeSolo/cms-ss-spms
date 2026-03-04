import pytest
from django.conf import settings

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Globally enable database access for all tests.
    """
    pass

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()
