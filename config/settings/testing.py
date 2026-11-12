"""Test settings for the project."""

from .development import *

DEBUG = False

SECURE_SSL_REDIRECT = False
WHITENOISE_MANIFEST_STRICT = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # type: ignore[typeddict-item]
    }
}

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
