"""
Evidence app serializers.
"""
from rest_framework import serializers
from .models import Evidence


class EvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evidence
        fields = [
            "id",
            "file_type",
            "file_url",
            "original_filename",
            "latitude",
            "longitude",
            "timestamp",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
