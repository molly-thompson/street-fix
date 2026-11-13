"""Tests for public reporting models."""

from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db.models.deletion import ProtectedError

from employees.organisation_models import Department, IssueType
from employees.work_models import Priority, Urgency, WorkItem, WorkItemStatus
from intake.models import (
    ContactMethod,
    Reporter,
    ReportSubmission,
    ReportSubmissionPhoto,
)

pytestmark = pytest.mark.django_db


def create_work_item() -> WorkItem:
    """Create a work item for report submission tests."""
    department = Department.objects.create(name="Roads")
    issue_type = IssueType.objects.create(
        department=department,
        name="Pothole",
        code="POTHOLE",
    )
    return WorkItem.objects.create(
        issue_type=issue_type,
        latitude=Decimal("51.500000"),
        longitude=Decimal("-0.120000"),
        priority=Priority.objects.get(code="NORMAL"),
        urgency=Urgency.objects.get(code="ROUTINE"),
        status=WorkItemStatus.objects.get(code="SUBMITTED"),
    )


def test_contact_methods_are_seeded_and_have_fixed_codes() -> None:
    """The supported contact methods are database rows with fixed codes."""
    assert set(ContactMethod.objects.values_list("code", "label")) == {
        ("EMAIL", "Email"),
        ("TELEPHONE", "Telephone"),
        ("POST", "Post"),
    }
    assert ContactMethod._meta.get_field("code").editable is False


def test_deleting_reporter_preserves_submission_and_clears_reporter_reference() -> None:
    """Removing a reporter leaves their submitted report intact."""
    reporter = Reporter.objects.create(
        name="A Reporter",
        email="reporter@example.com",
    )
    submission = ReportSubmission.objects.create(
        work_item=create_work_item(),
        reporter=reporter,
        contact_method=ContactMethod.objects.get(code="EMAIL"),
        updates_requested=True,
        description="A pothole needs attention.",
    )

    reporter.delete()
    submission.refresh_from_db()

    assert submission.reporter is None
    assert submission.description == "A pothole needs attention."


def test_deleting_submission_cascades_to_photos() -> None:
    """Deleting a report also removes its attached photos."""
    submission = ReportSubmission.objects.create(
        work_item=create_work_item(),
        contact_method=ContactMethod.objects.get(code="EMAIL"),
        updates_requested=False,
        description="A pothole needs attention.",
    )
    photo = ReportSubmissionPhoto.objects.create(
        report_submission=submission,
        image_url="https://example.com/pothole.jpg",
    )

    submission.delete()

    assert not ReportSubmissionPhoto.objects.filter(pk=photo.pk).exists()


def test_deleting_referenced_work_item_or_contact_method_is_protected() -> None:
    """Submissions retain their work item and contact-method references."""
    work_item = create_work_item()
    contact_method = ContactMethod.objects.get(code="EMAIL")
    submission = ReportSubmission.objects.create(
        work_item=work_item,
        contact_method=contact_method,
        updates_requested=False,
        description="A pothole needs attention.",
    )

    with pytest.raises(ProtectedError):
        work_item.delete()

    with pytest.raises(ProtectedError):
        contact_method.delete()

    assert WorkItem.objects.filter(pk=work_item.pk).exists()
    submission.refresh_from_db()
    assert submission.work_item_id == work_item.pk
    assert submission.contact_method_id == contact_method.pk


def test_work_item_transition_fields_are_required_for_cancellation() -> None:
    """The report lifecycle validates cancellation through the work item model."""
    item = create_work_item()
    item.status = WorkItemStatus.objects.get(code="CANCELLED")
    item.ended_at = item.created_at

    with pytest.raises(ValidationError) as error:
        item.full_clean()

    assert "cancellation_reason" in error.value.message_dict
