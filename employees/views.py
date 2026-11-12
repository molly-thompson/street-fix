"""Views for the employees application.

This module contains views for employee management,
dashboards, and related functionality.
"""

from django.views.generic import TemplateView


class EmployeeDashboardView(TemplateView):
    """View for the employee dashboard.

    Displays an overview of employee information, tasks,
    and relevant metrics for employee management.
    """

    template_name = "employees/dashboard.html"
