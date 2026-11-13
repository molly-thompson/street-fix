"""Admin configuration for public reporting models."""

# mypy: disable-error-code=type-arg

from django.contrib import admin
from django.http import HttpRequest

from intake.models import (
    ContactMethod,
    Reporter,
    ReportSubmission,
    ReportSubmissionPhoto,
)


@admin.register(ContactMethod)
class ContactMethodAdmin(admin.ModelAdmin):
    """Allow label edits while keeping seeded contact methods fixed."""

    list_display = ("code", "label")
    list_editable = ("label",)
    ordering = ("code",)
    readonly_fields = ("code",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Prevent creation of contact methods outside the seed migration."""
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: ContactMethod | None = None,
    ) -> bool:
        """Prevent deletion of fixed contact methods."""
        return False


@admin.register(Reporter)
class ReporterAdmin(admin.ModelAdmin):
    """Admin configuration for reporter contact details."""

    list_display = ("name", "email", "telephone")
    search_fields = ("name", "email", "telephone")


@admin.register(ReportSubmission)
class ReportSubmissionAdmin(admin.ModelAdmin):
    """Admin configuration for report submissions."""

    list_display = (
        "id",
        "work_item",
        "reporter",
        "contact_method",
        "updates_requested",
        "submitted_at",
    )
    list_filter = ("contact_method", "updates_requested", "submitted_at")
    search_fields = ("description", "reporter__name", "reporter__email")
    readonly_fields = ("submitted_at",)


@admin.register(ReportSubmissionPhoto)
class ReportSubmissionPhotoAdmin(admin.ModelAdmin):
    """Admin configuration for report photos."""

    list_display = ("report_submission", "image_url", "uploaded_at")
    readonly_fields = ("uploaded_at",)
