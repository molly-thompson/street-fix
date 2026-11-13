"""Seed the fixed work item option codes."""

from django.db import migrations


PRIORITIES = (
    ("LOW", "Low", "Minor issue, limited impact"),
    ("NORMAL", "Normal", "Standard maintenance work"),
    ("HIGH", "High", "Significant disruption or impact"),
    ("CRITICAL", "Critical", "Severe impact requiring highest attention"),
)
URGENCIES = (
    ("ROUTINE", "Routine", "Can be handled through normal scheduling"),
    ("SOON", "Soon", "Should be addressed in the near term"),
    ("URGENT", "Urgent", "Requires prompt attention"),
    ("EMERGENCY", "Emergency", "Immediate danger or serious active incident"),
)
STATUSES = (
    ("SUBMITTED", "Submitted"),
    ("TRIAGED", "Triaged"),
    ("ASSIGNED", "Assigned"),
    ("IN_PROGRESS", "In progress"),
    ("AWAITING_INFORMATION", "Awaiting information"),
    ("AWAITING_PARTS", "Awaiting parts"),
    ("ON_HOLD", "On hold"),
    ("RESOLVED", "Resolved"),
    ("CLOSED", "Closed"),
    ("CANCELLED", "Cancelled"),
)
CANCELLATION_REASONS = (
    ("DUPLICATE", "Duplicate report"),
    ("NO_LONGER_REQUIRED", "No longer required"),
    ("WITHDRAWN", "Request withdrawn"),
    ("NOT_MAINTENANCE", "Not a maintenance issue"),
    ("OUT_OF_SCOPE", "Outside our responsibility"),
    ("INVALID_REQUEST", "Invalid or insufficient information"),
    ("OTHER", "Other"),
)


def seed_options(apps, schema_editor):
    """Create the fixed option rows with their default labels and guidance."""
    Priority = apps.get_model("employees", "Priority")
    Urgency = apps.get_model("employees", "Urgency")
    WorkItemStatus = apps.get_model("employees", "WorkItemStatus")
    CancellationReason = apps.get_model("employees", "CancellationReason")

    Priority.objects.bulk_create(
        [
            Priority(code=code, label=label, guidance=guidance)
            for code, label, guidance in PRIORITIES
        ]
    )
    Urgency.objects.bulk_create(
        [
            Urgency(code=code, label=label, guidance=guidance)
            for code, label, guidance in URGENCIES
        ]
    )
    WorkItemStatus.objects.bulk_create(
        [WorkItemStatus(code=code, label=label) for code, label in STATUSES]
    )
    CancellationReason.objects.bulk_create(
        [
            CancellationReason(code=code, label=label)
            for code, label in CANCELLATION_REASONS
        ]
    )


def unseed_options(apps, schema_editor):
    """Remove only the seeded values when reversing this migration."""
    for model_name, rows in (
        ("Priority", PRIORITIES),
        ("Urgency", URGENCIES),
        ("WorkItemStatus", STATUSES),
        ("CancellationReason", CANCELLATION_REASONS),
    ):
        model = apps.get_model("employees", model_name)
        model.objects.filter(code__in=[row[0] for row in rows]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("employees", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_options, unseed_options),
    ]
