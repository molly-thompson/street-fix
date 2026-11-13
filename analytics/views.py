"""Views for the analytics application.

This module contains views for analytics dashboards,
reporting, metrics, and data visualization.
"""

from django.views.generic import TemplateView


class AnalyticsOverview(TemplateView):
    """View for the analytics overview dashboard.

    Displays key metrics, charts, and summary statistics
    for data analysis and reporting purposes.
    """

    template_name = "analytics/overview.html"
