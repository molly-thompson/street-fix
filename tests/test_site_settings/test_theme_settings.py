"""Tests for persisted theme settings and template integration."""

import pytest
from colorfield.widgets import ColorWidget
from django.contrib.admin.sites import AdminSite
from django.core.exceptions import ValidationError
from django.test import Client, RequestFactory

from site_settings.admin import ThemeSettingsAdmin
from site_settings.models import ThemeSettings


def test_saves_and_exposes_core_and_optional_theme_values(
    client: Client, theme_settings: ThemeSettings
) -> None:
    """Expose configured theme tokens as safe CSS custom properties."""
    theme_settings.primary_color = "#123456"
    theme_settings.background_color = "#f0f0f0"
    theme_settings.text_color = "#202020"
    theme_settings.radius = "8px"
    theme_settings.surface_color = "#eeeeee"
    theme_settings.link_color = "#654321"
    theme_settings.save()

    response = client.get("/")
    content = response.content.decode()

    assert "--theme-primary: #123456;" in content
    assert "--theme-background: #f0f0f0;" in content
    assert "--theme-text: #202020;" in content
    assert "--theme-radius: 8px;" in content
    assert "--theme-surface: #eeeeee;" in content
    assert "--theme-link: #654321;" in content
    assert "--theme-border:" not in content


def test_rejects_invalid_color_values() -> None:
    """Reject values that could break out of a CSS declaration."""
    settings = ThemeSettings(primary_color="red; color: black")

    with pytest.raises(ValidationError):
        settings.save()


@pytest.mark.django_db
def test_rejects_low_contrast_text_before_writing() -> None:
    """Do not persist text/background pairs that fail WCAG AA."""
    settings = ThemeSettings(text_color="#777777")

    with pytest.raises(ValidationError) as error:
        settings.save()

    assert "text_color" in error.value.message_dict
    assert not ThemeSettings.objects.exists()


@pytest.mark.django_db
def test_rejects_low_contrast_primary_action_text() -> None:
    """Validate default white text against the configured primary color."""
    settings = ThemeSettings(primary_color="#ffffff")

    with pytest.raises(ValidationError) as error:
        settings.save()

    assert "primary_color" in error.value.message_dict
    assert not ThemeSettings.objects.exists()


@pytest.mark.django_db
def test_accepts_text_just_above_the_contrast_threshold() -> None:
    """Accept near-threshold text when explicit tokens keep all pairs legible."""
    settings = ThemeSettings(
        text_color="#767676",
        surface_color="#ffffff",
        emphasis_text_color="#767676",
        muted_text_color="#767676",
    )

    settings.save()

    assert ThemeSettings.objects.get().text_color == "#767676"


@pytest.mark.parametrize(
    ("field_name", "value", "error_field"),
    (
        ("surface_color", "#0f172a", "surface_color"),
        ("link_color", "#777777", "link_color"),
        ("success_surface_color", "#166534", "success_surface_color"),
    ),
)
def test_rejects_low_contrast_explicit_theme_colors(
    field_name: str,
    value: str,
    error_field: str,
) -> None:
    """Attribute contrast errors to explicit surface, link, and status colors."""
    settings = ThemeSettings(**{field_name: value})

    with pytest.raises(ValidationError) as error:
        settings.save()

    assert error_field in error.value.message_dict


@pytest.mark.parametrize(
    ("field_name", "value"),
    (("text_color", "#777777"), ("radius", "2vh")),
)
def test_rejected_theme_update_does_not_change_persisted_value(
    theme_settings: ThemeSettings,
    field_name: str,
    value: str,
) -> None:
    """A failed singleton update leaves the previously stored value intact."""
    previous_value = getattr(theme_settings, field_name)
    setattr(theme_settings, field_name, value)

    with pytest.raises(ValidationError):
        theme_settings.save()

    persisted_settings = ThemeSettings.objects.get(pk=1)
    assert getattr(persisted_settings, field_name) == previous_value


def test_admin_uses_colorfield_picker_for_core_and_optional_colors() -> None:
    """Use django-colorfield pickers, including clearable optional values."""
    request = RequestFactory().get("/admin/")
    form_class = ThemeSettingsAdmin(ThemeSettings, AdminSite()).get_form(request)
    form = form_class()

    assert isinstance(form.fields["primary_color"].widget, ColorWidget)
    assert isinstance(form.fields["surface_color"].widget, ColorWidget)
    assert not form.fields["surface_color"].required


@pytest.mark.parametrize("radius", ("0", "8px", "0.375rem", "1em"))
@pytest.mark.django_db
def test_accepts_valid_radius_values(radius: str) -> None:
    """Accept supported radius values."""
    settings = ThemeSettings(radius=radius)

    settings.save()

    assert ThemeSettings.objects.get().radius == radius


@pytest.mark.parametrize(
    "radius",
    ("1rem; color: red", "8", "-1px", "8vh", ".5rem"),
)
def test_rejects_invalid_radius_values(radius: str) -> None:
    """Reject malformed or unsupported radius values."""
    settings = ThemeSettings(radius=radius)

    with pytest.raises(ValidationError):
        settings.save()


def test_settings_are_a_singleton(theme_settings: ThemeSettings) -> None:
    """Save later settings edits to the existing singleton row."""
    updated_settings = ThemeSettings(primary_color="#654321")
    updated_settings.save()

    assert ThemeSettings.objects.count() == 1
    assert ThemeSettings.objects.get().primary_color == "#654321"
