#!/usr/bin/env python3
"""
Quick test script for video upload to Cloudinary.

Usage:
    python test_upload.py /path/to/your/video.mp4
"""
import sys
import requests
import json

BASE_URL = "http://localhost:8000"

def create_emergency_case():
    """Step 1: Create an emergency case"""
    print("📱 Creating emergency case...")
    
    url = f"{BASE_URL}/api/emergency/start"
    data = {
        "user_phone": "+1234567890",
        "location_lat": 28.6139,
        "location_lng": 77.2090,
        "status": "active"
    }
    
    response = requests.post(url, json=data)
    
    if response.status_code in [200, 201]:
        case_data = response.json()
        case_id = case_data.get("case_id")
        print(f"✅ Emergency case created: {case_id}")
        return case_id
    else:
        print(f"❌ Failed to create case: {response.status_code}")
        print(response.text)
        return None


def upload_video(case_id, video_path):
    """Step 2: Upload video to the case"""
    print(f"\n📹 Uploading video: {video_path}")
    
    url = f"{BASE_URL}/api/evidence/upload"
    
    # Prepare form data
    data = {
        "case_id": case_id
    }
    
    try:
        with open(video_path, "rb") as video_file:
            files = {"video_file": video_file}
            response = requests.post(url, data=data, files=files)
        
        if response.status_code in [200, 201]:
            evidence_data = response.json()
            file_url = evidence_data.get("file_url")
            print(f"✅ Video uploaded successfully!")
            print(f"\n🔗 Cloudinary URL:")
            print(f"   {file_url}")
            print(f"\n💡 Open this URL in your browser to view the video")
            return file_url
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return None
            
    except FileNotFoundError:
        print(f"❌ File not found: {video_path}")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def main():
    print("=" * 60)
    print("🧪 SafeSphere - Cloudinary Video Upload Test")
    print("=" * 60)
    
    # Check if video path provided
    if len(sys.argv) < 2:
        print("\n❌ Please provide video file path")
        print("\nUsage:")
        print("  python test_upload.py /path/to/video.mp4")
        print("\nExample:")
        print("  python test_upload.py ~/Desktop/test_video.mp4")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    # Check if server is running
    try:
        requests.get(BASE_URL, timeout=2)
    except requests.exceptions.ConnectionError:
        print("\n❌ Django server is not running!")
        print("Please start it first:")
        print("  python manage.py runserver")
        sys.exit(1)
    
    # Step 1: Create case
    case_id = create_emergency_case()
    if not case_id:
        sys.exit(1)
    
    # Step 2: Upload video
    file_url = upload_video(case_id, video_path)
    if not file_url:
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
