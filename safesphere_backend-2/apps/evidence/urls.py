"""
Evidence app URL routes.
"""
from django.urls import path
from .views import UploadEvidenceView, ListEvidenceView

urlpatterns = [
    path("upload", UploadEvidenceView.as_view(), name="evidence-upload"),
    path("<uuid:case_id>", ListEvidenceView.as_view(), name="evidence-list"),
]
