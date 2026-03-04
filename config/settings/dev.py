from .base import *  # noqa

DEBUG = True

# For local development, allow all hosts
ALLOWED_HOSTS = ["*"]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
