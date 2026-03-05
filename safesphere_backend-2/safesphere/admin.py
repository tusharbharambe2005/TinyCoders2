"""
SafeSphere – Central Admin Registration
========================================
Place this file at:  safesphere_backend/safesphere/admin.py

OR run this command to auto-discover it:
    python manage.py runserver
    then visit: http://localhost:8000/admin

All 5 models are registered here in one place:
  ✅ User
  ✅ TrustedContact
  ✅ EmergencyCase
  ✅ Evidence
  ✅ FIRReport

HOW TO CREATE ADMIN LOGIN:
    python manage.py createsuperuser
    → enter username, email, password
    → visit http://localhost:8000/admin
"""

from django.contrib import admin

# ── Import all models ─────────────────────────────────────────────────────────
from apps.users.models import User, TrustedContact
from apps.emergency.models import EmergencyCase
from apps.evidence.models import Evidence
from apps.fir.models import FIRReport


# ═════════════════════════════════════════════════════════════════════════════
#  1. USER
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display  = ("name", "phone", "email", "device_id", "created_at")
    search_fields = ("name", "phone", "email")
    ordering      = ("-created_at",)
    readonly_fields = ("id", "created_at")


# ═════════════════════════════════════════════════════════════════════════════
#  2. TRUSTED CONTACT
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(TrustedContact)
class TrustedContactAdmin(admin.ModelAdmin):
    list_display  = ("contact_name", "contact_phone", "contact_email", "user", "created_at")
    search_fields = ("contact_name", "contact_phone", "user__name")
    list_filter   = ("user",)
    ordering      = ("-created_at",)
    readonly_fields = ("created_at",)


# ═════════════════════════════════════════════════════════════════════════════
#  3. EMERGENCY CASE
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(EmergencyCase)
class EmergencyCaseAdmin(admin.ModelAdmin):
    list_display  = ("case_id", "user", "status", "latitude", "longitude", "timestamp", "created_at")
    search_fields = ("case_id", "user__name", "user__phone")
    list_filter   = ("status",)
    ordering      = ("-created_at",)
    readonly_fields = ("case_id", "created_at", "updated_at")


# ═════════════════════════════════════════════════════════════════════════════
#  4. EVIDENCE
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display  = ("id", "case", "file_type", "original_filename", "latitude", "longitude", "timestamp", "created_at")
    search_fields = ("case__case_id", "original_filename")
    list_filter   = ("file_type",)
    ordering      = ("-created_at",)
    readonly_fields = ("created_at",)


# ═════════════════════════════════════════════════════════════════════════════
#  5. FIR REPORT
# ═════════════════════════════════════════════════════════════════════════════

@admin.register(FIRReport)
class FIRReportAdmin(admin.ModelAdmin):
    list_display  = ("id", "case", "created_at", "updated_at")
    search_fields = ("case__case_id",)
    ordering      = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")