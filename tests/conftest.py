"""Shared fixtures for the test suite."""

import pytest

from site_settings.models import ThemeSettings


@pytest.fixture
def theme_settings(db: None) -> ThemeSettings:
    """Provide the persisted site theme singleton."""
    return ThemeSettings.objects.create()
