"""Admin configuration for employee and work models."""

# mypy: disable-error-code=type-arg

from typing import ClassVar

from django.contrib import admin
from django.db import models, transaction
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import HttpRequest

from .organisation_models import Department, Employee, IssueType
from .work_models import (
    CancellationReason,
    Priority,
    Urgency,
    WorkItem,
    WorkItemComment,
    WorkItemStatus,
    WorkItemStatusHistory,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Admin configuration for departments."""

    list_display = ("name",)
    search_fields = ("name",)


@admin.register(IssueType)
class IssueTypeAdmin(admin.ModelAdmin):
    """Admin configuration for department issue types."""

    list_display = ("name", "code", "department")
    list_filter = ("department",)
    search_fields = ("name", "code", "department__name")


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    """Admin configuration for employee profiles."""

    list_display = ("name", "email", "department", "manager", "user")
    list_filter = ("department",)
    search_fields = ("name", "email", "user__username", "user__email")
    actions = ("deactivate_and_anonymize",)

    @admin.action(description="Deactivate and anonymize selected employees")
    def deactivate_and_anonymize(
        self,
        request: HttpRequest,
        queryset: QuerySet[Employee],
    ) -> None:
        """Deactivate selected accounts and clear their contact details."""
        for employee in queryset:
            employee.deactivate_and_anonymize()

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: Employee | None = None,
    ) -> bool:
        """Keep employee records for attribution."""
        return False


class FixedOptionAdmin(admin.ModelAdmin):
    """Allow label edits while keeping seeded option codes fixed."""

    list_display = ("code", "label")
    list_editable = ("label",)
    ordering = ("code",)
    readonly_fields: ClassVar[tuple[str, ...]] = ("code",)

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Prevent creation of option values outside the seed migration."""
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,
        obj: models.Model | None = None,
    ) -> bool:
        """Prevent deletion of fixed option values."""
        return False


@admin.register(Priority)
class PriorityAdmin(FixedOptionAdmin):
    """Admin configuration for priority labels."""

    readonly_fields: ClassVar[tuple[str, ...]] = ("code", "guidance")


@admin.register(Urgency)
class UrgencyAdmin(FixedOptionAdmin):
    """Admin configuration for urgency labels."""

    readonly_fields: ClassVar[tuple[str, ...]] = ("code", "guidance")


@admin.register(WorkItemStatus)
@admin.register(CancellationReason)
class WorkOptionAdmin(FixedOptionAdmin):
    """Admin configuration for other fixed work options."""


@admin.register(WorkItem)
class WorkItemAdmin(admin.ModelAdmin):
    """Admin configuration that records status changes in history."""

    list_display = ("id", "issue_type", "priority", "urgency", "status", "created_at")
    list_filter = ("status", "priority", "urgency", "issue_type__department")
    search_fields = ("issue_type__name", "issue_type__code")
    readonly_fields = ("created_at", "ended_at")

    @transaction.atomic
    def save_model(
        self,
        request: HttpRequest,
        obj: WorkItem,
        form: ModelForm[WorkItem],
        change: bool,
    ) -> None:
        """Record admin status edits through the transition operation."""
        if not change:
            super().save_model(request, obj, form, change)
            return

        current = WorkItem.objects.select_related("status").get(pk=obj.pk)
        if current.status_id == obj.status_id:
            super().save_model(request, obj, form, change)
            return

        target_status = obj.status
        cancellation_reason = obj.cancellation_reason
        cancellation_notes = obj.cancellation_notes
        employee = None
        if request.user.is_authenticated and request.user.pk is not None:
            employee = Employee.objects.filter(user_id=request.user.pk).first()
        current.transition_to(
            target_status,
            changed_by=employee,
            cancellation_reason=cancellation_reason,
            cancellation_notes=cancellation_notes,
        )

        transition_fields = {
            "status",
            "ended_at",
            "cancellation_reason",
            "cancellation_notes",
            "cancelled_by",
            "created_at",
            "id",
        }
        for field in obj._meta.concrete_fields:
            if field.name not in transition_fields:
                setattr(current, field.name, getattr(obj, field.name))
        current.save()
        obj.refresh_from_db()


@admin.register(WorkItemStatusHistory)
class WorkItemStatusHistoryAdmin(admin.ModelAdmin):
    """Read-only status history in the admin."""

    list_display = (
        "work_item",
        "previous_status",
        "new_status",
        "changed_by",
        "changed_at",
    )
    list_filter = ("new_status", "changed_at")
    readonly_fields = (
        "work_item",
        "changed_by",
        "previous_status",
        "new_status",
        "changed_at",
        "notes",
    )

    def has_add_permission(self, request: HttpRequest) -> bool:
        """Keep history creation tied to status transitions."""
        return False

    def has_change_permission(
        self,
        request: HttpRequest,
        obj: WorkItemStatusHistory | None = None,
    ) -> bool:
        """Keep recorded status transitions immutable."""
        return False


@admin.register(WorkItemComment)
class WorkItemCommentAdmin(admin.ModelAdmin):
    """Admin configuration for internal comments."""

    list_display = ("work_item", "author", "created_at")
    list_filter = ("created_at",)
    search_fields = ("content", "author__name")
