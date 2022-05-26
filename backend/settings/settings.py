"""
Django settings for settings project.

Generated by 'django-admin startproject' using Django 3.2.4.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""
import datetime
import os
from collections import OrderedDict
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv()

server_settings = {}
SETTINGS_FILE = os.getenv("SETTINGS_FILE", "/etc/django/settings-tournesol.yaml")
try:
    with open(SETTINGS_FILE, "r") as f:
        server_settings = yaml.full_load(f)
except FileNotFoundError:
    print("No local settings.")
    pass

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = server_settings.get(
    "SECRET_KEY", "django-insecure-(=8(97oj$3)!#j!+^&bh_+5v5&1pfpzmaos#z80c!ia5@9#jz1"
)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = server_settings.get("DEBUG", False)
ALLOWED_HOSTS = server_settings.get("ALLOWED_HOSTS", ["127.0.0.1", "localhost"])
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

STATIC_URL = "/static/"
MEDIA_URL = "/media/"

# It is considered quite unsafe to use the /tmp directory, so we might as well use a dedicated root folder in HOME
base_folder = f"{os.environ.get('HOME')}/.tournesol"
STATIC_ROOT = server_settings.get("STATIC_ROOT", f"{base_folder}{STATIC_URL}")
MEDIA_ROOT = server_settings.get("MEDIA_ROOT", f"{base_folder}{MEDIA_URL}")

MAIN_URL = server_settings.get("MAIN_URL", "http://localhost:8000/")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_prometheus",
    "core",
    "tournesol",
    "twitterbot",
    "ml",
    "oauth2_provider",
    "corsheaders",
    "rest_framework",
    "drf_spectacular",
    "rest_registration",
    "vouch",
]

REST_REGISTRATION_MAIN_URL = server_settings.get(
    "REST_REGISTRATION_MAIN_URL", "http://localhost:3000/"
)
REST_REGISTRATION = {
    "REGISTER_VERIFICATION_ENABLED": True,
    "REGISTER_VERIFICATION_URL": REST_REGISTRATION_MAIN_URL + "verify-user/",
    "REGISTER_VERIFICATION_ONE_TIME_USE": True,
    "SEND_RESET_PASSWORD_LINK_USER_FINDER": "core.utils.rest_registration.users.find_user_by_send_reset_password_link_data",
    "RESET_PASSWORD_VERIFICATION_ENABLED": True,
    "RESET_PASSWORD_VERIFICATION_URL": REST_REGISTRATION_MAIN_URL + "reset-password/",
    "RESET_PASSWORD_FAIL_WHEN_USER_NOT_FOUND": False,  # to be set to True to prevent user enumeration
    "RESET_PASSWORD_VERIFICATION_ONE_TIME_USE": True,
    "REGISTER_EMAIL_SERIALIZER_CLASS": "core.serializers.user.RegisterEmailSerializer",
    "REGISTER_EMAIL_VERIFICATION_ENABLED": True,
    "REGISTER_EMAIL_VERIFICATION_URL": REST_REGISTRATION_MAIN_URL + "verify-email/",
    "REGISTER_SERIALIZER_CLASS": "core.serializers.user.RegisterUserSerializer",
    "PROFILE_SERIALIZER_CLASS": "core.serializers.user.UserProfileSerializer",
    "VERIFICATION_FROM_EMAIL": "noreply@tournesol.app",
    "REGISTER_VERIFICATION_EMAIL_TEMPLATES": {
        "html_body": "accounts/register/body.html",
        "subject": "accounts/register/subject.txt",
    },
    "REGISTER_EMAIL_VERIFICATION_EMAIL_TEMPLATES": {
        "html_body": "accounts/register_email/body.html",
        "subject": "accounts/register_email/subject.txt",
    },
    "RESET_PASSWORD_VERIFICATION_EMAIL_TEMPLATES": {
        "html_body": "accounts/reset_password/body.html",
        "subject": "accounts/reset_password/subject.txt",
    },
    "VERIFICATION_EMAIL_HTML_TO_TEXT_CONVERTER": "rest_registration.utils.html.convert_html_to_text",
}

EMAIL_BACKEND = server_settings.get(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = server_settings.get("EMAIL_HOST", "")
EMAIL_PORT = server_settings.get("EMAIL_PORT", "")
EMAIL_HOST_USER = server_settings.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = server_settings.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = server_settings.get("EMAIL_USE_TLS", "")
EMAIL_USE_SSL = server_settings.get("EMAIL_USE_SSL", "")


# Modèle utilisateur utilisé par Django (1.5+)
AUTH_USER_MODEL = "core.user"

MIDDLEWARE = [
    "django_prometheus.middleware.PrometheusBeforeMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_prometheus.middleware.PrometheusAfterMiddleware",
]

ROOT_URLCONF = "settings.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "core" / "templates",
        ],
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

LOCALE_PATHS = [
    BASE_DIR / "core" / "locale",
]

WSGI_APPLICATION = "settings.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = OrderedDict(
    [
        [
            "default",
            {
                "ENGINE": "django_prometheus.db.backends.postgresql",
                "NAME": server_settings.get("DATABASE_NAME", "tournesol"),
                "USER": server_settings.get("DATABASE_USER", "postgres"),
                "PASSWORD": server_settings.get("DATABASE_PASSWORD", "password"),
                "HOST": server_settings.get("DATABASE_HOST", "localhost"),
                "PORT": server_settings.get("DATABASE_PORT", 5432),
                "NUMBER": 42,
            },
        ]
    ]
)

DRF_RECAPTCHA_PUBLIC_KEY = server_settings.get(
    "DRF_RECAPTCHA_PUBLIC_KEY", "dsfsdfdsfsdfsdfsdf"
)
DRF_RECAPTCHA_SECRET_KEY = server_settings.get(
    "DRF_RECAPTCHA_SECRET_KEY", "dsfsdfdsfsdf"
)


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

OAUTH2_PROVIDER = {
    "OIDC_ENABLED": server_settings.get("OIDC_ENABLED", False),
    "OIDC_RSA_PRIVATE_KEY": server_settings.get(
        "OIDC_RSA_PRIVATE_KEY", "dsfsdfdsfsdfsdfsdf"
    ),
    "SCOPES": {
        "openid": "OpenID Connect scope",
        "read": "Read scope",
        "write": "Write scope",
        "groups": "Access to your groups",
    },
    "OAUTH2_VALIDATOR_CLASS": "core.oauth_validator.CustomOAuth2Validator",
    "OIDC_ISS_ENDPOINT": server_settings.get("OIDC_ISS_ENDPOINT", ""),
    "ACCESS_TOKEN_EXPIRE_SECONDS": server_settings.get(
        "ACCESS_TOKEN_EXPIRE_SECONDS", 36000
    ),  # 10h
    "REFRESH_TOKEN_EXPIRE_SECONDS": server_settings.get(
        "REFRESH_TOKEN_EXPIRE_SECONDS", 604800
    ),  # 1w
}
LOGIN_URL = server_settings.get("LOGIN_URL", "")

CORS_ALLOWED_ORIGINS = server_settings.get("CORS_ALLOWED_ORIGINS", [])
CORS_ALLOW_CREDENTIALS = server_settings.get("CORS_ALLOW_CREDENTIALS", False)

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 30,
    # important to have no basic auth here
    # as we are using Apache with basic auth
    # https://stackoverflow.com/questions/40094823/django-rest-framework-invalid-username-password
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "oauth2_provider.contrib.rest_framework.OAuth2Authentication",
    ),
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.ScopedRateThrottle",
        "tournesol.throttling.BurstAnonRateThrottle",
        "tournesol.throttling.BurstUserRateThrottle",
        "tournesol.throttling.SustainedAnonRateThrottle",
        "tournesol.throttling.SustainedUserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon_burst": "120/min",
        "user_burst": "120/min",
        "anon_sustained": "3600/hour",
        "user_sustained": "3600/hour",
        # specific rates for specific parts of the API
        "api_video_post": "50/min",
        "api_users_me_export": "10/min",
        "api_export_comparisons": "10/min",
        # global throttle on account registrations and password reset
        "email": server_settings.get("THROTTLE_EMAIL_GLOBAL", "15/min"),
    },
}

LEGACY_CRITERIAS = [
    'largely_recommended',
    'reliability',
    'importance',
    'engaging',
    'pedagogy',
    'layman_friendly',
    'diversity_inclusion',
    'backfire_risk',
    'better_habits',
    'entertaining_relaxing',
]

# maximal weight to assign to a rating for a particular feature, see #41
MAX_FEATURE_WEIGHT = 8

SPECTACULAR_SETTINGS = {
    # Split data components into 2 distinct schemas for request and response.
    # It helps with the support of "read_only" fields by code generators.
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATION_PARAMETERS": False,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "oauth2RedirectUrl": MAIN_URL + "docs/",
    },
    "SWAGGER_UI_OAUTH2_CONFIG": {
        "clientId": server_settings.get("SWAGGER_UI_OAUTH2_CLIENT_ID", ""),
        "clientSecret": server_settings.get("SWAGGER_UI_OAUTH2_CLIENT_SECRET", ""),
        "appName": "Swagger UI",
        "scopes": "read write groups",
    },
    "SECURITY": [
        {
            "oauth2": ["read write groups"],
        }
    ],
    "OAUTH2_FLOWS": ["password"],
    "OAUTH2_AUTHORIZATION_URL": None,
    "OAUTH2_TOKEN_URL": MAIN_URL + "o/token/",
    "OAUTH2_REFRESH_URL": MAIN_URL + "o/token/",
    "OAUTH2_SCOPES": "read write groups",
    "TITLE": "Tournesol API",
    "ENUM_NAME_OVERRIDES": {
        "ScoreModeEnum": "tournesol.models.entity_score.Scoreode",
    }
}

YOUTUBE_API_KEY = server_settings.get("YOUTUBE_API_KEY", "")
ENABLE_API_WIKIDATA = server_settings.get("ENABLE_API_WIKIDATA", {"MIGRATIONS": False})

TWITTERBOT_CREDENTIALS = server_settings.get("TWITTERBOT_CREDENTIALS", {})

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": os.environ.get("DJANGO_LOG_LEVEL", "DEBUG"),
    },
    "loggers": {
        "factory": {
            "level": "WARN"
        },
        "faker": {
            "level": "INFO"
        }
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "default_cache_table",
        "OPTIONS": {
            "MAX_ENTRIES": 3000, # default value is 300
        }
    }
}

VIDEO_METADATA_EXPIRE_SECONDS = 2 * 24 * 3600  # 2 days

RECOMMENDATIONS_MIN_CONTRIBUTORS = 2

# Configuration of the app `core`
# See the documentation for the complete description.
APP_CORE = {
    "MGMT_DELETE_INACTIVE_USERS_PERIOD":
        # sync the value with the validity period of the validation emails
        REST_REGISTRATION.get(
            "REGISTER_VERIFICATION_PERIOD",
            datetime.timedelta(days=7)
        )
}
