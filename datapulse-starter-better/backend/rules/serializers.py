"""Rule serializers matching original Pydantic schemas."""

from rest_framework import serializers


class RuleCreateSerializer(serializers.Serializer):
    name = serializers.CharField()
    dataset_type = serializers.CharField(allow_blank=True)
    field_name = serializers.CharField()
    rule_type = serializers.CharField()
    parameters = serializers.CharField(required=False, allow_null=True, allow_blank=True, default=None)
    severity = serializers.CharField(default="MEDIUM")


class RuleResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    dataset_type = serializers.CharField()
    field_name = serializers.CharField()
    rule_type = serializers.CharField()
    parameters = serializers.CharField(allow_null=True, allow_blank=True)
    severity = serializers.CharField()
    is_active = serializers.BooleanField()
    created_at = serializers.DateTimeField()


class RuleUpdateSerializer(serializers.Serializer):
    name = serializers.CharField(required=False, allow_null=True)
    dataset_type = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    field_name = serializers.CharField(required=False, allow_null=True)
    rule_type = serializers.CharField(required=False, allow_null=True)
    parameters = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    severity = serializers.CharField(required=False, allow_null=True)
    is_active = serializers.BooleanField(required=False, allow_null=True)
