"""
FIR app views – save and retrieve FIR drafts.
Includes an endpoint to trigger Gemini FIR generation directly.
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.emergency.models import EmergencyCase
from .models import FIRReport
from .serializers import FIRReportSerializer, SaveFIRSerializer
from apps.services.gemini_service import GeminiService

logger = logging.getLogger(__name__)


class SaveFIRView(APIView):
    """
    POST /api/fir/save
    Saves a FIR draft (sent by n8n after Gemini generates it).

    Request body:
    {
        "case_id": "<uuid>",
        "fir_text": "Full FIR text..."
    }
    """
    def post(self, request):
        serializer = SaveFIRSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        case_id = serializer.validated_data["case_id"]
        fir_text = serializer.validated_data["fir_text"]

        try:
            case = EmergencyCase.objects.get(case_id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Emergency case not found."}, status=status.HTTP_404_NOT_FOUND)

        # Upsert: update existing FIR or create new one
        fir, created = FIRReport.objects.update_or_create(
            case=case,
            defaults={"fir_text": fir_text},
        )

        return Response(
            {
                "message": "FIR saved successfully.",
                "fir_id": fir.id,
                "case_id": str(case_id),
                "created": created,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class GenerateFIRView(APIView):
    """
    POST /api/fir/generate
    Calls Gemini directly to generate a FIR draft for a case.
    Useful for testing without n8n.

    Request body:
    {
        "case_id": "<uuid>",
        "audio_transcript": "...",   (optional)
        "video_description": "..."   (optional)
    }
    """
    def post(self, request):
        case_id = request.data.get("case_id")
        audio_transcript = request.data.get("audio_transcript", "No audio transcript available.")
        video_description = request.data.get("video_description", "No video description available.")

        if not case_id:
            return Response({"error": "case_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            case = EmergencyCase.objects.select_related("user").get(case_id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Emergency case not found."}, status=status.HTTP_404_NOT_FOUND)

        # ── Generate FIR via Gemini ───────────────────────────────────────
        try:
            gemini = GeminiService()
            fir_text = gemini.generate_fir(
                user_name=case.user.name,
                latitude=str(case.latitude),
                longitude=str(case.longitude),
                timestamp=str(case.timestamp),
                audio_transcript=audio_transcript,
                video_description=video_description,
            )
        except Exception as e:
            logger.error(f"Gemini FIR generation failed: {e}")
            return Response(
                {"error": f"FIR generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # ── Save the generated FIR ────────────────────────────────────────
        fir, created = FIRReport.objects.update_or_create(
            case=case,
            defaults={"fir_text": fir_text},
        )

        return Response(
            {
                "message": "FIR generated and saved.",
                "case_id": str(case_id),
                "fir_text": fir_text,
            },
            status=status.HTTP_201_CREATED,
        )


class GetFIRView(APIView):
    """
    GET /api/fir/<case_id>
    Returns the FIR report for a given case.
    """
    def get(self, request, case_id):
        try:
            fir = FIRReport.objects.get(case__case_id=case_id)
        except FIRReport.DoesNotExist:
            return Response({"error": "FIR not found for this case."}, status=status.HTTP_404_NOT_FOUND)

        serializer = FIRReportSerializer(fir)
        return Response(serializer.data, status=status.HTTP_200_OK)
