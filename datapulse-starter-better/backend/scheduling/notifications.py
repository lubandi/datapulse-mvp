"""Notification service — sends email alerts when quality drops below threshold."""

import logging

from django.core.mail import send_mail
from django.conf import settings

from scheduling.models import AlertConfig

logger = logging.getLogger(__name__)


def check_and_notify(dataset, score):
    """Check if any alert thresholds are breached and send notifications.

    Args:
        dataset: The Dataset instance that was just checked.
        score: The quality score (0-100).
    """
    # Get dataset-specific + global configs
    dataset_configs = AlertConfig.objects.filter(is_active=True, dataset=dataset)
    global_configs = AlertConfig.objects.filter(is_active=True, dataset__isnull=True)
    all_configs = list(dataset_configs) + list(global_configs)

    for config in all_configs:
        if score < config.threshold:
            _send_alert_email(config, dataset, score)


def _send_alert_email(config, dataset, score):
    """Send an alert email for a quality score drop."""
    recipients = [
        email.strip()
        for email in config.email_recipients.split(",")
        if email.strip()
    ]

    if not recipients:
        logger.warning(f"Alert config {config.id} has no valid recipients.")
        return

    subject = f"⚠️ DataPulse Alert: {dataset.name} quality score dropped to {score:.1f}%"
    body = (
        f"Dataset: {dataset.name} (ID: {dataset.id})\n"
        f"Quality Score: {score:.1f}%\n"
        f"Threshold: {config.threshold:.1f}%\n\n"
        f"The quality score has dropped below the configured threshold.\n"
        f"Please review the dataset and its validation results."
    )

    try:
        send_mail(
            subject=subject,
            message=body,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "datapulse@amalitech.com"),
            recipient_list=recipients,
            fail_silently=True,
        )
        logger.info(f"Alert sent to {recipients} for dataset {dataset.name}")
    except Exception as e:
        logger.error(f"Failed to send alert email: {e}")
