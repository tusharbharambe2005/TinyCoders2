# SafeSphere API Endpoints

## 🆕 NEW: Get or Create User by Phone

### Endpoint
```
POST http://localhost:8000/api/users/get-or-create
```

### Description
- If user with phone exists → returns existing user_id
- If user doesn't exist → creates new user and returns user_id
- Perfect for Flutter app login/registration flow

### Request Body (JSON)
```json
{
  "phone": "+1234567890",
  "name": "John Doe",           // Optional (used only if creating new user)
  "email": "john@example.com"   // Optional (used only if creating new user)
}
```

### Response (Existing User)
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "created": false
}
```

### Response (New User Created)
```json
{
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "phone": "+1234567890",
  "name": "John Doe",
  "email": "john@example.com",
  "created": true
}
```

---

## Complete Flow for Flutter App

### 1. Get/Create User by Phone
```
POST /api/users/get-or-create
Body: { "phone": "+1234567890", "name": "John Doe" }
Response: { "user_id": "uuid-here", "created": true/false }
```

### 2. Create Emergency Case
```
POST /api/emergency/start
Body: {
  "user_id": "uuid-from-step-1",
  "latitude": 28.6139,
  "longitude": 77.2090,
  "timestamp": "2026-03-05T12:00:00"
}
Response: { "case_id": "case-uuid-here" }
```

### 3. Upload Video Evidence
```
POST /api/evidence/upload
Body (form-data):
  - case_id: "case-uuid-from-step-2"
  - video_file: <file>
Response: { "file_url": "https://res.cloudinary.com/..." }
```

---

## Test in Postman

### Test 1: First Time User (Creates New)
1. Method: `POST`
2. URL: `http://localhost:8000/api/users/get-or-create`
3. Body (raw JSON):
```json
{
  "phone": "+9876543210",
  "name": "Test User",
  "email": "test@example.com"
}
```
4. Expected: `"created": true` and new `user_id`

### Test 2: Existing User (Returns Same)
1. Use same phone number again
2. Expected: `"created": false` and same `user_id`

### Test 3: Minimal Request (Phone Only)
```json
{
  "phone": "+1112223333"
}
```
Expected: Creates user with auto-generated name and email

---

## Flutter Implementation Example

```dart
class ApiService {
  static const String baseUrl = 'http://YOUR_IP:8000';
  
  // Get or create user by phone
  Future<String> getOrCreateUser(String phone, {String? name, String? email}) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/users/get-or-create'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'phone': phone,
        if (name != null) 'name': name,
        if (email != null) 'email': email,
      }),
    );
    
    if (response.statusCode == 200 || response.statusCode == 201) {
      final data = jsonDecode(response.body);
      return data['user_id'];  // Return user_id for next API calls
    } else {
      throw Exception('Failed to get/create user');
    }
  }
  
  // Create emergency case
  Future<String> createEmergency(String userId, double lat, double lng) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/emergency/start'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'user_id': userId,
        'latitude': lat,
        'longitude': lng,
        'timestamp': DateTime.now().toIso8601String(),
      }),
    );
    
    if (response.statusCode == 201) {
      final data = jsonDecode(response.body);
      return data['case_id'];
    } else {
      throw Exception('Failed to create emergency');
    }
  }
  
  // Upload video
  Future<String> uploadVideo(String caseId, File videoFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/evidence/upload'),
    );
    
    request.fields['case_id'] = caseId;
    request.files.add(await http.MultipartFile.fromPath(
      'video_file',
      videoFile.path,
    ));
    
    final response = await request.send();
    final responseData = await response.stream.bytesToString();
    
    if (response.statusCode == 201) {
      final data = jsonDecode(responseData);
      return data['uploaded_files'][0]['file_url'];
    } else {
      throw Exception('Failed to upload video');
    }
  }
}

// Usage in your Flutter app:
void triggerEmergency() async {
  try {
    // Step 1: Get user_id
    String userId = await apiService.getOrCreateUser(
      '+1234567890',
      name: 'John Doe',
    );
    
    // Step 2: Create emergency case
    String caseId = await apiService.createEmergency(
      userId,
      28.6139,
      77.2090,
    );
    
    // Step 3: Upload video
    File videoFile = File('/path/to/video.mp4');
    String videoUrl = await apiService.uploadVideo(caseId, videoFile);
    
    print('Emergency created! Video: $videoUrl');
  } catch (e) {
    print('Error: $e');
  }
}
```

---

## All Available Endpoints

### Users
- `POST /api/users/get-or-create` - Get or create user by phone ⭐ NEW
- `POST /api/users/register` - Register new user
- `GET /api/users/<user_id>` - Get user details
- `POST /api/users/trusted-contact` - Add trusted contact

### Emergency
- `POST /api/emergency/start` - Create emergency case
- `GET /api/case/<case_id>` - Get case details
- `PATCH /api/emergency/<case_id>/status` - Update case status

### Evidence
- `POST /api/evidence/upload` - Upload video/audio
- `GET /api/evidence/<case_id>` - List all evidence for case

### FIR
- `POST /api/fir/generate` - Generate FIR report
- `GET /api/fir/<case_id>` - Get FIR report
