"""
FIR app URL routes.
"""
from django.urls import path
from .views import SaveFIRView, GenerateFIRView, GetFIRView

urlpatterns = [
    path("save", SaveFIRView.as_view(), name="fir-save"),
    path("generate", GenerateFIRView.as_view(), name="fir-generate"),
    path("<uuid:case_id>", GetFIRView.as_view(), name="fir-get"),
]
