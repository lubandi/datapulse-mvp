"""Quality checks router - IMPLEMENTED."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from checks.models import CheckResult, QualityScore
from checks.serializers import CheckResultResponseSerializer, QualityScoreResponseSerializer
from checks.services.validation_engine import ValidationEngine
from checks.services.scoring_service import calculate_quality_score
from datasets.models import Dataset, DatasetFile
from datasets.services.file_parser import parse_csv, parse_json
from rules.models import ValidationRule
from datapulse.exceptions import DatasetNotFoundException, QualityCheckFailedException


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

        # 2. Execute checks via shared service
        from scheduling.services import run_checks_for_dataset
        from scheduling.notifications import check_and_notify

        user = request.user if request.user and request.user.is_authenticated else None
        result = run_checks_for_dataset(dataset, user=user, action="CHECK_RUN")

        if "error" in result:
            raise QualityCheckFailedException(result["error"])

        # 3. Check and trigger email notifications
        if "score" in result:
            check_and_notify(dataset, result["score"])

        # 4. Return QualityScore
        if "quality_score_id" in result:
            score_record = QualityScore.objects.get(id=result["quality_score_id"])
            return Response(
                QualityScoreResponseSerializer(score_record).data,
                status=status.HTTP_200_OK,
            )
        else:
            raise QualityCheckFailedException("Failed to retrieve quality score")


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
            CheckResult.objects.filter(dataset_id=dataset_id)
            .select_related("dataset", "rule")
            .order_by("-checked_at")
        )
        return Response(
            CheckResultResponseSerializer(results, many=True).data,
            status=status.HTTP_200_OK,
        )

