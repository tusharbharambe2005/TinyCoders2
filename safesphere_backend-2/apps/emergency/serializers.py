"""
Emergency app serializers.
"""
from rest_framework import serializers
from .models import EmergencyCase


class StartEmergencySerializer(serializers.ModelSerializer):
    """Used for POST /api/emergency/start."""
    user_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = EmergencyCase
        fields = ["user_id", "latitude", "longitude", "timestamp"]

    def create(self, validated_data):
        from apps.users.models import User
        user = User.objects.get(id=validated_data.pop("user_id"))
        return EmergencyCase.objects.create(user=user, **validated_data)


class EmergencyCaseSerializer(serializers.ModelSerializer):
    """Full case details – used for GET /api/case/<case_id>."""
    user_name = serializers.CharField(source="user.name", read_only=True)
    user_phone = serializers.CharField(source="user.phone", read_only=True)

    # Nested relations (populated via source in CaseDetailView)
    evidence_files = serializers.SerializerMethodField()
    fir_text = serializers.SerializerMethodField()

    class Meta:
        model = EmergencyCase
        fields = [
            "case_id",
            "user_name",
            "user_phone",
            "latitude",
            "longitude",
            "timestamp",
            "status",
            "created_at",
            "evidence_files",
            "fir_text",
        ]

    def get_evidence_files(self, obj):
        from apps.evidence.serializers import EvidenceSerializer
        return EvidenceSerializer(obj.evidence_files.all(), many=True).data

    def get_fir_text(self, obj):
        fir = obj.fir_reports.first()
        if fir:
            return fir.fir_text
        return None
