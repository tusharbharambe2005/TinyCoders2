"""
FIR app serializers.
"""
from rest_framework import serializers
from .models import FIRReport


class FIRReportSerializer(serializers.ModelSerializer):
    case_id = serializers.UUIDField(source="case.case_id", read_only=True)

    class Meta:
        model = FIRReport
        fields = ["id", "case_id", "fir_text", "created_at", "updated_at"]
        read_only_fields = ["id", "case_id", "created_at", "updated_at"]


class SaveFIRSerializer(serializers.Serializer):
    """Used for POST /api/fir/save – accepts case_id + fir_text."""
    case_id = serializers.UUIDField()
    fir_text = serializers.CharField()
