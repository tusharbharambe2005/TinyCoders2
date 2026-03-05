from django.contrib import admin
from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display    = ("id", "case", "file_type", "original_filename", "latitude", "longitude", "timestamp", "created_at")
    search_fields   = ("case__case_id", "original_filename")
    list_filter     = ("file_type",)
    ordering        = ("-created_at",)
    readonly_fields = ("id", "created_at")