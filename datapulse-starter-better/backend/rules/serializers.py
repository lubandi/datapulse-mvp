"""Rule serializers."""

from rest_framework import serializers
from rules.models import ValidationRule


class RuleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRule
        fields = ["name", "dataset_type", "field_name", "rule_type", "parameters", "severity"]


class RuleResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRule
        fields = [
            "id", "name", "dataset_type", "field_name", "rule_type", 
            "parameters", "severity", "is_active", "created_at"
        ]


class RuleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ValidationRule
        fields = ["name", "dataset_type", "field_name", "rule_type", "parameters", "severity", "is_active"]
        extra_kwargs = {
            "name": {"required": False},
            "dataset_type": {"required": False},
            "field_name": {"required": False},
            "rule_type": {"required": False},
            "parameters": {"required": False},
            "severity": {"required": False},
            "is_active": {"required": False},
        }
