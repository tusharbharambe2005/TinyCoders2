"""
Emergency app views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import EmergencyCase
from .serializers import StartEmergencySerializer, EmergencyCaseSerializer


class StartEmergencyView(APIView):
    """
    POST /api/emergency/start
    Creates a new emergency case and returns the case_id.

    Request body:
    {
        "user_id": "<uuid>",
        "latitude": 18.5204,
        "longitude": 73.8567,
        "timestamp": "2026-03-05T12:00:00"
    }
    """
    def post(self, request):
        serializer = StartEmergencySerializer(data=request.data)

        if serializer.is_valid():
            try:
                case = serializer.save()
            except Exception as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return Response(
                {
                    "message": "Emergency case created. Stay safe.",
                    "case_id": str(case.case_id),
                    "status": case.status,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CaseDetailView(APIView):
    """
    GET /api/case/<case_id>
    Returns full case details including evidence files and FIR report.
    """
    def get(self, request, case_id):
        try:
            case = EmergencyCase.objects.prefetch_related(
                "evidence_files", "fir_reports"
            ).get(case_id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Case not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = EmergencyCaseSerializer(case)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateCaseStatusView(APIView):
    """
    PATCH /api/emergency/<case_id>/status
    Updates the status of an emergency case (active → resolved → closed).
    """
    def patch(self, request, case_id):
        try:
            case = EmergencyCase.objects.get(case_id=case_id)
        except EmergencyCase.DoesNotExist:
            return Response({"error": "Case not found."}, status=status.HTTP_404_NOT_FOUND)

        new_status = request.data.get("status")
        valid_statuses = [s.value for s in EmergencyCase.Status]

        if new_status not in valid_statuses:
            return Response(
                {"error": f"Invalid status. Choose from: {valid_statuses}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        case.status = new_status
        case.save()

        return Response(
            {"message": "Case status updated.", "case_id": str(case.case_id), "status": case.status},
            status=status.HTTP_200_OK,
        )
