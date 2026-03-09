# Webhook Payload Guide

## What is the Webhook?

When a video/audio is uploaded via `/api/evidence/upload`, the backend automatically sends a webhook to n8n with all emergency details. This allows you to:

- Send SMS/Email alerts to trusted contacts
- Generate FIR reports using AI
- Notify police stations
- Store data in external systems

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
  "start_time": "2026-03-05T21:16:00+05:30",
  "end_time": "2026-03-05T21:16:00+05:30",
  "police_station_name": "Nearest Police Station",
  "evidence_count": 1,
  "trusted_contacts": [
    {
      "name": "Priya Sharma",
      "phone": "+919876543211",
      "email": "priya@example.com"
    }
  ]
}
```

---

## How to Use This Payload

### Option 1: Test with webhook.site (No Setup Required)

1. Go to https://webhook.site
2. Copy your unique URL (e.g., `https://webhook.site/abc123`)
3. Update `.env`:
   ```bash
   N8N_WEBHOOK_URL=https://webhook.site/abc123
   ```
4. Restart Django server
5. Upload a video via Postman
6. Go back to webhook.site - you'll see the payload!

### Option 2: Use n8n for Automation

Your current n8n URL:
```
https://tusharbhaambe.app.n8n.cloud/webhook/bb8e3fe1-2014-49e6-863c-333ca910d1d8
```

**In n8n:**

1. Create a new workflow
2. Add "Webhook" trigger node
3. Set path to match your URL
4. Add nodes to process the data:

**Example: Send SMS Alert**
```
Webhook → Split Out (trusted_contacts) → Twilio SMS
```

**Example: Send Email**
```
Webhook → Gmail/SendGrid → Send email with video_url
```

**Example: Generate FIR with AI**
```
Webhook → HTTP Request (Gemini API) → HTTP Request (POST back to /api/fir/save)
```

---

## Accessing Payload Fields in n8n

In n8n nodes, use these expressions:

```javascript
{{ $json.case_id }}              // "403e07b2-c1e5-4a0d-9db2-0a6010b3c3c5"
{{ $json.user_name }}            // "Anita Sharma"
{{ $json.user_phone }}           // "+919876543210"
{{ $json.video_url }}            // Cloudinary URL
{{ $json.latitude }}             // 18.5204
{{ $json.longitude }}            // 73.8567
{{ $json.start_time }}           // "2026-03-05T21:16:00+05:30"
{{ $json.police_station_name }}  // "Nearest Police Station"
{{ $json.evidence_count }}       // 1

// Loop through trusted contacts:
{{ $json.trusted_contacts[0].name }}   // First contact name
{{ $json.trusted_contacts[0].phone }}  // First contact phone
```

---

## Example n8n Workflow: Send SMS to All Contacts

```
1. Webhook Trigger
   ↓
2. Split Out Node
   - Field to Split Out: trusted_contacts
   ↓
3. Twilio SMS Node
   - To: {{ $json.phone }}
   - Message: 
     "🚨 EMERGENCY ALERT!
     
     {{ $node["Webhook"].json.user_name }} needs help!
     
     Location: {{ $node["Webhook"].json.location_description }}
     Time: {{ $node["Webhook"].json.start_time }}
     
     Video Evidence: {{ $node["Webhook"].json.video_url }}
     
     Please respond immediately!"
```

---

## Disabling Webhook (Optional)

If you don't want to use webhooks, leave it empty in `.env`:

```bash
N8N_WEBHOOK_URL=
```

The system will skip webhook calls and just upload the video.

---

## Testing the Complete Flow

### Step 1: Create User
```bash
POST http://localhost:8000/api/users/get-or-create
Body: { "phone": "+919876543210", "name": "Anita Sharma" }
Response: { "user_id": "uuid-here" }
```

### Step 2: Add Trusted Contact (Optional)
```bash
POST http://localhost:8000/api/users/trusted-contact
Body: {
  "user_id": "uuid-from-step-1",
  "contact_name": "Priya Sharma",
  "contact_phone": "+919876543211",
  "contact_email": "priya@example.com"
}
```

### Step 3: Create Emergency
```bash
POST http://localhost:8000/api/emergency/start
Body: {
  "user_id": "uuid-from-step-1",
  "latitude": 18.5204,
  "longitude": 73.8567,
  "timestamp": "2026-03-05T21:16:00"
}
Response: { "case_id": "case-uuid-here" }
```

### Step 4: Upload Video (Triggers Webhook)
```bash
POST http://localhost:8000/api/evidence/upload
Body (form-data):
  - case_id: "case-uuid-from-step-3"
  - video_file: <select video>
  - latitude: 18.5204
  - longitude: 73.8567
```

**Result:** 
- Video uploaded to Cloudinary
- Webhook sent to n8n with all details
- n8n can send SMS/emails automatically

---

## Troubleshooting

**Error: "Could not connect to n8n webhook"**
- Check if n8n is running
- Verify the webhook URL is correct
- Test URL in browser or Postman first
- This is just a warning - video still uploads successfully

**Timezone Warning**
- Fixed! The code now handles timezone-aware datetimes

**Webhook not triggering**
- Check n8n workflow is active (toggle switch ON)
- Check webhook path matches your URL
- Use webhook.site to test if payload is being sent
