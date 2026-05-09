"""
Django settings for Saree Store (monolithic, templates + Bootstrap 5).
"""

import os
import dj_database_url
from pathlib import Path

import environ
from django.contrib.messages import constants as msg_constants

BASE_DIR = Path(__file__).resolve().parent.parent

_env_file = BASE_DIR / ".env"
if _env_file.is_file():
    # overwrite=True: values in `.env` override empty/preset OS env vars (e.g. RESEND_API_KEY).
    environ.Env.read_env(_env_file, overwrite=True)

MESSAGE_TAGS = {
    msg_constants.DEBUG: "secondary",
    msg_constants.INFO: "info",
    msg_constants.SUCCESS: "success",
    msg_constants.WARNING: "warning",
    msg_constants.ERROR: "danger",
}

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-uvs)rc^q_zn0%r&i#-ibltub&)9nm4c)4d(l7%z7gqh1q1@5t!')

DEBUG = os.environ.get('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "*"]

# Reverse proxy (Render, Railway, etc.): trust TLS + host from proxy headers.
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

# HTTPS sites on Render etc.: set CSRF_TRUSTED_ORIGINS=https://your-app.onrender.com
# (comma-separated). Avoids 403 on POST/login when DEBUG=False.
_csrf_raw = os.environ.get("CSRF_TRUSTED_ORIGINS", "").strip()
if _csrf_raw:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_raw.split(",") if o.strip()]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "shop",
    "dashboard",
    "staff_admin",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.media",
                "shop.context_processors.cart_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Set DATABASE_URL for Postgres (Render dashboard, or External URL in local `.env`).
# No DATABASE_URL → SQLite at BASE_DIR/db.sqlite3 for local dev without Postgres.
_database_url = os.environ.get("DATABASE_URL")
if _database_url:
    DATABASES = {
        "default": dj_database_url.parse(
            _database_url,
            conn_max_age=600,
            ssl_require=os.environ.get("DATABASE_SSL_REQUIRE", "true").lower()
            in ("1", "true", "yes"),
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Leading slashes so browser resolves /media/... from any page (fixes broken product images).
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Resend (https://resend.com) — transactional email (verification + order updates).
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
# Use a verified-domain address in production. Until then, Resend only delivers
# “from” onboarding@resend.dev and may restrict “to” addresses (see Resend dashboard).
RESEND_FROM_EMAIL = os.environ.get(
    "RESEND_FROM_EMAIL",
    "onboarding@resend.dev",
)

AUTH_USER_MODEL = "accounts.User"

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
