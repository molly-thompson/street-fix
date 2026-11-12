"""Local settings for the project."""

import os

import dj_database_url
from dotenv import load_dotenv

from .base import *

# Load local environment variables
load_dotenv()

# If these variables are not configured, end immediately
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

DATABASES = {
    "default": dj_database_url.config(
        conn_max_age=600,
        conn_health_checks=True,
    ),
}

# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}
