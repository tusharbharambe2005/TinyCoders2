# Testing Video Upload to Cloudinary

## Prerequisites

1. **Get Cloudinary Credentials** (Free)
   - Sign up at: https://cloudinary.com
   - Go to Dashboard and copy:
     - Cloud Name
     - API Key
     - API Secret

2. **Update your `.env` file**:
   ```bash
   STORAGE_BACKEND=cloudinary
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

3. **Install Cloudinary**:
   ```bash
   pip install cloudinary
   ```

4. **Start Django Server**:
   ```bash
   python manage.py runserver
   ```

---

## Testing with Postman

### Step 1: Create Emergency Case

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/emergency/start`
- Headers:
  - `Content-Type: application/json`
- Body (raw JSON):
  ```json
  {
    "user_phone": "+1234567890",
    "location_lat": 28.6139,
    "location_lng": 77.2090,
    "status": "active"
  }
  ```

**Response:** You'll get a `case_id` like:
```json
{
  "case_id": "5ea838ca-849e-4221-a892-433f18e9ae0e",
  "status": "active",
  ...
}
```

**Copy the `case_id` for next step!**

---

### Step 2: Upload Video to Cloudinary

**Request:**
- Method: `POST`
- URL: `http://localhost:8000/api/evidence/upload`
- Headers: (Postman sets this automatically for form-data)
- Body (form-data):
  - Key: `case_id` | Value: `YOUR_CASE_ID_FROM_STEP_1`
  - Key: `video_file` | Type: File | Select your video file

**How to add file in Postman:**
1. Select "Body" tab
2. Choose "form-data"
3. Add two rows:
   - `case_id` (Text) = paste your case_id
   - `video_file` (File) = Click "Select Files" and choose your video

**Response:** You'll get a Cloudinary URL:
```json
{
  "id": "...",
  "case_id": "...",
  "evidence_type": "video",
  "file_url": "https://res.cloudinary.com/your-cloud/video/upload/v1234567890/safesphere/evidence/case_xxx/video/abc123.mp4",
  "uploaded_at": "2026-03-05T10:30:00Z"
}
```

---

## Testing with Audio Files

Same process, just change:
- Use `audio_file` instead of `video_file`
- Upload `.mp3`, `.m4a`, or `.wav` file

Example form-data:
- `case_id` (Text) = your case_id
- `audio_file` (File) = Select your audio file

---

## Verify Upload

1. **Check Cloudinary Dashboard:**
   - Go to https://cloudinary.com
   - Click "Media Library"
   - Look for folder: `safesphere/evidence/case_xxx/video/`

2. **Test URL:**
   - Copy the `file_url` from response
   - Paste in browser - video should play!

---

## Where to Put Test Files?

You can put test video files anywhere on your computer. Common locations:

**macOS:**
- Desktop: `/Users/YOUR_USERNAME/Desktop/test_video.mp4`
- Downloads: `/Users/YOUR_USERNAME/Downloads/test_video.mp4`

**In Postman:** Just click "Select Files" and browse to your video file location.

---

## Troubleshooting

**Error: "Cloudinary credentials are missing"**
- Check your `.env` file has all three credentials
- Restart Django server after updating `.env`

**Error: "cloudinary module not found"**
- Run: `pip install cloudinary`

**Upload works but URL doesn't load:**
- Check Cloudinary Dashboard to verify file uploaded
- Make sure you're using the `secure_url` (https://)

**File too large:**
- Free Cloudinary tier supports up to 100MB per file
- Try a smaller test video first
