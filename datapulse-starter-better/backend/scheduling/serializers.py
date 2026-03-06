"""Serializers for the scheduling & notifications app."""

from rest_framework import serializers


# --- Audit Log ---

class AuditLogSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(source="user.id", allow_null=True)
    user_email = serializers.EmailField(source="user.email", allow_null=True, default=None)
    action = serializers.CharField()
    dataset_id = serializers.IntegerField(source="dataset.id", allow_null=True)
    dataset_name = serializers.CharField(source="dataset.name", allow_null=True, default=None)
    details = serializers.CharField(allow_null=True)
    score = serializers.FloatField(allow_null=True)
    created_at = serializers.DateTimeField()


# --- Alert Config ---

class AlertConfigCreateSerializer(serializers.Serializer):
    dataset_id = serializers.IntegerField(required=False, allow_null=True)
    threshold = serializers.FloatField(default=70.0)
    email_recipients = serializers.CharField()
    is_active = serializers.BooleanField(default=True)


class AlertConfigResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    dataset_id = serializers.IntegerField(source="dataset.id", allow_null=True)
    threshold = serializers.FloatField()
    email_recipients = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class AlertConfigUpdateSerializer(serializers.Serializer):
    threshold = serializers.FloatField(required=False)
    email_recipients = serializers.CharField(required=False)
    is_active = serializers.BooleanField(required=False)


# --- Schedule Config ---

class ScheduleConfigCreateSerializer(serializers.Serializer):
    dataset_id = serializers.IntegerField()
    frequency = serializers.ChoiceField(
        choices=["HOURLY", "DAILY", "WEEKLY", "MONTHLY"], default="DAILY"
    )
    is_active = serializers.BooleanField(default=True)


class ScheduleConfigResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    dataset_id = serializers.IntegerField(source="dataset.id")
    dataset_name = serializers.CharField(source="dataset.name")
    frequency = serializers.CharField()
    is_active = serializers.BooleanField()
    last_run_at = serializers.DateTimeField(allow_null=True)
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class ScheduleConfigUpdateSerializer(serializers.Serializer):
    frequency = serializers.ChoiceField(
        choices=["HOURLY", "DAILY", "WEEKLY", "MONTHLY"], required=False
    )
    is_active = serializers.BooleanField(required=False)


# --- Batch Processing ---

class BatchCheckRequestSerializer(serializers.Serializer):
    dataset_ids = serializers.ListField(
        child=serializers.IntegerField(), min_length=1,
        help_text="List of dataset IDs to run checks on."
    )


class BatchCheckResultSerializer(serializers.Serializer):
    dataset_id = serializers.IntegerField()
    dataset_name = serializers.CharField()
    score = serializers.FloatField()
    status = serializers.CharField()
    detail = serializers.CharField(allow_null=True, required=False)
