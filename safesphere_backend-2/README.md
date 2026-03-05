# SafeSphere – Intelligent Evidence & Auto-Response System
### Backend API · Django + SQLite · Hackathon Edition

---

## What Changed From Default Setup

| Item | This Project |
|---|---|
| **Database** | Django built-in **SQLite** — zero config, auto-created |
| **Storage Option 1** | **Local** — files saved to `media/evidence/` on disk |
| **Storage Option 2** | **Cloud** — files uploaded to **AWS S3** |
| **AI** | **Google Gemini API** (`gemini-1.5-flash`) |

---

## Architecture

```
Frontend (SOS Trigger)
        │
        ▼
┌──────────────────────────────────────────────┐
│             SafeSphere Backend                │
│                                              │
│  POST /api/emergency/start  → EmergencyCase  │
│  POST /api/evidence/upload  → Evidence DB    │
│         │                                    │
│         └──► WebhookService → n8n Webhook    │
│                                    │         │
│                              ┌─────┴──────┐  │
│                              │    n8n     │  │
│                              │ 1. Alert   │  │
│                              │   Contacts │  │
│                              │ 2. Gemini  │  │
│                              │   FIR Gen  │  │
│                              └─────┬──────┘  │
│                                    │         │
│  POST /api/fir/save  ←─────────────┘         │
│  GET  /api/case/<id> → Full Case Details     │
└──────────────────────────────────────────────┘

Storage:
  STORAGE_BACKEND=local  → media/evidence/ (disk)
  STORAGE_BACKEND=cloud  → AWS S3 bucket
```

---

## Quick Start (5 minutes)

### Step 1 — Create virtual environment
```bash
cd safesphere_backend
python -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Configure environment
```bash
cp .env.example .env
```

Minimum config for local development (edit `.env`):
```env
SECRET_KEY=any-random-string-here
DEBUG=True
STORAGE_BACKEND=local
GEMINI_API_KEY=your-gemini-key-here
N8N_WEBHOOK_URL=http://localhost:5678/webhook/safesphere-emergency
```
> Get a free Gemini key at: https://aistudio.google.com/app/apikey

### Step 4 — Run database migrations
```bash
# SQLite db.sqlite3 is created automatically — no database setup needed

python manage.py makemigrations users
python manage.py makemigrations emergency
python manage.py makemigrations evidence
python manage.py makemigrations fir
python manage.py migrate
```

### Step 5 — Start the server
```bash
python manage.py runserver
```
API is live at **http://localhost:8000** ✅

---

## Storage Backend — Choose One

### Option 1: Local Storage (default)
Files are saved to `media/evidence/` on your machine.

```env
STORAGE_BACKEND=local
```
- ✅ Zero config — works immediately
- ✅ Files accessible at `http://localhost:8000/media/...`
- ⚠️  Files lost if server machine is wiped

### Option 2: Cloud Storage (AWS S3)
Files are uploaded to your AWS S3 bucket.

```env
STORAGE_BACKEND=cloud
AWS_ACCESS_KEY_ID=your-key-id
AWS_SECRET_ACCESS_KEY=your-secret
AWS_STORAGE_BUCKET=safesphere-evidence
AWS_S3_REGION=ap-south-1
```
- ✅ Persistent across restarts
- ✅ Suitable for live demos on cloud-hosted servers
- ⚠️  Requires AWS account + S3 bucket

---

## API Reference

### 1. Register User
```
POST /api/users/register
```
```json
{
    "name": "Anita Sharma",
    "phone": "9999999999",
    "email": "anita@example.com",
    "device_id": "android-abc123"
}
```
**Response:**
```json
{
    "message": "User registered successfully.",
    "user_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

---

### 2. Add Trusted Contact
```
POST /api/users/trusted-contact
```
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "contact_name": "Priya Patel",
    "contact_phone": "9876543210",
    "contact_email": "priya@example.com"
}
```

---

### 3. Start Emergency
```
POST /api/emergency/start
```
```json
{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "latitude": 18.5204,
    "longitude": 73.8567,
    "timestamp": "2026-03-05T12:00:00"
}
```
**Response:**
```json
{
    "case_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "status": "active"
}
```

---

### 4. Upload Evidence
```
POST /api/evidence/upload
Content-Type: multipart/form-data
```
| Field | Type | Required |
|---|---|---|
| case_id | UUID string | ✅ |
| video_file | file | optional |
| audio_file | file | optional |
| latitude | decimal | ✅ |
| longitude | decimal | ✅ |
| timestamp | ISO8601 string | ✅ |

**cURL example:**
```bash
curl -X POST http://localhost:8000/api/evidence/upload \
  -F "case_id=6ba7b810-9dad-11d1-80b4-00c04fd430c8" \
  -F "video_file=@/path/to/video.mp4" \
  -F "audio_file=@/path/to/audio.m4a" \
  -F "latitude=18.5204" \
  -F "longitude=73.8567" \
  -F "timestamp=2026-03-05T12:01:30"
```

After upload → n8n webhook fires automatically.

---

### 5. Generate FIR via Gemini (direct, no n8n needed)
```
POST /api/fir/generate
```
```json
{
    "case_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "audio_transcript": "Help! Someone is following me.",
    "video_description": "Deserted street at night, figure following closely."
}
```

---

### 6. Save FIR Draft (called by n8n)
```
POST /api/fir/save
```
```json
{
    "case_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "fir_text": "FIRST INFORMATION REPORT\n\nPolice Station: ..."
}
```

---

### 7. Get Full Case Details
```
GET /api/case/6ba7b810-9dad-11d1-80b4-00c04fd430c8
```
**Response:**
```json
{
    "case_id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
    "user_name": "Anita Sharma",
    "latitude": "18.5204000",
    "longitude": "73.8567000",
    "timestamp": "2026-03-05T12:00:00Z",
    "status": "active",
    "evidence_files": [
        {
            "file_type": "video",
            "file_url": "/media/evidence/case_xxx/video/abc123.mp4"
        }
    ],
    "fir_text": "FIRST INFORMATION REPORT\n\n..."
}
```

---

## Project Structure

```
safesphere_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── README.md
├── db.sqlite3                    ← auto-created on first migrate
├── media/                        ← local evidence files (local storage)
│   └── evidence/
├── safesphere/
│   ├── settings.py               ← SQLite + storage config
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── users/                    ← User + TrustedContact
    ├── emergency/                ← EmergencyCase
    ├── evidence/                 ← Evidence upload
    ├── fir/                      ← FIR save/generate/retrieve
    └── services/
        ├── storage_service.py    ← LocalStorage | CloudStorage + factory
        ├── gemini_service.py     ← Gemini FIR generation
        └── webhook_service.py    ← n8n webhook trigger
```

---

## n8n Webhook Payload

The backend sends this JSON to n8n on every evidence upload:
```json
{
    "case_id": "...",
    "user_name": "Anita",
    "user_phone": "9999999999",
    "user_email": "anita@example.com",
    "latitude": "18.5204",
    "longitude": "73.8567",
    "timestamp": "2026-03-05T12:00:00",
    "evidence_url": "http://localhost:8000/media/evidence/...",
    "evidence_count": 2,
    "trusted_contacts": [
        { "name": "Priya", "phone": "9876543210", "email": "priya@example.com" }
    ]
}
```
