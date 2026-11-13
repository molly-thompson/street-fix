"""Work item, lifecycle, and work-option models."""

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils import timezone

from .organisation_models import Employee, IssueType


class WorkOption(models.Model):
    """A fixed-code option with an administrator-editable label."""

    code = models.CharField(max_length=40, unique=True, editable=False)
    label = models.CharField(max_length=100)

    class Meta:
        """Share option ordering across work lookup tables."""

        abstract = True
        ordering = ("code",)

    def __str__(self) -> str:
        """Return the configurable label."""
        return self.label


class Priority(WorkOption):
    """Operational impact of an issue."""

    guidance = models.TextField()


class Urgency(WorkOption):
    """Time sensitivity of an issue."""

    guidance = models.TextField()


class WorkItemStatus(WorkOption):
    """A stage in the work item's operational lifecycle."""


class CancellationReason(WorkOption):
    """A structured reason for cancelling a work item."""


class WorkItem(models.Model):
    """An internal work item that may have one or more public submissions."""

    issue_type = models.ForeignKey(
        IssueType,
        on_delete=models.PROTECT,
        related_name="work_items",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.PROTECT,
        related_name="work_items",
    )
    urgency = models.ForeignKey(
        Urgency,
        on_delete=models.PROTECT,
        related_name="work_items",
    )
    status = models.ForeignKey(
        WorkItemStatus,
        on_delete=models.PROTECT,
        related_name="work_items",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    cancellation_reason = models.ForeignKey(
        CancellationReason,
        on_delete=models.PROTECT,
        related_name="cancelled_work_items",
        null=True,
        blank=True,
    )
    cancellation_notes = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        related_name="cancelled_work_items",
        null=True,
        blank=True,
    )

    class Meta:
        """Sort work items by most recent creation time."""

        ordering = ("-created_at",)

    def __str__(self) -> str:
        """Return a concise work item identifier."""
        return f"Work item {self.pk}"

    def clean(self) -> None:
        """Validate end-state and cancellation fields."""
        super().clean()
        if not self.status_id:
            return

        status_code = self.status.code
        is_ended = status_code in {"CLOSED", "CANCELLED"}
        errors: dict[str, str] = {}

        if not is_ended and self.ended_at is not None:
            errors["ended_at"] = "Only closed or cancelled work can have an end time."

        if status_code == "CANCELLED":
            reason = self.cancellation_reason
            if not self.cancellation_reason_id or reason is None:
                errors["cancellation_reason"] = (
                    "A cancellation reason is required for cancelled work."
                )
            elif reason.code == "OTHER" and not self.cancellation_notes.strip():
                errors["cancellation_notes"] = (
                    "Add notes when the cancellation reason is Other."
                )
        elif (
            self.cancellation_reason_id
            or self.cancellation_notes
            or self.cancelled_by_id
        ):
            errors["cancellation_reason"] = (
                "Cancellation details are only valid for cancelled work."
            )

        if errors:
            raise ValidationError(errors)

    @transaction.atomic
    def transition_to(
        self,
        new_status: WorkItemStatus,
        *,
        changed_by: Employee | None = None,
        notes: str = "",
        cancellation_reason: CancellationReason | None = None,
        cancellation_notes: str = "",
    ) -> None:
        """Change status and record the transition atomically."""
        if self.pk is None:
            raise ValueError("A work item must be saved before changing its status.")

        current = (
            WorkItem.objects.select_for_update()
            .select_related("status")
            .get(pk=self.pk)
        )
        if current.status_id == new_status.pk:
            return
        if current.status.code in {"CLOSED", "CANCELLED"}:
            raise ValidationError("Closed or cancelled work cannot be reopened.")

        previous_status = current.status
        current.status = new_status
        current.ended_at = (
            timezone.now() if new_status.code in {"CLOSED", "CANCELLED"} else None
        )
        if new_status.code == "CANCELLED":
            current.cancellation_reason = cancellation_reason
            current.cancellation_notes = cancellation_notes
            current.cancelled_by = changed_by
        else:
            current.cancellation_reason = None
            current.cancellation_notes = ""
            current.cancelled_by = None

        current.full_clean()
        current.save(
            update_fields=(
                "status",
                "ended_at",
                "cancellation_reason",
                "cancellation_notes",
                "cancelled_by",
            )
        )
        WorkItemStatusHistory.objects.create(
            work_item=current,
            changed_by=changed_by,
            previous_status=previous_status,
            new_status=new_status,
            notes=notes,
        )
        self.refresh_from_db()


class WorkItemStatusHistory(models.Model):
    """A recorded transition between work item statuses."""

    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.PROTECT,
        related_name="status_history",
    )
    changed_by = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        related_name="status_changes",
        null=True,
        blank=True,
    )
    previous_status = models.ForeignKey(
        WorkItemStatus,
        on_delete=models.PROTECT,
        related_name="previous_status_changes",
    )
    new_status = models.ForeignKey(
        WorkItemStatus,
        on_delete=models.PROTECT,
        related_name="new_status_changes",
    )
    changed_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        """List status transitions in chronological order."""

        ordering = ("changed_at", "pk")

    def __str__(self) -> str:
        """Describe the recorded transition."""
        return f"{self.previous_status} -> {self.new_status}"


class WorkItemComment(models.Model):
    """An internal comment on a work item."""

    work_item = models.ForeignKey(
        WorkItem,
        on_delete=models.PROTECT,
        related_name="comments",
    )
    author = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        related_name="work_item_comments",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        """List comments in chronological order."""

        ordering = ("created_at", "pk")

    def __str__(self) -> str:
        """Identify the commented work item."""
        return f"Comment on work item {self.work_item_id}"
