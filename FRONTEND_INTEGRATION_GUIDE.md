# 🚀 Frontend Integration Guide - Carbon Credit Blockchain

## 📍 Available Backend APIs

### **API 1: Joyo Core API** (Production Ready ✅)
**URL:** `https://joyo-cc-production.up.railway.app`
**Status:** 100% Tested & Working
**Purpose:** Daily plant care tracking & rewards

### **API 2: Unified Verification API** (New! 🎉)
**URL:** `http://localhost:8002` (Deploy to Railway needed)
**Status:** Ready for Testing
**Purpose:** Complete 7-stage verification pipeline

---

## 🎯 What Features Are Available

### ✅ READY TO USE (API 1 - Live on Railway)

#### 1. **Plant Management**
```javascript
// Register a plant
POST /plants/register
{
  user_id: "USER_123",
  name: "John Doe",
  email: "john@example.com",
  plant_type: "bamboo",
  location: "Mumbai, India",
  gps_latitude: 19.0760,
  gps_longitude: 72.8777
}
Response: {
  plant_id: "PLANT_ABC123",
  points_earned: 30,
  total_points: 30
}

// Get plant catalog
GET /plants/catalog
Response: {
  plants: {
    bamboo: { name: "Bamboo", co2_kg_per_year: 35 },
    tulsi: { name: "Tulsi", co2_kg_per_year: 12 },
    // ... 8 plant types
  }
}

// Get user's plants
GET /plants/user/{user_id}
Response: {
  total_plants: 5,
  plants: [...]
}

// Get plant details
GET /plants/{plant_id}
Response: {
  plant: {
    plant_type: "bamboo",
    health_score: 100,
    status: "active"
  }
}
```

#### 2. **Photo Uploads**
```javascript
// Upload planting photo (Webcam/Camera)
POST /plants/{plant_id}/planting-photo
FormData:
  - image: File (from webcam/camera)
  - gps_latitude: 19.0760
  - gps_longitude: 72.8777

Response: {
  success: true,
  points_earned: 20,
  total_points: 50
}
```

#### 3. **Daily Watering**
```javascript
// Record watering (Video Upload)
POST /plants/{plant_id}/water
FormData:
  - video: File (watering video from webcam)
  - gps_latitude: 19.0760
  - gps_longitude: 72.8777

Response: {
  success: true,
  points_earned: 5,
  streak: {
    current: 7,
    longest: 10,
    total_waterings: 45
  }
}
```

#### 4. **Health Scanning**
```javascript
// Scan plant health (Photo from Camera)
POST /plants/{plant_id}/health-scan
FormData:
  - image: File (plant photo)

Response: {
  health_score: 85,
  overall_health: "healthy",
  recommendations: ["Continue watering", "Add sunlight"],
  points_earned: 5
}
```

#### 5. **Points & Rewards**
```javascript
// Get user points
GET /users/{user_id}/points
Response: {
  points: {
    total_points: 240,
    lifetime_points: 450
  },
  level: {
    current_level: 3,
    level_name: "Plant Guardian"
  }
}

// Get transaction history
GET /users/{user_id}/history
Response: {
  transactions: [
    { type: "plant_purchase", points: 30 },
    { type: "planting_photo", points: 20 },
    { type: "watering", points: 5 }
  ]
}
```

#### 6. **Statistics**
```javascript
// System stats
GET /stats
Response: {
  total_users: 150,
  total_plants: 543,
  total_co2_offset_kg: 1250.5
}

// CSR Dashboard
GET /stats/csr
Response: {
  monthly_summary: {
    plants_registered: 45,
    active_workers: 32,
    co2_offset_kg: 342.5
  }
}
```

---

### 🆕 NEW FEATURES (API 2 - Unified Verification)

#### 1. **Complete 7-Stage Verification**
```javascript
// Single endpoint for complete verification
POST /verify/complete
FormData:
  - user_id: "USER_123"
  - plant_type: "bamboo"
  - location: "Mumbai"
  - gps_latitude: 19.0760
  - gps_longitude: 72.8777
  - trees_planted: 5
  - plant_image: File (plant photo)
  - gesture_video: File (webcam recording of gestures)

Response: {
  success: true,
  verification_stages: {
    plant_recognition: { success: true, confidence: 95 },
    plant_health: { health_score: 88 },
    geo_verification: { weather: { temp: 28 } },
    gesture_verification: { gesture_count: 5, signature: "..." },
    ai_validation: { valid: true, confidence: 85 }
  },
  verification_report: {
    overall_confidence: 87.5,
    passed_stages: ["Plant Recognition", "Health Scan", ...]
  },
  nft_result: {
    transaction_id: "ABC123...",
    asset_id: 748753679,
    explorer_url: "https://testnet.algoexplorer.io/asset/748753679"
  },
  database_record: {
    plant_id: "PLANT_XYZ",
    points_earned: 65
  }
}
```

#### 2. **Gesture Verification Only** (Webcam Feature)
```javascript
// Verify gestures from webcam
POST /verify/gesture
FormData:
  - user_id: "USER_123"
  - gesture_video: File (10-second webcam recording)

Response: {
  success: true,
  gesture_count: 7,
  signature: "biometric_hash...",
  confidence: 95.0
}
```

#### 3. **AI Fraud Detection**
```javascript
// Check if claim is fraudulent
POST /verify/fraud-check
FormData:
  - plant_type: "bamboo"
  - location: "Mumbai"
  - gps_latitude: 19.0760
  - gps_longitude: 72.8777
  - trees_planted: 5
  - plant_image: File (optional)

Response: {
  valid: true,
  confidence: 85,
  recommendation: "approve",
  risk_level: "low"
}
```

---

## 📱 Frontend Implementation Guide

### **Screen 1: Login/Registration**
```javascript
// No endpoint yet - needs to be built
// For now, frontend can generate user_id locally
const userId = `USER_${Date.now()}`;
localStorage.setItem('userId', userId);
```

### **Screen 2: Plant Catalog**
```javascript
// Fetch available plants
const catalog = await fetch('https://joyo-cc-production.up.railway.app/plants/catalog')
  .then(r => r.json());

// Display plants with:
// - Name
// - CO2 absorption rate
// - Difficulty level
// - Points multiplier
```

### **Screen 3: Register Plant**
```javascript
// User selects plant type from catalog
const formData = new FormData();
formData.append('user_id', userId);
formData.append('plant_type', 'bamboo');
formData.append('location', 'Mumbai, India');
formData.append('gps_latitude', position.coords.latitude);
formData.append('gps_longitude', position.coords.longitude);

const response = await fetch(
  'https://joyo-cc-production.up.railway.app/plants/register',
  { method: 'POST', body: formData }
);

const data = await response.json();
// Save plant_id for future use
localStorage.setItem(`plant_${data.plant_id}`, JSON.stringify(data));
```

### **Screen 4: Upload Planting Photo (Webcam)**
```javascript
// Capture photo from webcam
const stream = await navigator.mediaDevices.getUserMedia({ video: true });
const video = document.querySelector('video');
video.srcObject = stream;

// Capture frame
const canvas = document.createElement('canvas');
canvas.width = video.videoWidth;
canvas.height = video.videoHeight;
canvas.getContext('2d').drawImage(video, 0, 0);

// Convert to blob
canvas.toBlob(async (blob) => {
  const formData = new FormData();
  formData.append('image', blob, 'plant.jpg');
  formData.append('gps_latitude', latitude);
  formData.append('gps_longitude', longitude);
  
  const response = await fetch(
    `https://joyo-cc-production.up.railway.app/plants/${plantId}/planting-photo`,
    { method: 'POST', body: formData }
  );
  
  const data = await response.json();
  alert(`You earned ${data.points_earned} points!`);
}, 'image/jpeg');
```

### **Screen 5: Daily Watering (Video)**
```javascript
// Record video from webcam
const mediaRecorder = new MediaRecorder(stream);
const chunks = [];

mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
mediaRecorder.onstop = async () => {
  const blob = new Blob(chunks, { type: 'video/mp4' });
  
  const formData = new FormData();
  formData.append('video', blob, 'watering.mp4');
  formData.append('gps_latitude', latitude);
  formData.append('gps_longitude', longitude);
  
  const response = await fetch(
    `https://joyo-cc-production.up.railway.app/plants/${plantId}/water`,
    { method: 'POST', body: formData }
  );
  
  const data = await response.json();
  console.log('Streak:', data.streak);
};

// Start recording
mediaRecorder.start();
setTimeout(() => mediaRecorder.stop(), 5000); // 5 second video
```

### **Screen 6: Gesture Verification (NEW!)**
```javascript
// Record 10-second video of hand gestures
const stream = await navigator.mediaDevices.getUserMedia({ video: true });
const mediaRecorder = new MediaRecorder(stream);
const chunks = [];

// Show instructions: "Show thumbs up 3-4 times"
mediaRecorder.ondataavailable = (e) => chunks.push(e.data);
mediaRecorder.onstop = async () => {
  const blob = new Blob(chunks, { type: 'video/mp4' });
  
  const formData = new FormData();
  formData.append('user_id', userId);
  formData.append('gesture_video', blob, 'gesture.mp4');
  
  const response = await fetch(
    'http://localhost:8002/verify/gesture', // Deploy this to Railway!
    { method: 'POST', body: formData }
  );
  
  const data = await response.json();
  if (data.gesture_count >= 3) {
    alert('✅ Gesture verified!');
  } else {
    alert('❌ Please try again - show thumbs up clearly');
  }
};

mediaRecorder.start();
setTimeout(() => mediaRecorder.stop(), 10000); // 10 seconds
```

### **Screen 7: Complete Verification (All-in-One)**
```javascript
// Single API call for complete verification
const formData = new FormData();
formData.append('user_id', userId);
formData.append('plant_type', 'bamboo');
formData.append('location', 'Mumbai');
formData.append('gps_latitude', latitude);
formData.append('gps_longitude', longitude);
formData.append('trees_planted', 5);
formData.append('plant_image', plantPhotoBlob);
formData.append('gesture_video', gestureVideoBlob);

const response = await fetch(
  'http://localhost:8002/verify/complete',
  { method: 'POST', body: formData }
);

const data = await response.json();

// Show results:
// - Verification report
// - NFT minted
// - Points earned
// - All stage details
```

---

## 📊 Feature Comparison

| Feature | API 1 (Live) | API 2 (New) | Frontend Work |
|---------|--------------|-------------|---------------|
| Plant Registration | ✅ | ✅ | Simple form |
| Photo Upload (Webcam) | ✅ | ✅ | MediaDevices API |
| Video Upload (Webcam) | ✅ | ✅ | MediaRecorder API |
| GPS Location | ✅ | ✅ | Geolocation API |
| Points System | ✅ | ✅ | Display only |
| Gesture Verification | ❌ | ✅ | Video + Instructions |
| AI Fraud Detection | ❌ | ✅ | Background process |
| NFT Minting | ⚠️ Separate | ✅ Integrated | Display NFT link |
| Complete Pipeline | ❌ | ✅ | Single flow |

---

## 🎨 UI/UX Recommendations

### **Webcam Integration**
1. **Permission Request:** Ask for camera access with clear explanation
2. **Preview:** Show live camera feed before capture
3. **Countdown:** 3-2-1 countdown before photo/video capture
4. **Retake Option:** Allow users to retake if not satisfied
5. **Loading State:** Show "Processing..." during upload

### **Gesture Verification UI**
```
┌─────────────────────────────────┐
│     👍 Gesture Verification      │
├─────────────────────────────────┤
│                                 │
│   [Live Camera Preview]         │
│                                 │
│   Instructions:                 │
│   1. Show thumbs up gesture     │
│   2. Repeat 3-4 times           │
│   3. Keep hand visible          │
│                                 │
│   Detected: 2/3 ✋              │
│   Time: 5s remaining ⏱️         │
│                                 │
│   [Cancel] [Recording...🔴]     │
└─────────────────────────────────┘
```

### **Points Display**
```javascript
// Animated points counter
function animatePoints(from, to) {
  let current = from;
  const interval = setInterval(() => {
    current += 1;
    document.getElementById('points').textContent = current;
    if (current >= to) clearInterval(interval);
  }, 50);
}
```

---

## 🚀 Deployment Steps

### **Step 1: Deploy Unified API to Railway**
```bash
# Add to Procfile or railway.json
{
  "build": {
    "builder": "DOCKERFILE"
  },
  "deploy": {
    "startCommand": "uvicorn api_unified_verification:app --host 0.0.0.0 --port $PORT"
  }
}
```

### **Step 2: Update Frontend ENV**
```javascript
// config.js
const API_CONFIG = {
  CORE_API: 'https://joyo-cc-production.up.railway.app',
  UNIFIED_API: 'https://unified-verify-production.up.railway.app', // After deployment
  ENVIRONMENT: 'production'
};
```

### **Step 3: Test End-to-End**
1. Register plant ✅
2. Upload photo ✅
3. Record watering ✅
4. Verify gestures ✅
5. Mint NFT ✅

---

## 📞 Quick Reference

### **Live API (Ready Now)**
```
Base URL: https://joyo-cc-production.up.railway.app
Health: /health
Docs: /docs
Status: ✅ 100% Operational
```

### **New Unified API (Deploy Next)**
```
Base URL: http://localhost:8002 (local)
Deploy to: Railway
Features: 7-stage verification pipeline
Status: ⚠️ Needs deployment
```

---

## ✅ What Frontend Team Can Start NOW

1. ✅ Build plant catalog UI
2. ✅ Implement webcam photo capture
3. ✅ Create video recording for watering
4. ✅ Build points dashboard
5. ✅ Design user profile
6. ✅ Implement GPS location tracking

## ⏳ What Needs Backend Deployment First

1. ⏳ Gesture verification endpoint
2. ⏳ Complete 7-stage pipeline
3. ⏳ NFT minting integration
4. ⏳ AI fraud detection

---

**�� The backend is READY! Frontend team can start building immediately!**
