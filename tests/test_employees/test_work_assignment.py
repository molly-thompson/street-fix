"""Tests for work assignments, case officers and support."""

from collections.abc import Callable
from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from employees.organisation_models import Employee
from employees.work_models import WorkAssignment, WorkItem

pytestmark = pytest.mark.django_db

MakeEmployee = Callable[..., Employee]
MakeWorkItem = Callable[..., WorkItem]


def open_rows(item: WorkItem) -> list[WorkAssignment]:
    """Return the work item's current assignments."""
    return list(item.assignments.filter(unassigned_at__isnull=True))


def test_assign_makes_case_officer_by_default(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """Assigning gives the work item a responsible case officer."""
    item = make_work_item()
    officer = make_employee("priya")
    manager = make_employee("manager")

    assignment = WorkAssignment.assign(item, officer, assigned_by=manager)

    assert assignment.is_open
    assert assignment.is_case_officer
    assert assignment.assigned_by == manager


def test_support_joins_without_replacing_case_officer(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """A crew can work one item under a single case officer."""
    item = make_work_item()
    lead = WorkAssignment.assign(item, make_employee("priya"))
    helper = WorkAssignment.assign(item, make_employee("dan"), case_officer=False)
    second = WorkAssignment.assign(item, make_employee("sam"), case_officer=False)

    assert open_rows(item) == [lead, helper, second]
    assert [row.is_case_officer for row in open_rows(item)] == [True, False, False]


def test_new_case_officer_closes_previous_and_keeps_history(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """Handing over the case keeps support on and records the change."""
    item = make_work_item()
    priya = WorkAssignment.assign(item, make_employee("priya"))
    helper = WorkAssignment.assign(item, make_employee("dan"), case_officer=False)

    sam = WorkAssignment.assign(item, make_employee("sam"), reason="Priya off sick")
    priya.refresh_from_db()

    assert not priya.is_open
    assert priya.reason == "Priya off sick"
    assert open_rows(item) == [helper, sam]
    assert item.assignments.count() == 3


def test_promoting_support_records_role_change(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """Support becoming case officer closes both old rows."""
    item = make_work_item()
    priya = WorkAssignment.assign(item, make_employee("priya"))
    dan = make_employee("dan")
    as_support = WorkAssignment.assign(item, dan, case_officer=False)

    as_lead = WorkAssignment.assign(item, dan, reason="Priya moved to urgent job")
    priya.refresh_from_db()
    as_support.refresh_from_db()

    assert not priya.is_open
    assert not as_support.is_open
    assert open_rows(item) == [as_lead]
    assert as_lead.is_case_officer


def test_repeating_an_assignment_is_a_no_op(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """Assigning someone to the role they already have changes nothing."""
    item = make_work_item()
    priya = make_employee("priya")

    first = WorkAssignment.assign(item, priya)
    again = WorkAssignment.assign(item, priya)

    assert again.pk == first.pk
    assert item.assignments.count() == 1


def test_release_ends_assignment(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """Releasing takes the employee off the work item."""
    item = make_work_item()
    assignment = WorkAssignment.assign(item, make_employee("priya"))

    assignment.release(reason="Re-triaged")

    assert not assignment.is_open
    assert assignment.reason == "Re-triaged"
    assert open_rows(item) == []


def test_only_one_open_case_officer_per_work_item(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """The database rejects a second open case officer."""
    item = make_work_item()
    WorkAssignment.objects.create(
        work_item=item, employee=make_employee("priya"), is_case_officer=True
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        WorkAssignment.objects.create(
            work_item=item, employee=make_employee("dan"), is_case_officer=True
        )


def test_employee_cannot_hold_two_open_rows_on_one_item(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """The database rejects the same person on the same job twice."""
    item = make_work_item()
    priya = make_employee("priya")
    WorkAssignment.objects.create(work_item=item, employee=priya)

    with pytest.raises(IntegrityError), transaction.atomic():
        WorkAssignment.objects.create(work_item=item, employee=priya)


def test_assignment_cannot_end_before_it_starts(
    make_employee: MakeEmployee, make_work_item: MakeWorkItem
) -> None:
    """The database rejects an end time earlier than the start."""
    now = timezone.now()

    with pytest.raises(IntegrityError), transaction.atomic():
        WorkAssignment.objects.create(
            work_item=make_work_item(),
            employee=make_employee("priya"),
            assigned_at=now,
            unassigned_at=now - timedelta(minutes=1),
        )
