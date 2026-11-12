"""URL configuration for the analytics application.

This module defines URL patterns for the analytics app,
including the analytics overview view.
"""

from django.urls import path

from .views import AnalyticsOverview

app_name = "analytics"

urlpatterns = [
    path("", AnalyticsOverview.as_view(), name="overview"),
]
