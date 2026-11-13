"""Tests for intake application views."""

import pytest
from django.test import Client
from django.urls import resolve, reverse

from intake.views import FormIntakeView

pytestmark = pytest.mark.django_db


def test_form_intake_view_url_exists_at_desired_location(client: Client) -> None:
    """Test that the form intake view is accessible at the root URL."""
    response = client.get("/")

    assert response.status_code == 200


def test_form_intake_view_url_accessible_by_name(client: Client) -> None:
    """Test that the form intake view is accessible by its URL name."""
    response = client.get(reverse("intake:form_intake"))

    assert response.status_code == 200


def test_form_intake_view_uses_correct_template(client: Client) -> None:
    """Test that the form intake view uses the correct template."""
    response = client.get(reverse("intake:form_intake"))

    assert any(
        template.name == "intake/form_intake.html" for template in response.templates
    )


def test_form_intake_view_extends_base_template(client: Client) -> None:
    """Test that the form intake template extends base.html."""
    response = client.get(reverse("intake:form_intake"))

    assert any(template.name == "base.html" for template in response.templates)


def test_base_template_loads_ui_kit_before_runtime_theme(client: Client) -> None:
    """Test the base template loads UIkit before the theme overrides."""
    response = client.get(reverse("intake:form_intake"))
    content = response.content.decode()

    assert "uikit/uikit.min" in content
    assert "css/new-theme" in content
    assert content.index("uikit/uikit.min") < content.index("css/new-theme")


def test_form_intake_view_resolves_to_correct_view_class() -> None:
    """Test that the URL resolves to the FormIntakeView class."""
    resolver_match = resolve("/")

    assert getattr(resolver_match.func, "view_class", None) is FormIntakeView


def test_form_intake_view_context_contains_expected_content(client: Client) -> None:
    """Test that the response contains expected content."""
    response = client.get(reverse("intake:form_intake"))
    content = response.content.decode()

    assert "Form Intake" in content
    assert "Welcome to the Form Intake System" in content
