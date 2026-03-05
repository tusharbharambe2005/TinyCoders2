from django.contrib import admin
from .models import User, TrustedContact


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display   = ("name", "phone", "email", "device_id", "created_at")
    search_fields  = ("name", "phone", "email")
    ordering       = ("-created_at",)
    readonly_fields = ("id", "created_at")


@admin.register(TrustedContact)
class TrustedContactAdmin(admin.ModelAdmin):
    list_display   = ("contact_name", "contact_phone", "contact_email", "user", "created_at")
    search_fields  = ("contact_name", "contact_phone", "user__name")
    list_filter    = ("user",)
    ordering       = ("-created_at",)
    readonly_fields = ("id", "created_at")