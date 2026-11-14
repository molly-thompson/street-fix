"""Shared fixtures for the test suite."""

from collections.abc import Callable
from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model

from employees.organisation_models import Department, Employee, IssueType
from employees.work_models import Priority, Urgency, WorkItem, WorkItemStatus
from site_settings.models import ThemeSettings


@pytest.fixture
def theme_settings(db: None) -> ThemeSettings:
    """Provide the persisted site theme singleton."""
    return ThemeSettings.objects.create()


@pytest.fixture
def make_employee(db: None) -> Callable[..., Employee]:
    """Provide a factory for employees with linked user accounts."""

    def make(username: str = "officer", department: str = "Roads") -> Employee:
        dept, _ = Department.objects.get_or_create(name=department)
        user = get_user_model().objects.create_user(
            username=username,
            email=f"{username}@example.com",
        )
        return Employee.objects.create(
            user=user,
            department=dept,
            email=f"{username}@example.com",
            name=username.title(),
        )

    return make


@pytest.fixture
def make_work_item(db: None) -> Callable[..., WorkItem]:
    """Provide a factory for submitted work items."""

    def make(issue_code: str = "POTHOLE", department: str = "Roads") -> WorkItem:
        dept, _ = Department.objects.get_or_create(name=department)
        issue_type, _ = IssueType.objects.get_or_create(
            department=dept,
            code=issue_code,
            defaults={"name": issue_code.replace("_", " ").title()},
        )
        return WorkItem.objects.create(
            issue_type=issue_type,
            latitude=Decimal("51.500000"),
            longitude=Decimal("-0.120000"),
            priority=Priority.objects.get(code="NORMAL"),
            urgency=Urgency.objects.get(code="ROUTINE"),
            status=WorkItemStatus.objects.get(code="SUBMITTED"),
        )

    return make
