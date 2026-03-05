"""
Emergency app URL routes.
"""
from django.urls import path
from .views import StartEmergencyView, CaseDetailView, UpdateCaseStatusView

urlpatterns = [
    # Emergency management
    path("start", StartEmergencyView.as_view(), name="emergency-start"),
    path("<uuid:case_id>/status", UpdateCaseStatusView.as_view(), name="emergency-status-update"),

    # Case detail (also mounted at /api/case/<case_id> from root urls.py)
    path("<uuid:case_id>", CaseDetailView.as_view(), name="case-detail"),
]
