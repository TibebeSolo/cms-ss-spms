# Generate default password and return it.

from django.utils.crypto import get_random_string

DEFAULT_PASSWORD_LENGTH = 6

DEFAULT_PASSWORD_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+'


def generate_default_password():
    return f"Default Password: {get_random_string(DEFAULT_PASSWORD_LENGTH, allowed_chars=DEFAULT_PASSWORD_CHARS)}"
    