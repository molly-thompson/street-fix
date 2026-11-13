"""Tests for analytics application views."""

import pytest
from django.test import Client
from django.urls import resolve, reverse

from analytics.views import AnalyticsOverview

pytestmark = pytest.mark.django_db


def test_analytics_overview_view_url_exists_at_desired_location(
    client: Client,
) -> None:
    """Test that the analytics overview view is accessible at /analytics/."""
    response = client.get("/analytics/")

    assert response.status_code == 200


def test_analytics_overview_view_url_accessible_by_name(client: Client) -> None:
    """Test that the analytics overview view is accessible by its URL name."""
    response = client.get(reverse("analytics:overview"))

    assert response.status_code == 200


def test_analytics_overview_view_uses_correct_template(client: Client) -> None:
    """Test that the analytics overview view uses the correct template."""
    response = client.get(reverse("analytics:overview"))

    assert any(
        template.name == "analytics/overview.html" for template in response.templates
    )


def test_analytics_overview_view_extends_base_template(client: Client) -> None:
    """Test that the analytics overview template extends base.html."""
    response = client.get(reverse("analytics:overview"))

    assert any(template.name == "base.html" for template in response.templates)


def test_analytics_overview_view_resolves_to_correct_view_class() -> None:
    """Test that the URL resolves to the AnalyticsOverview class."""
    resolver_match = resolve("/analytics/")

    assert getattr(resolver_match.func, "view_class", None) is AnalyticsOverview


def test_analytics_overview_view_context_contains_expected_content(
    client: Client,
) -> None:
    """Test that the response contains expected content."""
    response = client.get(reverse("analytics:overview"))
    content = response.content.decode()

    assert "Analytics Overview" in content
    assert "Welcome to the Analytics Overview" in content
