"""Tests for employees application views."""

import pytest
from django.test import Client
from django.urls import resolve, reverse

from employees.views import EmployeeDashboardView

pytestmark = pytest.mark.django_db


def test_employee_dashboard_view_url_exists_at_desired_location(
    client: Client,
) -> None:
    """Test that the employee dashboard view is accessible at /employees/."""
    response = client.get("/employees/")

    assert response.status_code == 200


def test_employee_dashboard_view_url_accessible_by_name(client: Client) -> None:
    """Test that the employee dashboard view is accessible by its URL name."""
    response = client.get(reverse("employees:dashboard"))

    assert response.status_code == 200


def test_employee_dashboard_view_uses_correct_template(client: Client) -> None:
    """Test that the employee dashboard view uses the correct template."""
    response = client.get(reverse("employees:dashboard"))

    assert any(
        template.name == "employees/dashboard.html" for template in response.templates
    )


def test_employee_dashboard_view_extends_base_template(client: Client) -> None:
    """Test that the employee dashboard template extends base.html."""
    response = client.get(reverse("employees:dashboard"))

    assert any(template.name == "base.html" for template in response.templates)


def test_employee_dashboard_view_resolves_to_correct_view_class() -> None:
    """Test that the URL resolves to the EmployeeDashboardView class."""
    resolver_match = resolve("/employees/")

    assert getattr(resolver_match.func, "view_class", None) is EmployeeDashboardView


def test_employee_dashboard_view_context_contains_expected_content(
    client: Client,
) -> None:
    """Test that the response contains expected content."""
    response = client.get(reverse("employees:dashboard"))
    content = response.content.decode()

    assert "Employee Dashboard" in content
    assert "Welcome to the Employee Dashboard" in content
