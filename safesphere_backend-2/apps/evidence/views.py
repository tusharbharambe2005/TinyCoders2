"""
Evidence app views – handles multipart file upload, storage, and n8n webhook trigger.
"""
import logging
from django.utils import timezone
from datetime import datetime

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser

from apps.emergency.models import EmergencyCase
from .models import Evidence
from .serializers import EvidenceSerializer
from apps.services.storage_service import StorageService  # factory: .get() picks local or cloud
from apps.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)


class UploadEvidenceView(APIView):
    """
    POST /api/evidence/upload
    Accepts multipart/form-data with video and/or audio files.

    Fields:
        case_id     – UUID of the emergency case
        video_file  – (optional) video recording
        audio_file  – (optional) audio recording
        latitude    – GPS latitude at time of upload
        longitude   – GPS longitude at time of upload
        timestamp   – ISO8601 datetime string
    """
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        case_id = request.data.get("case_id")
        latitude = request.data.get("latitude")
        longitude = request.data.get("longitude")
        timestamp_str = request.data.get("timestamp")
        
        # Parse and make timestamp timezone-aware
        if timestamp_str:
            try:
                # Try parsing ISO format
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                # Make timezone-aware if naive
                if timezone.is_naive(timestamp):
                    timestamp = timezone.make_aware(timestamp)
            except (ValueError, AttributeError):
                timestamp = timezone.now()
        else:
            timestamp = timezone.now()

        # ── Validate case ────────────────────────────────────────────────
        if not case_id:
            return Response({"error": "case_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            case = EmergencyCase.objects.select_related("user").get(case_id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Emergency case not found."}, status=status.HTTP_404_NOT_FOUND)

        storage = StorageService.get()   # picks LocalStorage or CloudStorage from .env
        saved_evidence = []

        # ── Process video file ────────────────────────────────────────────
        video_file = request.FILES.get("video_file")
        if video_file:
            try:
                video_url = storage.save(video_file, subfolder=f"case_{case_id}/video")
                ev = Evidence.objects.create(
                    case=case,
                    file_type=Evidence.FileType.VIDEO,
                    file_url=video_url,
                    original_filename=video_file.name,
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=timestamp,
                )
                saved_evidence.append(ev)
            except Exception as e:
                logger.error(f"Video upload failed: {e}")
                return Response({"error": f"Video upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # ── Process audio file ────────────────────────────────────────────
        audio_file = request.FILES.get("audio_file")
        if audio_file:
            try:
                audio_url = storage.save(audio_file, subfolder=f"case_{case_id}/audio")
                ev = Evidence.objects.create(
                    case=case,
                    file_type=Evidence.FileType.AUDIO,
                    file_url=audio_url,
                    original_filename=audio_file.name,
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=timestamp,
                )
                saved_evidence.append(ev)
            except Exception as e:
                logger.error(f"Audio upload failed: {e}")
                return Response({"error": f"Audio upload failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        if not saved_evidence:
            return Response(
                {"error": "No files provided. Include video_file or audio_file."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ── Trigger n8n webhook ───────────────────────────────────────────
        primary_url = saved_evidence[0].file_url
        
        # Build webhook payload with all required fields
        webhook_payload = {
            "case_id": str(case_id),
            "user_name": case.user.name,
            "user_phone": case.user.phone,
            "user_email": case.user.email,
            "video_url": primary_url,  # Cloudinary URL or local path
            "location_description": f"Location: {latitude}, {longitude}",
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "start_time": str(timestamp) if timestamp else str(case.created_at),
            "end_time": str(timestamp) if timestamp else str(case.created_at),
            "police_station_name": "Nearest Police Station",  # Can be customized
            "evidence_count": len(saved_evidence),
            "trusted_contacts": [
                {
                    "name": tc.contact_name,
                    "phone": tc.contact_phone,
                    "email": tc.contact_email,
                }
                for tc in case.user.trusted_contacts.all()
            ],
        }

        try:
            webhook = WebhookService()
            webhook.trigger(webhook_payload)
        except Exception as e:
            # Log but don't fail the request – evidence is already saved
            logger.error(f"n8n webhook trigger failed: {e}")

        # ── Return response ───────────────────────────────────────────────
        return Response(
            {
                "message": "Evidence uploaded successfully. Emergency contacts notified.",
                "case_id": str(case_id),
                "uploaded_files": EvidenceSerializer(saved_evidence, many=True).data,
            },
            status=status.HTTP_201_CREATED,
        )


class ListEvidenceView(APIView):
    """
    GET /api/evidence/<case_id>
    Returns all evidence files for a given case.
    """
    def get(self, request, case_id):
        evidence = Evidence.objects.filter(case__case_id=case_id)
        serializer = EvidenceSerializer(evidence, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
