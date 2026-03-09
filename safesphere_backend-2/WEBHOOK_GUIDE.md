# n8n Webhook Integration Guide

## Overview

When a video/audio is uploaded via `/api/evidence/upload`, the backend automatically triggers an n8n webhook with emergency case details. This webhook can be used to:

1. Send SMS/Email alerts to trusted contacts
2. Generate FIR report using AI
3. Notify police stations
4. Store data in external systems

---

## Webhook Payload Structure

### Example Payload Sent to n8n:

```json
{
  "case_id": "403e07b2-c1e5-4a0d-9db2-0a6010b3c3c5",
  "user_name": "Anita Sharma",
  "user_phone": "+919876543210",
  "user_email": "anita@example.com",
  "video_url": "https://res.cloudinary.com/dufpqxo64/video/upload/v1772701455/safesphere/evidence/case_403e07b2-c1e5-4a0d-9db2-0a6010b3c3c5/video/ovdzon2kb2nkr4ioyjs8.mp4",
  "location_description": "Location: 18.5204, 73.8567",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "start_time": "2026-03-05T21:16:00",
  "end_time": "2026-03-05T21:16:00",
  "police_station_name": "Nearest Police Station",
  "evidence_count": 1,
  "trusted_contacts": [
    {
      "name": "Priya Sharma",
      "phone": "+919876543211",
      "email": "priya@example.com"
    },
    {
      "name": "Raj Kumar",
      "phone": "+919876543212",
      "email": "raj@example.com"
    }
  ]
}
```

### Payload Fields:

| Field | Type | Description |
|-------|------|-------------|
| `case_id` | string (UUID) | Unique emergency case identifier |
| `user_name` | string | Name of the person in emergency |
| `user_phone` | string | Phone number of the user |
| `user_email` | string | Email of the user |
| `video_url` | string | Cloudinary URL of uploaded video/audio |
| `location_description` | string | Human-readable location description |
| `latitude` | float | GPS latitude coordinate |
| `longitude` | float | GPS longitude coordinate |
| `start_time` | string (ISO 8601) | When emergency started |
| `end_time` | string (ISO 8601) | When evidence was uploaded |
| `police_station_name` | string | Nearest police station name |
| `evidence_count` | integer | Number of files uploaded |
| `trusted_contacts` | array | List of emergency contacts to notify |

---

## Setting Up n8n Webhook

### Step 1: Create n8n Workflow

1. Go to https://n8n.io or your self-hosted n8n instance
2. Create a new workflow
3. Add a "Webhook" node as the trigger

### Step 2: Configure Webhook Node

**Webhook Settings:**
- Method: `POST`
- Path: `safesphere-emergency` (or any custom path)
- Response Mode: `On Received`
- Response Code: `200`

**Copy the webhook URL** - it will look like:
```
https://your-n8n-instance.com/webhook/safesphere-emergency
```

### Step 3: Update Backend Configuration

Add the webhook URL to your `.env` file:

```bash
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/safesphere-emergency
```

Restart Django server:
```bash
python manage.py runserver
```

---

## Example n8n Workflows

### Workflow 1: Send SMS Alerts to Trusted Contacts

```
1. Webhook Trigger (receives payload)
   ↓
2. Split Out (loop through trusted_contacts array)
   ↓
3. Twilio SMS Node
   - To: {{ $json.phone }}
   - Message: "EMERGENCY ALERT! {{ $node["Webhook"].json.user_name }} needs help at {{ $node["Webhook"].json.location_description }}. Video: {{ $node["Webhook"].json.video_url }}"
```

### Workflow 2: Generate FIR Report with AI

```
1. Webhook Trigger
   ↓
2. HTTP Request to Gemini API
   - Method: POST
   - URL: https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent
   - Body: {
       "contents": [{
         "parts": [{
           "text": "Generate FIR report for: User {{ $json.user_name }}, Location: {{ $json.location_description }}, Time: {{ $json.start_time }}"
         }]
       }]
     }
   ↓
3. HTTP Request to Backend
   - Method: POST
   - URL: http://your-backend/api/fir/save
   - Body: {
       "case_id": "{{ $node["Webhook"].json.case_id }}",
       "fir_text": "{{ $json.candidates[0].content.parts[0].text }}"
     }
```

### Workflow 3: Email Alert with Video Link

```
1. Webhook Trigger
   ↓
2. Gmail Node (or SendGrid)
   - To: {{ $json.trusted_contacts[0].email }}
   - Subject: "🚨 EMERGENCY ALERT - {{ $json.user_name }}"
   - Body: 
     "Emergency reported by {{ $json.user_name }}
     
     Location: {{ $json.location_description }}
     Time: {{ $json.start_time }}
     
     Video Evidence: {{ $json.video_url }}
     
     Please respond immediately!"
```

---

## Testing the Webhook

### Test 1: Using Postman to Simulate Upload

1. **Create Emergency Case:**
```
POST http://localhost:8000/api/emergency/start
Body: {
  "user_id": "your-user-id",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "timestamp": "2026-03-05T21:16:00"
}
```

2. **Upload Video (triggers webhook):**
```
POST http://localhost:8000/api/evidence/upload
Body (form-data):
  - case_id: "case-id-from-step-1"
  - video_file: <select video file>
  - latitude: 18.5204
  - longitude: 73.8567
  - timestamp: "2026-03-05T21:16:00"
```

3. **Check n8n Workflow Executions:**
   - Go to n8n dashboard
   - Click "Executions" tab
   - You should see the webhook was triggered
   - View the payload received

### Test 2: Using webhook.site for Testing

If you don't have n8n set up yet:

1. Go to https://webhook.site
2. Copy the unique URL (e.g., `https://webhook.site/abc123`)