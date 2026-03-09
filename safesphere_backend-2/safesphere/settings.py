"""
SafeSphere Backend – Django Settings

DATABASE : Django built-in SQLite (zero config, works out of the box)
STORAGE  : Set STORAGE_BACKEND=local       → saves files on disk (media/ folder)
           Set STORAGE_BACKEND=cloudinary  → uploads to Cloudinary (free cloud storage)
AI       : Google Gemini API (gemini-1.5-flash)
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-safesphere-hackathon-2026")
DEBUG = os.getenv("DEBUG", "True") == "True"
ALLOWED_HOSTS = ["*"]

# ── Installed Apps ────────────────────────────────────────────────────────────
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    # SafeSphere apps
    "apps.users",
    "apps.emergency",
    "apps.evidence",
    "apps.fir",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "safesphere.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

WSGI_APPLICATION = "safesphere.wsgi.application"

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  DATABASE — Django built-in SQLite                                      ║
# ║  File: db.sqlite3 (auto-created on first migrate, no setup needed)      ║
# ╚══════════════════════════════════════════════════════════════════════════╝
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# ── REST Framework ────────────────────────────────────────────────────────────
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        # AllowAny for hackathon – change to IsAuthenticated in production
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

# ── CORS ──────────────────────────────────────────────────────────────────────
CORS_ALLOW_ALL_ORIGINS = True  # Hackathon only

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  FILE STORAGE — Choose your backend in .env                             ║
# ║                                                                          ║
# ║  STORAGE_BACKEND=local       → Saves to  media/evidence/  on this machine  ║
# ║  STORAGE_BACKEND=cloudinary  → Uploads to Cloudinary (free cloud storage)  ║
# ╚══════════════════════════════════════════════════════════════════════════╝

# Default: local storage (works with zero config)
STORAGE_BACKEND = os.getenv("STORAGE_BACKEND", "local")   # "local" | "cloudinary"

# Local storage paths (used when STORAGE_BACKEND=local)
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Cloudinary settings (used only when STORAGE_BACKEND=cloudinary)
# Get free account at: https://cloudinary.com
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY    = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  GEMINI AI — for FIR generation                                         ║
# ║  Get your key at: https://aistudio.google.com/app/apikey               ║
# ╚══════════════════════════════════════════════════════════════════════════╝
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# ── n8n Webhook ───────────────────────────────────────────────────────────────
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    "https://tusharbhaambe.app.n8n.cloud/webhook-test/safesphere-emergency"
)

# ── Static & Internationalization ─────────────────────────────────────────────
STATIC_URL = "static/"
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
