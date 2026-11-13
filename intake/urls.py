"""URL configuration for the intake application.

This module defines URL patterns for the intake app,
including the main form intake view.
"""

from django.urls import path

from .views import FormIntakeView

app_name = "intake"

urlpatterns = [
    path("", FormIntakeView.as_view(), name="form_intake"),
]
