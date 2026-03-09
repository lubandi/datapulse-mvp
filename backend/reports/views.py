"""Reports router - IMPLEMENTED."""

from checks.models import QualityScore
from checks.serializers import QualityScoreResponseSerializer
from datapulse.exceptions import DatasetNotFoundException
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from reports.serializers import QualityReportSerializer
from reports.services.report_service import generate_report, get_trend_data
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView


class DatasetReportView(APIView):
    """Get a full quality report for a dataset."""

    @extend_schema(
        responses={200: QualityReportSerializer},
        tags=["Reports"],
        summary="Get quality report for a dataset",
    )
    def get(self, request, dataset_id):
        """Get a full quality report for a dataset."""
        from datasets.models import Dataset

        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                Dataset.objects.get(id=dataset_id)
            else:
                Dataset.objects.get(id=dataset_id, uploaded_by=request.user)
        except Dataset.DoesNotExist:
            raise DatasetNotFoundException(f"Dataset with id {dataset_id} not found")

        report = generate_report(dataset_id)
        if report is None:
            raise DatasetNotFoundException(f"Dataset with id {dataset_id} not found")

        return Response(
            QualityReportSerializer(report).data,
            status=status.HTTP_200_OK,
        )


class QualityTrendsView(APIView):
    """Get quality score trends over time."""

    @extend_schema(
        parameters=[
            OpenApiParameter("days", OpenApiTypes.INT, OpenApiParameter.QUERY, default=30),
        ],
        responses={200: QualityScoreResponseSerializer(many=True)},
        tags=["Reports"],
        summary="Get quality score trends",
    )
    def get(self, request):
        """Get quality score trends over time."""
        days = int(request.query_params.get("days", 30))
        scores = get_trend_data(days=days, user=request.user)
        return Response(
            QualityScoreResponseSerializer(scores, many=True).data,
            status=status.HTTP_200_OK,
        )


class DashboardView(APIView):
    """Get aggregate dashboard data — latest quality score per dataset."""

    @extend_schema(
        responses={200: QualityScoreResponseSerializer(many=True)},
        tags=["Reports"],
        summary="Dashboard: latest quality scores for all datasets",
    )
    def get(self, request):
        """Return the latest QualityScore for each dataset that has been checked."""
        # Get unique dataset IDs that have scores, filtered by user
        if getattr(request.user, "role", "USER") == "ADMIN":
            dataset_ids = QualityScore.objects.values_list("dataset_id", flat=True).distinct()
        else:
            dataset_ids = (
                QualityScore.objects.filter(dataset__uploaded_by=request.user)
                .values_list("dataset_id", flat=True)
                .distinct()
            )

        latest_scores = []
        for ds_id in dataset_ids:
            latest = (
                QualityScore.objects.filter(dataset_id=ds_id).select_related("dataset").order_by("-checked_at").first()
            )
            if latest:
                latest_scores.append(latest)

        return Response(
            QualityScoreResponseSerializer(latest_scores, many=True).data,
            status=status.HTTP_200_OK,
        )
