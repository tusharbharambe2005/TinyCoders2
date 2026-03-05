"""
Users app models – User profiles and trusted emergency contacts.
"""
import uuid
from django.db import models


class User(models.Model):
    """
    SafeSphere user profile.
    Separate from Django's auth.User to keep the prototype simple.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    phone = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    device_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.phone})"


class TrustedContact(models.Model):
    """
    People to notify when the user triggers an emergency.
    Each user can have multiple trusted contacts.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="trusted_contacts"
    )
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    contact_email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "trusted_contacts"

    def __str__(self):
        return f"{self.contact_name} → {self.user.name}"
