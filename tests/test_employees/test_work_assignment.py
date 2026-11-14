"""Tests for work assignment history."""

from datetime import timedelta
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from employees.organisation_models import Department, Employee, IssueType
from employees.work_models import (
    Priority,
    Urgency,
    WorkAssignment,
    WorkItem,
    WorkItemStatus,
)

pytestmark = pytest.mark.django_db


def make_employee(username: str) -> Employee:
    """Create an employee in the Roads department."""
    department, _ = Department.objects.get_or_create(name="Roads")
    user = get_user_model().objects.create_user(
        username=username,
        email=f"{username}@example.com",
    )
    return Employee.objects.create(
        user=user,
        department=department,
        email=f"{username}@example.com",
        name=username.title(),
    )


def make_work_item() -> WorkItem:
    """Create a submitted pothole work item."""
    department, _ = Department.objects.get_or_create(name="Roads")
    issue_type, _ = IssueType.objects.get_or_create(
        department=department,
        code="POTHOLE",
        defaults={"name": "Pothole"},
    )
    return WorkItem.objects.create(
        issue_type=issue_type,
        latitude=Decimal("51.500000"),
        longitude=Decimal("-0.120000"),
        priority=Priority.objects.get(code="NORMAL"),
        urgency=Urgency.objects.get(code="ROUTINE"),
        status=WorkItemStatus.objects.get(code="SUBMITTED"),
    )


def test_assign_creates_open_assignment() -> None:
    """Assigning gives the work item a current owner."""
    item = make_work_item()
    officer = make_employee("priya")
    manager = make_employee("manager")

    assignment = WorkAssignment.assign(item, officer, assigned_by=manager)

    assert assignment.is_open
    assert assignment.assigned_by == manager
    assert list(officer.work_assignments.all()) == [assignment]


def test_reassign_closes_previous_and_keeps_history() -> None:
    """Reassigning ends the old row and adds a new one."""
    item = make_work_item()
    priya = make_employee("priya")
    dan = make_employee("dan")

    first = WorkAssignment.assign(item, priya)
    second = WorkAssignment.assign(item, dan, reason="Priya off sick")
    first.refresh_from_db()

    assert not first.is_open
    assert first.reason == "Priya off sick"
    assert second.is_open
    assert list(item.assignments.all()) == [first, second]


def test_assigning_same_employee_again_is_a_no_op() -> None:
    """Repeating an assignment does not duplicate history."""
    item = make_work_item()
    priya = make_employee("priya")

    first = WorkAssignment.assign(item, priya)
    again = WorkAssignment.assign(item, priya)

    assert again.pk == first.pk
    assert item.assignments.count() == 1


def test_release_ends_assignment() -> None:
    """Releasing leaves the work item unassigned."""
    item = make_work_item()
    assignment = WorkAssignment.assign(item, make_employee("priya"))

    assignment.release(reason="Re-triaged")

    assert not assignment.is_open
    assert assignment.reason == "Re-triaged"
    assert not item.assignments.filter(unassigned_at__isnull=True).exists()


def test_only_one_open_assignment_per_work_item() -> None:
    """The database rejects a second open assignment."""
    item = make_work_item()
    WorkAssignment.objects.create(work_item=item, employee=make_employee("priya"))

    with pytest.raises(IntegrityError), transaction.atomic():
        WorkAssignment.objects.create(work_item=item, employee=make_employee("dan"))


def test_assignment_cannot_end_before_it_starts() -> None:
    """The database rejects an end time earlier than the start."""
    now = timezone.now()

    with pytest.raises(IntegrityError), transaction.atomic():
        WorkAssignment.objects.create(
            work_item=make_work_item(),
            employee=make_employee("priya"),
            assigned_at=now,
            unassigned_at=now - timedelta(minutes=1),
        )
