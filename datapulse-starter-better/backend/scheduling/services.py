"""Core check runner service — shared logic used by views and Celery tasks."""

from django.utils import timezone

from checks.models import CheckResult, QualityScore
from checks.services.validation_engine import ValidationEngine
from checks.services.scoring_service import calculate_quality_score
from datasets.models import Dataset, DatasetFile
from datasets.services.file_parser import parse_csv, parse_json
from rules.models import ValidationRule
from scheduling.models import AuditLog


def run_checks_for_dataset(dataset, user=None, action="CHECK_RUN"):
    """Run all applicable quality checks on a dataset and return results.

    This is the shared logic used by:
    - POST /api/checks/run/{id}  (single check)
    - POST /api/scheduling/batch  (batch check)
    - Celery scheduled task       (cron check)

    Returns:
        dict with keys: score, total_rules, passed_rules, failed_rules, status
    """
    # Get file
    dataset_file = DatasetFile.objects.filter(dataset=dataset).first()
    if not dataset_file:
        return {"error": "No file associated with this dataset", "status": "ERROR"}

    # Parse
    try:
        if dataset.file_type == "csv":
            metadata = parse_csv(dataset_file.file_path)
        else:
            metadata = parse_json(dataset_file.file_path)
        df = metadata["dataframe"]
    except Exception as e:
        return {"error": f"Failed to parse file: {e}", "status": "ERROR"}

    # Fetch rules
    from django.db.models import Q
    rules = list(
        ValidationRule.objects.filter(is_active=True).filter(
            Q(dataset_type=dataset.file_type) | Q(dataset_type="") | Q(dataset_type__isnull=True)
        )
    )

    if not rules:
        score_record = QualityScore.objects.create(
            dataset=dataset, score=100.0, total_rules=0, passed_rules=0, failed_rules=0
        )
        dataset.status = "VALIDATED"
        dataset.save()
        _create_audit_log(user, action, dataset, 100.0, "No rules defined — perfect score")
        return {
            "score": 100.0, "total_rules": 0, "passed_rules": 0,
            "failed_rules": 0, "status": "VALIDATED", "quality_score_id": score_record.id,
        }

    # Run checks
    engine = ValidationEngine()
    results = engine.run_all_checks(df, rules)

    # Persist results
    check_records = []
    for result in results:
        check_records.append(
            CheckResult(
                dataset=dataset,
                rule_id=result["rule_id"],
                passed=result["passed"],
                failed_rows=result["failed_rows"],
                total_rows=result["total_rows"],
                details=result.get("details", ""),
            )
        )
    CheckResult.objects.bulk_create(check_records)

    # Score
    score_data = calculate_quality_score(results, rules)

    score_record = QualityScore.objects.create(
        dataset=dataset,
        score=score_data["score"],
        total_rules=score_data["total_rules"],
        passed_rules=score_data["passed_rules"],
        failed_rules=score_data["failed_rules"],
    )

    # Update status
    new_status = "VALIDATED" if score_data["score"] >= 50 else "FAILED"
    dataset.status = new_status
    dataset.save()

    # Audit
    _create_audit_log(
        user, action, dataset, score_data["score"],
        f"Score: {score_data['score']}% | Passed: {score_data['passed_rules']}/{score_data['total_rules']}"
    )

    return {
        "score": score_data["score"],
        "total_rules": score_data["total_rules"],
        "passed_rules": score_data["passed_rules"],
        "failed_rules": score_data["failed_rules"],
        "status": new_status,
        "quality_score_id": score_record.id,
    }


def _create_audit_log(user, action, dataset, score, details):
    """Helper to create an audit log entry."""
    AuditLog.objects.create(
        user=user,
        action=action,
        dataset=dataset,
        score=score,
        details=details,
    )
