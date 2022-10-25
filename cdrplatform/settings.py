"""
Django settings for cdrplatform project.

Generated by 'django-admin startproject' using Django 4.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

import os
from pathlib import Path

import environ

env = environ.Env(DJANGO_DEBUG=(bool, False))
# This will be disabled in future anyway so explicitly disable now to avoid any
# future weirdness
env.smart_cast = False
env.prefix = (
    "CDRPLATFORM_"  # All environment variables must be prefixed with `CDRPLATFORM_`
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Load any .env files
env.read_env(os.path.join(BASE_DIR, ".env"))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", False)

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=[])

INTERNAL_IPS = env.list("INTERNAL_IPS", default=[])


# Application definition

BASE_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    # Use whitenoise to serve static files in development
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
)

THIRD_PARTY_APPS = (
    "flags",
    "rest_framework",
    "rest_framework_api_key",
    "drf_spectacular",
    "drf_standardized_errors",
)

if DEBUG:
    THIRD_PARTY_APPS = THIRD_PARTY_APPS + ("debug_toolbar",)

CUSTOM_APPS = ("cdrplatform.core",)

INSTALLED_APPS = BASE_APPS + THIRD_PARTY_APPS + CUSTOM_APPS

MIDDLEWARE_INITIAL = (
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
)

if DEBUG:
    # Add debug toolbar middleware as early as possible but after anything that
    # encodes response content
    # https://django-debug-toolbar.readthedocs.io/en/latest/installation.html#add-the-middleware
    MIDDLEWARE_INITIAL += ("debug_toolbar.middleware.DebugToolbarMiddleware",)

MIDDLEWARE_MIDDLE = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
)

MIDDLEWARE_END = (
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

MIDDLEWARE = MIDDLEWARE_INITIAL + MIDDLEWARE_MIDDLE + MIDDLEWARE_END

ROOT_URLCONF = "cdrplatform.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "cdrplatform.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
DATABASES = {"default": env.db_url("DEFAULT_DB_URL")}

CACHES = {"default": env.cache_url("DEFAULT_CACHE_URL")}


# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",  # noqa E501
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = ["cdrplatform.core.hashers.CDRPlatformArgon2PasswordHasher"]

# Custom authentication

AUTH_USER_MODEL = "core.CDRUser"


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LANGUAGE_CODE = "en-us"
LANGUAGE_COOKIE_NAME = "lang"
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "assets",
]


# Whitenoise setup for serving static files
# https://whitenoise.evans.io/en/stable/django.html
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
STATIC_HOST = env.str("STATIC_HOST", "")
STATIC_URL = STATIC_HOST + "/static/"
WHITENOISE_MAX_AGE = env.int("WHITENOISE_MAX_AGE", 120)
WHITENOISE_KEEP_ONLY_HASHED_FILES = True


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Email Settings
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL")
SERVER_EMAIL = env.str("SERVER_EMAIL")

# Securing the Django admin interface a bit through obscurity
ENABLE_DJANGO_ADMIN = env.bool("ENABLE_DJANGO_ADMIN", False)
DJANGO_ADMIN_PATH = env.str("DJANGO_ADMIN_PATH", "admin/").removeprefix("/")

# Django rest framework setting
# https://www.django-rest-framework.org/api-guide/settings/
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_standardized_errors.openapi.AutoSchema",
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.NamespaceVersioning",
    "EXCEPTION_HANDLER": "drf_standardized_errors.handler.exception_handler",
}

APPEND_SLASH = True

# Django Spectacular settings
# https://drf-spectacular.readthedocs.io/en/latest/settings.html
SPECTACULAR_SETTINGS = {
    "TITLE": "CDR Platform API",
    "DESCRIPTION": """Integrate CO2 removal into your business.

Fetch prices and order carbon dioxide removal from a portfolio of suppliers.""",  # noqa: W293, E501
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "CONTACT": {
        "name": "CDR Support",
        "email": "help@cdrplatform.com",
        "url": "https://cdrplatform.com/support",
    },
    "SWAGGER_UI_FAVICON_HREF": STATIC_URL + "favicon.ico",  # default is swagger favicon
    # Used by drf_standardized_errors
    # https://drf-standardized-errors.readthedocs.io/en/latest/openapi.html
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_standardized_errors.openapi_serializers.ValidationErrorEnum.values",  # noqa: E501
        "ClientErrorEnum": "drf_standardized_errors.openapi_serializers.ClientErrorEnum.values",  # noqa: E501
        "ServerErrorEnum": "drf_standardized_errors.openapi_serializers.ServerErrorEnum.values",  # noqa: E501
        "ErrorCode401Enum": "drf_standardized_errors.openapi_serializers.ErrorCode401Enum.values",  # noqa: E501
        "ErrorCode403Enum": "drf_standardized_errors.openapi_serializers.ErrorCode403Enum.values",  # noqa: E501
        "ErrorCode404Enum": "drf_standardized_errors.openapi_serializers.ErrorCode404Enum.values",  # noqa: E501
        "ErrorCode405Enum": "drf_standardized_errors.openapi_serializers.ErrorCode405Enum.values",  # noqa: E501
        "ErrorCode406Enum": "drf_standardized_errors.openapi_serializers.ErrorCode406Enum.values",  # noqa: E501
        "ErrorCode415Enum": "drf_standardized_errors.openapi_serializers.ErrorCode415Enum.values",  # noqa: E501
        "ErrorCode429Enum": "drf_standardized_errors.openapi_serializers.ErrorCode429Enum.values",  # noqa: E501
        "ErrorCode500Enum": "drf_standardized_errors.openapi_serializers.ErrorCode500Enum.values",  # noqa: E501
    },
    "POSTPROCESSING_HOOKS": [
        "drf_standardized_errors.openapi_hooks.postprocess_schema_enums"
    ],
}


# CDR Platform application settings
# ---------------------------------------------------------------------------
