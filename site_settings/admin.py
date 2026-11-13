"""Admin configuration for site-wide settings."""

from django.contrib import admin
from django.http import HttpRequest

from site_settings.models import ThemeSettings


@admin.register(ThemeSettings)
class ThemeSettingsAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    """Expose the singleton theme settings to site administrators."""

    fieldsets = [
        (
            "Core theme",
            {"fields": ("primary_color", "background_color", "text_color", "radius")},
        ),
        (
            "Optional overrides",
            {
                "fields": (
                    "surface_color",
                    "emphasis_text_color",
                    "border_color",
                    "muted_text_color",
                    "link_color",
                    "link_hover_color",
                    "on_primary_color",
                    "primary_hover_color",
                    "primary_active_color",
                    "secondary_color",
                    "success_color",
                    "warning_color",
                    "danger_color",
                    "success_surface_color",
                    "warning_surface_color",
                    "danger_surface_color",
                ),
                "description": (
                    "Leave a value blank to use the theme-derived or default value."
                ),
            },
        ),
    ]

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Allow creating settings only when the singleton does not exist."""
        return not ThemeSettings.objects.filter(
            pk=1
        ).exists() and super().has_add_permission(request)

    def has_delete_permission(
        self, request: HttpRequest, obj: ThemeSettings | None = None
    ) -> bool:
        """Keep the site configuration from being accidentally deleted."""
        return False
