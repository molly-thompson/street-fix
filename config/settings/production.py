"""Production settings for the project."""

import os

import dj_database_url

from .base import *

DEBUG = False

# If these environment variables are not configured, end immediately
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DATABASE_URL = os.environ["DATABASE_URL"]
ALLOWED_HOSTS = [
    host.strip() for host in os.environ["ALLOWED_HOSTS"].split(",") if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ["CSRF_TRUSTED_ORIGINS"].split(",")
    if origin.strip()
]


DATABASES = {
    "default": dj_database_url.config(conn_max_age=600, ssl_require=True),
}


# Production security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 31536000


# Email
# https://docs.djangoproject.com/en/6.1/topics/email/#topic-email-configuration

MAILERS: dict[str, str] = {}
