"""
SafeSphere – Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Users & trusted contacts
    path("api/users/", include("apps.users.urls")),

    # Emergency case management
    path("api/emergency/", include("apps.emergency.urls")),

    # Evidence upload
    path("api/evidence/", include("apps.evidence.urls")),

    # FIR reports
    path("api/fir/", include("apps.fir.urls")),

    # Unified case detail endpoint
    path("api/case/", include("apps.emergency.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
