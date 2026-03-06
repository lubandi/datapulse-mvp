"""Scheduling URL configuration."""

from django.urls import path
from scheduling.views import (
    BatchCheckView,
    AuditLogListView,
    AlertConfigListCreateView,
    AlertConfigDetailView,
    ScheduleConfigListCreateView,
    ScheduleConfigDetailView,
)

urlpatterns = [
    # Batch processing
    path("batch", BatchCheckView.as_view(), name="scheduling-batch"),

    # Audit log
    path("audit", AuditLogListView.as_view(), name="scheduling-audit"),

    # Alert configurations
    path("alerts", AlertConfigListCreateView.as_view(), name="scheduling-alerts"),
    path("alerts/<int:config_id>", AlertConfigDetailView.as_view(), name="scheduling-alerts-detail"),

    # Schedule configurations
    path("schedules", ScheduleConfigListCreateView.as_view(), name="scheduling-schedules"),
    path("schedules/<int:config_id>", ScheduleConfigDetailView.as_view(), name="scheduling-schedules-detail"),
]
