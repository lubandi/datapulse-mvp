"""Report service - IMPLEMENTED."""

from datetime import timedelta

from checks.models import CheckResult, QualityScore
from datasets.models import Dataset
from django.utils import timezone


def generate_report(dataset_id: int) -> dict:
    """Generate a quality report for a dataset.

    Fetches dataset info, latest score, and all check results from the latest run.
    Returns a report dict ready for serialization.
    """
    try:
        dataset = Dataset.objects.get(id=dataset_id)
    except Dataset.DoesNotExist:
        return None

    # Get the latest quality score
    latest_score = QualityScore.objects.filter(dataset=dataset).order_by("-checked_at").first()

    if not latest_score:
        return {
            "dataset_id": dataset.id,
            "dataset_name": dataset.name,
            "score": 0.0,
            "total_rules": 0,
            "results": [],
            "checked_at": None,
        }

    # Fetch check results from the latest run (same checked_at timestamp window)
    results = (
        CheckResult.objects.filter(
            dataset=dataset,
            checked_at__gte=latest_score.checked_at - timedelta(seconds=5),
        )
        .select_related("dataset", "rule")
        .order_by("-checked_at")
    )

    return {
        "dataset_id": dataset.id,
        "dataset_name": dataset.name,
        "score": latest_score.score,
        "total_rules": latest_score.total_rules,
        "results": results,
        "checked_at": latest_score.checked_at,
    }


def get_trend_data(days: int = 30, user=None) -> list:
    """Get quality score trend data over a given number of days.

    Returns a list of QualityScore records ordered by date, with dataset info.
    Filters by the dataset owner (uploaded_by) unless user is ADMIN.
    """
    start_date = timezone.now() - timedelta(days=days)
    queryset = QualityScore.objects.filter(checked_at__gte=start_date)

    if user and getattr(user, "role", "USER") != "ADMIN":
        queryset = queryset.filter(dataset__uploaded_by=user)

    scores = queryset.select_related("dataset").order_by("checked_at")
    return scores
