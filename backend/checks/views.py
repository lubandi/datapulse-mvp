"""Quality checks router - IMPLEMENTED."""

from checks.models import CheckResult, QualityScore
from checks.serializers import CheckResultResponseSerializer, QualityScoreResponseSerializer
from checks.services.scoring_service import calculate_quality_score
from checks.services.validation_engine import ValidationEngine
from datapulse.exceptions import DatasetNotFoundException, QualityCheckFailedException
from datasets.models import Dataset, DatasetFile
from datasets.services.file_parser import parse_csv, parse_json
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rules.models import ValidationRule


class RunChecksView(APIView):
    """Run all applicable validation checks on a dataset."""

    @extend_schema(
        responses={200: QualityScoreResponseSerializer},
        tags=["Checks"],
        summary="Run quality checks on a dataset",
    )
    def post(self, request, dataset_id):
        """Run all applicable validation checks on a dataset.

        Steps:
        1. Fetch dataset by ID (404 if not found)
        2. Get DatasetFile, read file path
        3. Load file with file_parser (parse_csv or parse_json)
        4. Fetch active ValidationRules matching dataset type
        5. Init ValidationEngine, call run_all_checks(df, rules)
        6. Create CheckResult records for each check
        7. Calculate quality score via scoring_service
        8. Create QualityScore record
        9. Update dataset status (VALIDATED or FAILED)
        10. Return score and results summary
        """
        # 1. Fetch dataset
        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                dataset = Dataset.objects.get(id=dataset_id)
            else:
                dataset = Dataset.objects.get(id=dataset_id, uploaded_by=request.user)
        except Dataset.DoesNotExist:
            raise DatasetNotFoundException(f"Dataset with id {dataset_id} not found")

        # 2. Get file path
        dataset_file = DatasetFile.objects.filter(dataset=dataset).first()
        if not dataset_file:
            raise QualityCheckFailedException("No file associated with this dataset")

        # 3. Parse file
        try:
            if dataset.file_type == "csv":
                metadata = parse_csv(dataset_file.file_path)
            else:
                metadata = parse_json(dataset_file.file_path)
            df = metadata["dataframe"]
        except Exception as e:
            raise QualityCheckFailedException(f"Failed to parse dataset file: {e}")

        # 4. Fetch active rules matching dataset type (or rules with blank/null dataset_type)
        from django.db.models import Q

        rules = list(
            ValidationRule.objects.filter(is_active=True).filter(
                Q(dataset_type=dataset.file_type) | Q(dataset_type="") | Q(dataset_type__isnull=True)
            )
        )

        if not rules:
            # No rules to run — mark as validated with perfect score
            score_record = QualityScore.objects.create(
                dataset=dataset,
                score=100.0,
                total_rules=0,
                passed_rules=0,
                failed_rules=0,
            )
            dataset.status = "VALIDATED"
            dataset.save()
            return Response(
                QualityScoreResponseSerializer(score_record).data,
                status=status.HTTP_200_OK,
            )

        # 5. Run all checks
        engine = ValidationEngine()
        results = engine.run_all_checks(df, rules)

        # 6. Create CheckResult records
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

        # 7. Calculate quality score
        score_data = calculate_quality_score(results, rules)

        # 8. Create QualityScore record
        score_record = QualityScore.objects.create(
            dataset=dataset,
            score=score_data["score"],
            total_rules=score_data["total_rules"],
            passed_rules=score_data["passed_rules"],
            failed_rules=score_data["failed_rules"],
        )

        # 9. Update dataset status
        dataset.status = "VALIDATED" if score_data["score"] >= 50 else "FAILED"
        dataset.save()

        # 10. Return score
        return Response(
            QualityScoreResponseSerializer(score_record).data,
            status=status.HTTP_200_OK,
        )


class CheckResultsView(APIView):
    """Get all check results for a dataset."""

    @extend_schema(
        responses={200: CheckResultResponseSerializer(many=True)},
        tags=["Checks"],
        summary="Get check results for a dataset",
    )
    def get(self, request, dataset_id):
        """Get all check results for a dataset."""
        # Verify dataset exists and belongs to user
        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                Dataset.objects.get(id=dataset_id)
            else:
                Dataset.objects.get(id=dataset_id, uploaded_by=request.user)
        except Dataset.DoesNotExist:
            raise DatasetNotFoundException(f"Dataset with id {dataset_id} not found")

        results = (
            CheckResult.objects.filter(dataset_id=dataset_id).select_related("dataset", "rule").order_by("-checked_at")
        )
        return Response(
            CheckResultResponseSerializer(results, many=True).data,
            status=status.HTTP_200_OK,
        )
