"""
Emergency app models – tracks active emergency cases.
"""
import uuid
from django.db import models
from apps.users.models import User


class EmergencyCase(models.Model):
    """
    An emergency case created when a user triggers the SOS.
    All evidence and FIR reports are linked to this case.
    """

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RESOLVED = "resolved", "Resolved"
        CLOSED = "closed", "Closed"

    case_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="emergency_cases"
    )
    latitude = models.DecimalField(max_digits=10, decimal_places=7)
    longitude = models.DecimalField(max_digits=10, decimal_places=7)
    timestamp = models.DateTimeField()
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "emergency_cases"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Case {self.case_id} – {self.user.name} [{self.status}]"
