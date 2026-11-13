"""Tests for admin-managed work item transitions."""

from decimal import Decimal

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import RequestFactory

from employees.admin import WorkItemAdmin
from employees.organisation_models import Department, Employee, IssueType
from employees.work_models import (
    CancellationReason,
    Priority,
    Urgency,
    WorkItem,
    WorkItemStatus,
)


def test_admin_status_change_uses_transition_operation(db: None) -> None:
    """Admin cancellation records its actor and cancellation details."""
    department = Department.objects.create(name="Roads")
    user = get_user_model().objects.create_user(username="employee")
    employee = Employee.objects.create(
        user=user,
        department=department,
        name="Roads Employee",
    )
    issue_type = IssueType.objects.create(
        department=department,
        name="Pothole",
        code="POTHOLE",
    )
    item = WorkItem.objects.create(
        issue_type=issue_type,
        latitude=Decimal("51.500000"),
        longitude=Decimal("-0.120000"),
        priority=Priority.objects.get(code="NORMAL"),
        urgency=Urgency.objects.get(code="ROUTINE"),
        status=WorkItemStatus.objects.get(code="SUBMITTED"),
    )
    item.status = WorkItemStatus.objects.get(code="CANCELLED")
    item.cancellation_reason = CancellationReason.objects.get(code="OTHER")
    item.cancellation_notes = "The request is outside the service area."

    request = RequestFactory().post("/admin/employees/workitem/")
    request.user = employee.user
    work_item_admin = WorkItemAdmin(WorkItem, admin.site)
    form = work_item_admin.get_form(request)(instance=item)

    work_item_admin.save_model(request, item, form, change=True)
    item.refresh_from_db()

    history = item.status_history.get()
    assert history.changed_by == employee
    assert history.new_status.code == "CANCELLED"
    assert item.ended_at is not None
    assert item.cancellation_notes == "The request is outside the service area."
