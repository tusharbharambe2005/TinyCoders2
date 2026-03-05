"""
StorageService – saves uploaded evidence files.

TWO BACKENDS – controlled by STORAGE_BACKEND in your .env:

  STORAGE_BACKEND=local        → LocalStorage       → saves to media/evidence/ on disk
  STORAGE_BACKEND=cloudinary   → CloudinaryStorage  → uploads to Cloudinary (FREE ✅)

Usage (called from evidence/views.py):
    storage = StorageService.get()        # returns correct backend automatically
    url = storage.save(file_obj, subfolder="case_abc/video")

RECOMMENDATION:
  ✅ Hackathon / demo / production → cloudinary  (free, files accessible from any device/app)
  ✅ Local dev / testing           → local       (zero config)
"""
import os
import uuid
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════════════
#  BASE CLASS
# ═════════════════════════════════════════════════════════════════════════════

class BaseStorage:
    """Interface that all storage backends must implement."""

    def save(self, file_obj, subfolder: str = "uploads") -> str:
        raise NotImplementedError("Storage backend must implement save()")


# ═════════════════════════════════════════════════════════════════════════════
#  OPTION 1 · LOCAL STORAGE  (STORAGE_BACKEND=local)
# ═════════════════════════════════════════════════════════════════════════════

class LocalStorage(BaseStorage):
    """
    Saves files to MEDIA_ROOT/evidence/<subfolder>/ on the local filesystem.
    Files are served by Django's dev server via /media/ URL.

    ✅ Works out of the box – no credentials needed
    ✅ Use for: local development, testing
    ⚠️  Files only accessible on the same machine / same WiFi network
    ⚠️  Flutter on a different machine CANNOT load file URLs directly
    """

    def save(self, file_obj, subfolder: str = "uploads") -> str:
        # Build target directory
        save_dir = os.path.join(settings.MEDIA_ROOT, "evidence", subfolder)
        os.makedirs(save_dir, exist_ok=True)

        # Generate a unique filename to prevent overwrite collisions
        ext = os.path.splitext(file_obj.name)[1]           # e.g. ".mp4"
        unique_name = f"{uuid.uuid4().hex}{ext}"           # e.g. "a3f9...mp4"
        full_path = os.path.join(save_dir, unique_name)

        # Stream-write the uploaded file to disk (memory-safe for large videos)
        with open(full_path, "wb+") as dest:
            for chunk in file_obj.chunks():
                dest.write(chunk)

        # Build relative media URL → /media/evidence/case_xxx/video/abc.mp4
        relative = os.path.relpath(full_path, settings.MEDIA_ROOT)
        url = f"{settings.MEDIA_URL}{relative}"

        logger.info(f"[LocalStorage] File saved → {full_path}")
        return url


# ═════════════════════════════════════════════════════════════════════════════
#  OPTION 2 · CLOUDINARY  (STORAGE_BACKEND=cloudinary)
#
#  ✅ FREE tier: 25 GB storage + 25 GB bandwidth/month
#  ✅ Files get a permanent HTTPS URL — accessible from ANY device or app
#  ✅ Flutter, browser, Postman — all can load the file directly
#  ✅ No credit card needed
#
#  Setup (3 minutes):
#    1. Sign up free at  https://cloudinary.com
#    2. Open your Dashboard and copy the 3 values shown below
#    3. Add to your .env file:
#
#         STORAGE_BACKEND=cloudinary
#         CLOUDINARY_CLOUD_NAME=your_cloud_name
#         CLOUDINARY_API_KEY=123456789012345
#         CLOUDINARY_API_SECRET=AbCdEfGhIjKlMnOpQrStUv
#
#    4. Install:  pip install cloudinary
# ═════════════════════════════════════════════════════════════════════════════

class CloudinaryStorage(BaseStorage):
    """
    Uploads files to Cloudinary and returns a permanent public HTTPS URL.
    Supports video, audio, and any other file type.
    """

    # File extensions → resource_type mapping for Cloudinary API
    VIDEO_EXTS = {".mp4", ".mov", ".avi", ".webm", ".mkv", ".3gp", ".flv"}
    AUDIO_EXTS = {".mp3", ".m4a", ".wav", ".aac", ".ogg", ".flac", ".opus"}

    def save(self, file_obj, subfolder: str = "uploads") -> str:
        # ── Import check ──────────────────────────────────────────────────────
        try:
            import cloudinary
            import cloudinary.uploader
        except ImportError:
            raise RuntimeError(
                "Cloudinary SDK is not installed.\n"
                "Run: pip install cloudinary"
            )

        # ── Credentials check ─────────────────────────────────────────────────
        cloud_name = getattr(settings, "CLOUDINARY_CLOUD_NAME", "").strip()
        api_key    = getattr(settings, "CLOUDINARY_API_KEY",    "").strip()
        api_secret = getattr(settings, "CLOUDINARY_API_SECRET", "").strip()

        if not all([cloud_name, api_key, api_secret]):
            raise ValueError(
                "Cloudinary credentials are missing or incomplete.\n"
                "Add these three lines to your .env file:\n"
                "  CLOUDINARY_CLOUD_NAME=your_cloud_name\n"
                "  CLOUDINARY_API_KEY=your_api_key\n"
                "  CLOUDINARY_API_SECRET=your_api_secret\n"
                "Get them from: https://cloudinary.com → Dashboard"
            )

        # ── Configure Cloudinary SDK ──────────────────────────────────────────
        cloudinary.config(
            cloud_name=cloud_name,
            api_key=api_key,
            api_secret=api_secret,
            secure=True,    # always return https:// URLs
        )

        # ── Detect resource type from file extension ──────────────────────────
        # Cloudinary splits files into: image | video | raw
        # Note: audio files are uploaded under "video" resource_type in Cloudinary
        ext = os.path.splitext(file_obj.name)[1].lower()

        if ext in self.VIDEO_EXTS:
            resource_type = "video"
        elif ext in self.AUDIO_EXTS:
            resource_type = "video"     # Cloudinary handles audio under "video"
        else:
            resource_type = "raw"       # PDFs, text files, etc.

        # ── Upload to Cloudinary ──────────────────────────────────────────────
        folder = f"safesphere/evidence/{subfolder}"

        logger.info(f"[CloudinaryStorage] Uploading {file_obj.name} → folder: {folder}")

        result = cloudinary.uploader.upload(
            file_obj,
            folder=folder,
            resource_type=resource_type,
            use_filename=False,         # use Cloudinary's auto-generated ID
            unique_filename=True,
            overwrite=False,
        )

        # ── Return the secure public URL ──────────────────────────────────────
        url = result.get("secure_url", "")

        if not url:
            raise RuntimeError("Cloudinary upload succeeded but returned no URL.")

        logger.info(f"[CloudinaryStorage] Uploaded → {url}")
        return url





# ═════════════════════════════════════════════════════════════════════════════
#  FACTORY — auto-selects backend from STORAGE_BACKEND in .env
# ═════════════════════════════════════════════════════════════════════════════

class StorageService:
    """
    Factory. Call StorageService.get() to get the active storage backend.
    The rest of the codebase never needs to know which backend is active.

    STORAGE_BACKEND=local        → LocalStorage       (saves to disk)
    STORAGE_BACKEND=cloudinary   → CloudinaryStorage  (Cloudinary FREE ✅)
    """

    @staticmethod
    def get() -> BaseStorage:
        backend = getattr(settings, "STORAGE_BACKEND", "local").strip().lower()

        if backend == "cloudinary":
            logger.debug("StorageService → CloudinaryStorage (Cloudinary)")
            return CloudinaryStorage()

        logger.debug("StorageService → LocalStorage (disk)")
        return LocalStorage()