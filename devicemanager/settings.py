"""
Django settings for devicemanager project.

Generated by 'django-admin startproject' using Django 5.0.3.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

from pathlib import Path

import environ

env = environ.Env(
    MARIADB_USER=(str, "maria_db"),
    MARIADB_PASSWORD=(str, "maria_db"),
    MARIADB_DATABASE=(str, "device_manager"),
    MARIADB_HOST=(str, "127.0.0.1"),
    GOOGLE_CLIENT_ID=(str, "534939113963-72f2ph3fve2e7q374phrq4cl66r6jetd.apps.googleusercontent.com"),
    GOOGLE_CLIENT_SECRET=(str, "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"),
    GITHUB_CLIENT_ID=(str, "cb3e145ad1d73bc4dfe2"),
    GITHUB_CLIENT_SECRET=(str, "916cae2335f7a158afe4b93247b85201a444c3c2"),
    AUTHENTIK_CLIENT_ID=(str, "1XKXhk8IIi3RlLBkS9cCiIjzj0DDnh1NOcOM8epN"),
    AUTHENTIK_CLIENT_SECRET=(
        str,
        "LPKVuxWeiAjPePmHkL3ylGjLNllXBTZBtMz5q9VHvzsEHf45RlEQxlZifWa4Q99rB7gx0OwpNzOh63mIwTRygPhZaPlvV57Ils2hpCIoaCd1JfrfPbJWoNQPOq4yrBxR",
    ),
)
environ.Env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-&#w*b7*0v3z4z62l989)sjk6wqdj_%v-)ty(7iakr+nw9&4i(%"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    "jazzmin",
    "devicemanager.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_extensions",
    "debug_toolbar",
    "rest_framework",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",
    "allauth.socialaccount.providers.google",
    "drf_spectacular",
    "colorfield",
    "devicemanager.users.providers.authentik",
    "devicemanager.inventory",
    "devicemanager.utils",
    "devicemanager.users",
]

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["devicemanager.drf_permissions.DRFPermissions"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "DeviceManager",
    "DESCRIPTION": "Application to manage devices in AGH WFiIS",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # OTHER SETTINGS
}

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("GOOGLE_CLIENT_ID"),
            "secret": env("GOOGLE_CLIENT_SECRET"),
            "key": "",
        },
        "SCOPE": [
            "profile",
            "email",
        ],
    },
    "github": {
        "APP": {"client_id": env("GITHUB_CLIENT_ID"), "secret": env("GITHUB_CLIENT_SECRET")},
        "SCOPE": ["user", "profile", "email", "oidc"],
    },
    "authentik": {
        "APP": {
            "client_id": env("AUTHENTIK_CLIENT_ID"),
            "secret": env("AUTHENTIK_CLIENT_SECRET"),
        },
        "SCOPE": ["user", "profile", "email", "user:email"],
    },
}

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ROOT_URLCONF = "devicemanager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            "libraries": {
                "jazzmin": "templatetags.jazzmin",
            },
        },
    },
]

WSGI_APPLICATION = "devicemanager.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MARIADB_DATABASE"),
        "USER": env("MARIADB_USER"),
        "PASSWORD": env("MARIADB_PASSWORD"),
        "HOST": env("MARIADB_HOST"),
        "PORT": 3306,
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
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

# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

TEST_RUNNER = "devicemanager.testrunner.PytestTestRunner"

AUTH_USER_MODEL = "users.User"

JAZZMIN_SETTINGS = {
    "site_title": "Device Manager",
    "site_header": "Device Manager",
    "site_brand": "Device Manager",
    "site_logo": "common/img/AGH_logo.png",
    "site_logo_classes": "img-logo",
    "custom_css": "common/css/jazzmin.css",
    "icons": {
        "users.user": "fas fa-user",
        "users.displaynamedecorator": "fas fa-solid fa-graduation-cap",
        "auth.Group": "fas fa-users",
        "inventory.building": "fas fa-building",
        "inventory.device": "fas fa-laptop",
        "inventory.devicemodel": "fas fa-tablet",
        "inventory.devicetype": "fas fa-blender-phone",
        "inventory.faculty": "fas fa-building",
        "inventory.manufacturer": "fas fa-industry",
        "inventory.qrcodegenerationconfig": "fas fa-qrcode",
        "inventory.devicerental": "fas fa-scroll",
        "inventory.room": "fas fa-door-open",
        "socialaccount.socialaccount": "fas fa-user",
        "socialaccount.socialtoken": "fas fa-key",
        "socialaccount.socialapp": "fas fa-share-alt",
        "account.emailaddress": "fas fa-at",
    },
    "order_with_respect_to": [
        "users.User",
        "users.DisplayNameDecorator",
        "inventory.device",
        "inventory.devicerental",
        "inventory.devicemodel",
        "inventory.devicetype",
        "inventory.manufacturer",
        "inventory.faculty",
        "inventory.building",
        "inventory.room",
        "inventory.qrcodegenerationconfig",
    ],
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": False,
    "brand_small_text": False,
    "brand_colour": "navbar-orange",
    "accent": "accent-primary",
    "navbar": "navbar-success",
    "no_navbar_border": False,
    "navbar_fixed": False,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "cyborg",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success",
    },
}

# Silence
# - ?: (templates.E003) 'jazzmin' is used for multiple template tag modules
SILENCED_SYSTEM_CHECKS = ["templates.E003"]

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

INTERNAL_IPS = [
    "127.0.0.1",
]

LOGIN_REDIRECT_URL = "/"

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "emails"
MEDIA_ROOT = BASE_DIR / "build/media"
STATIC_ROOT = BASE_DIR / "build/static"
