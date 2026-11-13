"""Models for site-wide configuration."""

from typing import Any

from coloraide import Color
from colorfield.fields import ColorField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

RADIUS_VALIDATOR = RegexValidator(
    regex=r"^(?:0|(?:\d+(?:\.\d+)?)(?:px|rem|em))$",
    message="Enter a radius using px, rem, or em units, or 0.",
)

MINIMUM_TEXT_CONTRAST = 4.5
DEFAULT_SUCCESS_COLOR = "#166534"
DEFAULT_WARNING_COLOR = "#92400e"
DEFAULT_DANGER_COLOR = "#b91c1c"


class ThemeSettings(models.Model):
    """The singleton theme configuration for the site."""

    primary_color = ColorField(
        "primary color",
        max_length=7,
        default="#2563eb",
    )
    background_color = ColorField(
        "page background",
        max_length=7,
        default="#ffffff",
    )
    text_color = ColorField(
        "text color",
        max_length=7,
        default="#0f172a",
    )
    radius = models.CharField(
        max_length=12,
        default="0.375rem",
        validators=[RADIUS_VALIDATOR],
    )

    surface_color = ColorField(
        "surface color",
        max_length=7,
        blank=True,
        default="",
    )
    emphasis_text_color = ColorField(
        "emphasis text color",
        max_length=7,
        blank=True,
        default="",
    )
    border_color = ColorField(
        "border color",
        max_length=7,
        blank=True,
        default="",
    )
    muted_text_color = ColorField(
        "muted text color",
        max_length=7,
        blank=True,
        default="",
    )
    link_color = ColorField(
        "link color",
        max_length=7,
        blank=True,
        default="",
    )
    link_hover_color = ColorField(
        "link hover color",
        max_length=7,
        blank=True,
        default="",
    )
    on_primary_color = ColorField(
        "text on primary color",
        max_length=7,
        blank=True,
        default="",
    )
    primary_hover_color = ColorField(
        "primary hover color",
        max_length=7,
        blank=True,
        default="",
    )
    primary_active_color = ColorField(
        "primary active color",
        max_length=7,
        blank=True,
        default="",
    )
    secondary_color = ColorField(
        "secondary color",
        max_length=7,
        blank=True,
        default="",
    )
    success_color = ColorField(
        "success color",
        max_length=7,
        blank=True,
        default="",
    )
    warning_color = ColorField(
        "warning color",
        max_length=7,
        blank=True,
        default="",
    )
    danger_color = ColorField(
        "danger color",
        max_length=7,
        blank=True,
        default="",
    )
    success_surface_color = ColorField(
        "success alert background",
        max_length=7,
        blank=True,
        default="",
    )
    warning_surface_color = ColorField(
        "warning alert background",
        max_length=7,
        blank=True,
        default="",
    )
    danger_surface_color = ColorField(
        "danger alert background",
        max_length=7,
        blank=True,
        default="",
    )

    class Meta:
        verbose_name = "theme settings"
        verbose_name_plural = "theme settings"

    def __str__(self) -> str:
        """Return the settings label shown in the admin."""
        return "Site theme"

    def save(self, *args: Any, **kwargs: Any) -> None:
        """Validate values and persist the singleton settings row."""
        self.pk = 1
        self.clean_fields()
        self.clean()
        super().save(*args, **kwargs)

    def clean(self) -> None:
        """Validate WCAG AA contrast for the foreground/background pairs."""
        super().clean()
        errors: dict[str, list[str]] = {}

        def check_contrast(
            error_field: str,
            foreground: str | Color,
            background: str | Color,
            description: str,
        ) -> None:
            try:
                foreground_color = (
                    foreground if isinstance(foreground, Color) else Color(foreground)
                )
                ratio = foreground_color.contrast(background, method="wcag21")
            except ValueError:
                return

            if ratio < MINIMUM_TEXT_CONTRAST:
                errors.setdefault(error_field, []).append(
                    f"{description} contrast is {ratio:.2f}:1; "
                    f"WCAG AA requires at least {MINIMUM_TEXT_CONTRAST:.1f}:1."
                )

        def mix(
            background: str, foreground: str, foreground_weight: float
        ) -> str | Color:
            try:
                return Color(background).mix(
                    foreground,
                    percent=foreground_weight,
                    space="srgb",
                )
            except ValueError:
                return background

        surface = self.surface_color or mix(
            self.background_color,
            self.text_color,
            0.04,
        )
        link_color = self.link_color or self.primary_color
        link_hover_color = self.link_hover_color or mix(
            "#000000",
            self.primary_color,
            0.84,
        )
        emphasis_text = self.emphasis_text_color or mix(
            self.background_color,
            self.text_color,
            0.92,
        )
        muted_text = self.muted_text_color or mix(
            self.background_color,
            self.text_color,
            0.64,
        )

        check_contrast(
            "text_color",
            self.text_color,
            self.background_color,
            "Body text on the page background",
        )
        check_contrast(
            "text_color" if not self.surface_color else "surface_color",
            self.text_color,
            surface,
            "Body text on the surface",
        )

        for field_name, color, label in (
            (
                "link_color" if self.link_color else "primary_color",
                link_color,
                "Links",
            ),
            (
                "link_hover_color" if self.link_hover_color else "primary_color",
                link_hover_color,
                "Hovered links",
            ),
            (
                "emphasis_text_color" if self.emphasis_text_color else "text_color",
                emphasis_text,
                "Emphasis text",
            ),
            (
                "muted_text_color" if self.muted_text_color else "text_color",
                muted_text,
                "Muted text",
            ),
            ("primary_color", self.primary_color, "Primary text"),
        ):
            check_contrast(field_name, color, self.background_color, label)
            check_contrast(field_name, color, surface, label)

        on_primary = self.on_primary_color or "#ffffff"
        check_contrast(
            "on_primary_color" if self.on_primary_color else "primary_color",
            on_primary,
            self.primary_color,
            "Text on primary actions",
        )
        primary_hover = self.primary_hover_color or mix(
            self.primary_color,
            "#000000",
            0.12,
        )
        primary_active = self.primary_active_color or mix(
            self.primary_color,
            "#000000",
            0.24,
        )
        check_contrast(
            "primary_hover_color"
            if self.primary_hover_color
            else "on_primary_color"
            if self.on_primary_color
            else "primary_color",
            on_primary,
            primary_hover,
            "Text on hovered primary actions",
        )
        check_contrast(
            "primary_active_color"
            if self.primary_active_color
            else "on_primary_color"
            if self.on_primary_color
            else "primary_color",
            on_primary,
            primary_active,
            "Text on pressed primary actions",
        )

        secondary = self.secondary_color or self.text_color
        check_contrast(
            "secondary_color" if self.secondary_color else "text_color",
            self.background_color,
            secondary,
            "Text on secondary components",
        )

        for field_name, color, explicit_surface, default_color, label in (
            (
                "success_color",
                self.success_color,
                self.success_surface_color,
                DEFAULT_SUCCESS_COLOR,
                "Success status",
            ),
            (
                "warning_color",
                self.warning_color,
                self.warning_surface_color,
                DEFAULT_WARNING_COLOR,
                "Warning status",
            ),
            (
                "danger_color",
                self.danger_color,
                self.danger_surface_color,
                DEFAULT_DANGER_COLOR,
                "Danger status",
            ),
        ):
            status_color = color or default_color
            status_surface = explicit_surface or mix(
                self.background_color,
                status_color,
                0.12,
            )
            check_contrast(
                field_name,
                status_color,
                self.background_color,
                label,
            )
            check_contrast(
                f"{field_name.removesuffix('_color')}_surface_color"
                if explicit_surface
                else field_name,
                status_color,
                status_surface,
                label,
            )

        if errors:
            raise ValidationError(errors)
