"""Views for scheduling, notifications, batch processing, and audit log."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from datasets.models import Dataset
from datapulse.exceptions import DatasetNotFoundException

from scheduling.models import AuditLog, AlertConfig, ScheduleConfig
from scheduling.serializers import (
    AuditLogSerializer,
    AlertConfigCreateSerializer,
    AlertConfigResponseSerializer,
    AlertConfigUpdateSerializer,
    ScheduleConfigCreateSerializer,
    ScheduleConfigResponseSerializer,
    ScheduleConfigUpdateSerializer,
    BatchCheckRequestSerializer,
    BatchCheckResultSerializer,
)
from scheduling.services import run_checks_for_dataset
from scheduling.notifications import check_and_notify


# ---------- Batch Processing ----------

class BatchCheckView(APIView):
    """Run quality checks on multiple datasets at once."""

    @extend_schema(
        request=BatchCheckRequestSerializer,
        responses={200: BatchCheckResultSerializer(many=True)},
        tags=["Scheduling"],
        summary="Run quality checks on multiple datasets",
    )
    def post(self, request):
        """Run checks on a list of dataset IDs and return results for each."""
        serializer = BatchCheckRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dataset_ids = serializer.validated_data["dataset_ids"]

        results = []
        user = request.user if request.user and request.user.is_authenticated else None

        if getattr(request.user, "role", "USER") == "ADMIN":
            datasets = Dataset.objects.filter(id__in=dataset_ids)
        else:
            datasets = Dataset.objects.filter(id__in=dataset_ids, uploaded_by=request.user)
            
        dataset_map = {ds.id: ds for ds in datasets}

        for ds_id in dataset_ids:
            dataset = dataset_map.get(ds_id)
            if not dataset:
                results.append({
                    "dataset_id": ds_id,
                    "dataset_name": "Unknown",
                    "score": 0.0,
                    "status": "ERROR",
                    "detail": f"Dataset {ds_id} not found or access denied",
                })
                continue

            result = run_checks_for_dataset(dataset, user=user, action="BATCH_RUN")

            if "error" in result:
                results.append({
                    "dataset_id": ds_id,
                    "dataset_name": dataset.name,
                    "score": 0.0,
                    "status": "ERROR",
                    "detail": result["error"],
                })
            else:
                results.append({
                    "dataset_id": ds_id,
                    "dataset_name": dataset.name,
                    "score": result["score"],
                    "status": result["status"],
                    "detail": None,
                })
                # Check and notify on each result
                check_and_notify(dataset, result["score"])

        return Response(
            BatchCheckResultSerializer(results, many=True).data,
            status=status.HTTP_200_OK,
        )


# ---------- Audit Log ----------

class AuditLogListView(APIView):
    """View audit log entries."""

    @extend_schema(
        parameters=[
            OpenApiParameter("dataset_id", OpenApiTypes.INT, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("action", OpenApiTypes.STR, OpenApiParameter.QUERY, required=False),
            OpenApiParameter("limit", OpenApiTypes.INT, OpenApiParameter.QUERY, default=50),
        ],
        responses={200: AuditLogSerializer(many=True)},
        tags=["Scheduling"],
        summary="List audit log entries",
    )
    def get(self, request):
        """List audit log entries with optional filtering."""
        if getattr(request.user, "role", "USER") == "ADMIN":
            queryset = AuditLog.objects.select_related("user", "dataset").all()
        else:
            queryset = AuditLog.objects.select_related("user", "dataset").filter(user=request.user)

        dataset_id = request.query_params.get("dataset_id")
        if dataset_id:
            queryset = queryset.filter(dataset_id=dataset_id)

        action = request.query_params.get("action")
        if action:
            queryset = queryset.filter(action=action)

        limit = min(int(request.query_params.get("limit", 50)), 200)
        queryset = queryset[:limit]

        return Response(
            AuditLogSerializer(queryset, many=True).data,
            status=status.HTTP_200_OK,
        )


# ---------- Alert Config ----------

class AlertConfigListCreateView(APIView):
    """CRUD for alert configurations."""

    @extend_schema(
        responses={200: AlertConfigResponseSerializer(many=True)},
        tags=["Scheduling"],
        summary="List alert configurations",
    )
    def get(self, request):
        """List all alert configurations."""
        if getattr(request.user, "role", "USER") == "ADMIN":
            configs = AlertConfig.objects.select_related("dataset").filter(is_active=True)
        else:
            from django.db.models import Q
            configs = AlertConfig.objects.select_related("dataset").filter(
                Q(dataset__isnull=True) | Q(dataset__uploaded_by=request.user),
                is_active=True
            )
        return Response(
            AlertConfigResponseSerializer(configs, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=AlertConfigCreateSerializer,
        responses={201: AlertConfigResponseSerializer},
        tags=["Scheduling"],
        summary="Create an alert configuration",
    )
    def post(self, request):
        """Create a new alert configuration."""
        serializer = AlertConfigCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        dataset = None
        if data.get("dataset_id"):
            try:
                if getattr(request.user, "role", "USER") == "ADMIN":
                    dataset = Dataset.objects.get(id=data["dataset_id"])
                else:
                    dataset = Dataset.objects.get(id=data["dataset_id"], uploaded_by=request.user)
            except Dataset.DoesNotExist:
                raise DatasetNotFoundException(f"Dataset {data['dataset_id']} not found or access denied")
        elif getattr(request.user, "role", "USER") != "ADMIN":
            # Only ADMIN can create global alerts
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only administrators can create global alert configurations.")

        config = AlertConfig.objects.create(
            dataset=dataset,
            threshold=data["threshold"],
            email_recipients=data["email_recipients"],
            is_active=data.get("is_active", True),
        )
        return Response(
            AlertConfigResponseSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )


class AlertConfigDetailView(APIView):
    """Update or delete an alert configuration."""

    @extend_schema(
        request=AlertConfigUpdateSerializer,
        responses={200: AlertConfigResponseSerializer},
        tags=["Scheduling"],
        summary="Update an alert configuration",
    )
    def put(self, request, config_id):
        """Update an existing alert configuration."""
        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                config = AlertConfig.objects.get(id=config_id)
            else:
                from django.db.models import Q
                config = AlertConfig.objects.get(
                    Q(id=config_id),
                    Q(dataset__isnull=True, is_active=True) | Q(dataset__uploaded_by=request.user)
                )
                if config.dataset is None:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("Cannot modify global alert configurations.")
        except AlertConfig.DoesNotExist:
            return Response(
                {"detail": f"Alert config {config_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = AlertConfigUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(config, field, value)
        config.save()

        return Response(
            AlertConfigResponseSerializer(config).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={204: None},
        tags=["Scheduling"],
        summary="Delete an alert configuration",
    )
    def delete(self, request, config_id):
        """Delete an alert configuration."""
        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                config = AlertConfig.objects.get(id=config_id)
            else:
                from django.db.models import Q
                config = AlertConfig.objects.get(
                    Q(id=config_id),
                    Q(dataset__isnull=True, is_active=True) | Q(dataset__uploaded_by=request.user)
                )
                if config.dataset is None:
                    from rest_framework.exceptions import PermissionDenied
                    raise PermissionDenied("Cannot delete global alert configurations.")
        except AlertConfig.DoesNotExist:
            return Response(
                {"detail": f"Alert config {config_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# ---------- Schedule Config ----------

class ScheduleConfigListCreateView(APIView):
    """CRUD for schedule configurations."""

    @extend_schema(
        responses={200: ScheduleConfigResponseSerializer(many=True)},
        tags=["Scheduling"],
        summary="List schedule configurations",
    )
    def get(self, request):
        """List all schedule configurations."""
        if getattr(request.user, "role", "USER") == "ADMIN":
            configs = ScheduleConfig.objects.select_related("dataset").all()
        else:
            configs = ScheduleConfig.objects.select_related("dataset").filter(dataset__uploaded_by=request.user)
            
        return Response(
            ScheduleConfigResponseSerializer(configs, many=True).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=ScheduleConfigCreateSerializer,
        responses={201: ScheduleConfigResponseSerializer},
        tags=["Scheduling"],
        summary="Create a schedule configuration",
    )
    def post(self, request):
        """Create a new schedule configuration."""
        serializer = ScheduleConfigCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                dataset = Dataset.objects.get(id=data["dataset_id"])
            else:
                dataset = Dataset.objects.get(id=data["dataset_id"], uploaded_by=request.user)
        except Dataset.DoesNotExist:
            raise DatasetNotFoundException(f"Dataset {data['dataset_id']} not found")

        config = ScheduleConfig.objects.create(
            dataset=dataset,
            frequency=data.get("frequency", "DAILY"),
            is_active=data.get("is_active", True),
        )
        return Response(
            ScheduleConfigResponseSerializer(config).data,
            status=status.HTTP_201_CREATED,
        )


class ScheduleConfigDetailView(APIView):
    """Update or delete a schedule configuration."""

    @extend_schema(
        request=ScheduleConfigUpdateSerializer,
        responses={200: ScheduleConfigResponseSerializer},
        tags=["Scheduling"],
        summary="Update a schedule configuration",
    )
    def put(self, request, config_id):
        """Update an existing schedule configuration."""
        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                config = ScheduleConfig.objects.select_related("dataset").get(id=config_id)
            else:
                config = ScheduleConfig.objects.select_related("dataset").get(id=config_id, dataset__uploaded_by=request.user)
        except ScheduleConfig.DoesNotExist:
            return Response(
                {"detail": f"Schedule config {config_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ScheduleConfigUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(config, field, value)
        config.save()

        return Response(
            ScheduleConfigResponseSerializer(config).data,
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        responses={204: None},
        tags=["Scheduling"],
        summary="Delete a schedule configuration",
    )
    def delete(self, request, config_id):
        """Delete a schedule configuration."""
        try:
            if getattr(request.user, "role", "USER") == "ADMIN":
                config = ScheduleConfig.objects.get(id=config_id)
            else:
                config = ScheduleConfig.objects.get(id=config_id, dataset__uploaded_by=request.user)
        except ScheduleConfig.DoesNotExist:
            return Response(
                {"detail": f"Schedule config {config_id} not found"},
                status=status.HTTP_404_NOT_FOUND,
            )
        config.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
