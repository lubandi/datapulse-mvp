"""DataPulse project package."""

# Ensure the Celery app is loaded when Django starts.
from datapulse.celery import app as celery_app

__all__ = ("celery_app",)
