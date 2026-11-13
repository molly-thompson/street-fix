"""Views for the intake application.

This module contains views for handling form intake processes
and related functionality.
"""

from django.views.generic import TemplateView


class FormIntakeView(TemplateView):
    """View for the form intake landing page.

    Displays the main intake form or dashboard for submitting
    and managing form submissions.
    """

    template_name = "intake/form_intake.html"
