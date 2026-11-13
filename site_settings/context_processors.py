"""Template context processors for site-wide settings."""

from typing import TypedDict

from django.http import HttpRequest

from site_settings.models import ThemeSettings


class ThemeContext(TypedDict):
    """Template variables used to configure the runtime theme."""

    theme_css_vars: dict[str, str]


OPTIONAL_THEME_FIELDS = {
    "surface_color": "--theme-surface",
    "emphasis_text_color": "--theme-text-emphasis",
    "border_color": "--theme-border",
    "muted_text_color": "--theme-text-muted",
    "link_color": "--theme-link",
    "link_hover_color": "--theme-link-hover",
    "on_primary_color": "--theme-on-primary",
    "primary_hover_color": "--theme-primary-hover",
    "primary_active_color": "--theme-primary-active",
    "secondary_color": "--theme-secondary",
    "success_color": "--theme-success",
    "warning_color": "--theme-warning",
    "danger_color": "--theme-danger",
    "success_surface_color": "--theme-success-surface",
    "warning_surface_color": "--theme-warning-surface",
    "danger_surface_color": "--theme-danger-surface",
}


def theme_settings(request: HttpRequest) -> ThemeContext:
    """Expose configured theme tokens to every Django template."""
    settings = ThemeSettings.objects.filter(pk=1).first()
    if settings is None:
        return {"theme_css_vars": {}}

    css_vars = {
        "--theme-primary": settings.primary_color,
        "--theme-background": settings.background_color,
        "--theme-text": settings.text_color,
        "--theme-radius": settings.radius,
    }

    for field_name, variable_name in OPTIONAL_THEME_FIELDS.items():
        value = getattr(settings, field_name)
        if value:
            css_vars[variable_name] = value

    return {"theme_css_vars": css_vars}
