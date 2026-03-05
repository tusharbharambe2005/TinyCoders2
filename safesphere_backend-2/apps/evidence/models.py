"""
Evidence app models – stores uploaded video/audio files linked to a case.
"""
from django.db import models
from apps.emergency.models import EmergencyCase


class Evidence(models.Model):
    """
    A single piece of evidence (video or audio) tied to an emergency case.
    The file itself is stored locally or in Cloudinary (see StorageService).
    """

    class FileType(models.TextChoices):
        VIDEO = "video", "Video"
        AUDIO = "audio", "Audio"
        IMAGE = "image", "Image"
        OTHER = "other", "Other"

    case = models.ForeignKey(
        EmergencyCase,
        on_delete=models.CASCADE,
        related_name="evidence_files"
    )
    file_type = models.CharField(max_length=20, choices=FileType.choices)
    file_url = models.TextField()          # Local path or full S3 URL
    original_filename = models.CharField(max_length=500, blank=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "evidence"
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.file_type} – Case {self.case.case_id}"
