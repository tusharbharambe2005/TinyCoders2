from django.contrib import admin
from .models import FIRReport


@admin.register(FIRReport)
class FIRReportAdmin(admin.ModelAdmin):
    list_display    = ("id", "case", "created_at", "updated_at")
    search_fields   = ("case__case_id",)
    ordering        = ("-created_at",)
    readonly_fields = ("id", "created_at", "updated_at")