from django.contrib import admin
from .models import EmergencyCase


@admin.register(EmergencyCase)
class EmergencyCaseAdmin(admin.ModelAdmin):
    list_display    = ("case_id", "user", "status", "latitude", "longitude", "timestamp", "created_at")
    search_fields   = ("case_id", "user__name", "user__phone")
    list_filter     = ("status",)
    ordering        = ("-created_at",)
    readonly_fields = ("case_id", "created_at", "updated_at")