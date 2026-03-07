"""Check result serializers."""

from rest_framework import serializers
from checks.models import CheckResult, QualityScore


class CheckResultResponseSerializer(serializers.ModelSerializer):
    dataset_id = serializers.IntegerField(source="dataset.id", read_only=True)
    rule_id = serializers.IntegerField(source="rule.id", read_only=True)

    class Meta:
        model = CheckResult
        fields = [
            "id", "dataset_id", "rule_id", "passed", 
            "failed_rows", "total_rows", "details", "checked_at"
        ]


class QualityScoreResponseSerializer(serializers.ModelSerializer):
    dataset_id = serializers.IntegerField(source="dataset.id", read_only=True)

    class Meta:
        model = QualityScore
        fields = [
            "id", "dataset_id", "score", "total_rules", 
            "passed_rules", "failed_rules", "checked_at"
        ]
