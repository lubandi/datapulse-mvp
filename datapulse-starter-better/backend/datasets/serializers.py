"""Dataset serializers matching original Pydantic schemas."""

from rest_framework import serializers


class DatasetResponseSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    file_type = serializers.CharField()
    row_count = serializers.IntegerField()
    column_count = serializers.IntegerField()
    column_names = serializers.CharField(allow_null=True)
    status = serializers.CharField()
    uploaded_at = serializers.DateTimeField()


class DatasetListSerializer(serializers.Serializer):
    datasets = DatasetResponseSerializer(many=True)
    total = serializers.IntegerField()
