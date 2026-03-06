"""Celery tasks for scheduled quality checks and notifications."""

import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="scheduling.tasks.run_scheduled_checks")
def run_scheduled_checks():
    """Run quality checks on all datasets with active schedules.

    This task is triggered by django-celery-beat at the configured interval.
    It processes all active ScheduleConfig entries whose frequency has elapsed.
    """
    from scheduling.models import ScheduleConfig
    from scheduling.services import run_checks_for_dataset
    from scheduling.notifications import check_and_notify
    from datetime import timedelta

    FREQUENCY_DELTAS = {
        "HOURLY": timedelta(hours=1),
        "DAILY": timedelta(days=1),
        "WEEKLY": timedelta(weeks=1),
        "MONTHLY": timedelta(days=30),
    }

    active_schedules = ScheduleConfig.objects.filter(is_active=True).select_related("dataset")
    now = timezone.now()

    for schedule in active_schedules:
        delta = FREQUENCY_DELTAS.get(schedule.frequency, timedelta(days=1))

        # Skip if last run was too recent
        if schedule.last_run_at and (now - schedule.last_run_at) < delta:
            continue

        logger.info(f"Running scheduled check for dataset: {schedule.dataset.name}")

        result = run_checks_for_dataset(
            dataset=schedule.dataset,
            user=None,
            action="SCHEDULED_RUN",
        )

        # Update last run timestamp
        schedule.last_run_at = now
        schedule.save(update_fields=["last_run_at"])

        # Send notifications if score is below threshold
        if "score" in result:
            check_and_notify(schedule.dataset, result["score"])

        logger.info(
            f"Scheduled check complete for {schedule.dataset.name}: "
            f"score={result.get('score', 'N/A')}"
        )
