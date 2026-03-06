"""Scheduling & Notifications app — Models for audit log, alert config, and schedule config."""

from django.db import models


class AuditLog(models.Model):
    """Track all quality check runs and results."""

    ACTION_CHOICES = [
        ("CHECK_RUN", "Quality Check Run"),
        ("BATCH_RUN", "Batch Check Run"),
        ("SCHEDULED_RUN", "Scheduled Check Run"),
        ("RULE_CREATED", "Rule Created"),
        ("RULE_UPDATED", "Rule Updated"),
        ("RULE_DELETED", "Rule Deleted"),
    ]

    user = models.ForeignKey(
        "authentication.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    dataset = models.ForeignKey(
        "datasets.Dataset", on_delete=models.SET_NULL, null=True, blank=True
    )
    details = models.TextField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "audit_logs"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.action} on {self.created_at}"


class AlertConfig(models.Model):
    """Configuration for quality score alerts."""

    dataset = models.ForeignKey(
        "datasets.Dataset", on_delete=models.CASCADE, null=True, blank=True,
        help_text="If null, applies to all datasets as the global default."
    )
    threshold = models.FloatField(
        default=70.0,
        help_text="Alert when quality score drops below this value (0-100)."
    )
    email_recipients = models.TextField(
        help_text="Comma-separated list of email addresses to notify."
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "alert_configs"

    def __str__(self):
        target = self.dataset.name if self.dataset else "Global"
        return f"Alert: {target} < {self.threshold}"


class ScheduleConfig(models.Model):
    """Configuration for scheduled quality checks."""

    FREQUENCY_CHOICES = [
        ("HOURLY", "Every hour"),
        ("DAILY", "Every day"),
        ("WEEKLY", "Every week"),
        ("MONTHLY", "Every month"),
    ]

    dataset = models.ForeignKey(
        "datasets.Dataset", on_delete=models.CASCADE,
        help_text="Dataset to run scheduled checks on."
    )
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES, default="DAILY")
    is_active = models.BooleanField(default=True)
    last_run_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "schedule_configs"

    def __str__(self):
        return f"Schedule: {self.dataset.name} ({self.frequency})"
