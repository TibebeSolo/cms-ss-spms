import os
import sys
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Add apps to sys.path
sys.path.append(str(BASE_DIR / "apps"))

env = environ.Env()
# Read .env file from the root
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
    # Core Apps
    "org.apps.OrgConfig",
    "identity.apps.IdentityConfig",
    "people.apps.PeopleConfig",
    "sundayschool.apps.SundayschoolConfig",
    "melody.apps.MelodyConfig",
    "audit.apps.AuditConfig",
    "imports.apps.ImportsConfig",
    "reports.apps.ReportsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "identity.middleware.ForcePasswordChangeMiddleware", # Force password change middleware
]

ROOT_URLCONF = "config.urls"

# Auth
AUTH_USER_MODEL = "identity.UserAccount"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "org.context_processors.branding", # Branding Context processors
            ],
        },
    },
]

# Tell Django where your ACTUAL login page lives
LOGIN_URL = 'identity:login'

# Tell Django where to go after a successful login
LOGIN_REDIRECT_URL = 'dashboard'

# Tell Django where to go after logging out
LOGOUT_REDIRECT_URL = 'identity:login'

WSGI_APPLICATION = "config.wsgi.application"

# Database
DATABASES = {
    "default": env.db(
        "DATABASE_URL",
        default=f"postgres://{env('DB_USER')}:{env('DB_PASSWORD')}@{env('DB_HOST')}:{env('DB_PORT')}/{env('DB_NAME')}"
    ),
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {"min_length": 6},
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    'identity.auth_backends.SS_SPMS_Backend',  # Custom role-based logic
    'django.contrib.auth.backends.ModelBackend',   # Fallback
]

# Internationalization
LANGUAGE_CODE = "en"
LANGUAGES = [
    ("am", "Amharic"),
    ("en", "English"),
]
TIME_ZONE = "Africa/Addis_Ababa"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Project Specific
CHURCH_ABBREV = env("CHURCH_ABBREV", default="HS")
SS_ABBREV = env("SS_ABBREV", default="ABSS")
