# 🌱 Joyo Environment Mini App - Quick Start Guide

## 🎉 What Was Just Implemented

Your voice note concept has been transformed into a fully functional API! Here's what's ready:

### ✅ Phase 1 Complete: Backend Cleanup & Core Features
- ✅ Removed dev endpoints from FastAPI (keeping only official x402 routes)
- ✅ Fixed remedy endpoints in both Flask and FastAPI
- ✅ Added real Algorand NFT minting endpoint
- ✅ Created SQLite database with 9 tables
- ✅ Built 15+ core Joyo API endpoints

### ✅ Phase 2 Complete: Full Joyo Flow Implementation
- ✅ Plant registration & catalog
- ✅ Daily watering with video AI verification
- ✅ Health scanning with deficiency detection
- ✅ Organic remedy recommendations
- ✅ Protection/netting tracking
- ✅ Points ledger & rewards system
- ✅ Watering streaks with bonuses
- ✅ User history & plant tracking

---

## 📊 Database Schema

### Tables Created:
1. **users** - User accounts & total points/coins
2. **plants** - Registered plants with GPS & fingerprints
3. **activities** - All user activities (watering, scans, remedies)
4. **points_ledger** - Transaction history for all points
5. **streaks** - Watering streak tracking per plant
6. **health_scans** - AI health scan results
7. **remedies_applied** - Organic remedy applications
8. **coins** - Coin conversions & transactions
9. **nfts** - Minted NFTs on Algorand

---

## 🚀 How to Run

### 1. Install Dependencies

```bash
pip install fastapi uvicorn sqlite3 python-dotenv
pip install openai opencv-python pillow numpy
pip install x402  # Optional: for paid x402 routes
pip install py-algorand-sdk  # Optional: for NFT minting
```

### 2. Set Environment Variables

Create `.env` file:
```bash
# Required
OPENAI_API_KEY=your_openai_key

# Optional - for Algorand NFT minting
ALGOD_URL=https://testnet-api.algonode.cloud
ALGO_MNEMONIC=your_25_word_mnemonic
NFT_IMAGE_URL=ipfs://your_image_cid

# Optional - for x402 paid routes
ADDRESS=0x_your_payment_address

# Optional - for geo verification
GOOGLE_MAPS_API_KEY=your_key
OPENWEATHER_API_KEY=your_key
```

### 3. Initialize Database

```bash
python database.py
```

Output:
```
🗄️  Initializing Joyo Database...
✅ Database initialized successfully!
📊 Stats: {'total_users': 0, 'total_plants': 0, ...}
```

### 4. Start Core Joyo API Server

```bash
python api_joyo_core.py
```

Server runs on: **http://localhost:8001**

Interactive docs: **http://localhost:8001/docs**

### 5. (Optional) Start x402 Protected API

For paid AI services:
```bash
python api_fastapi_official_x402.py
```

Server runs on: **http://localhost:8000**

---

## 🌱 Complete User Flow - API Calls

### **Day 0: Plant Selection & Purchase (+30 points)**

```bash
# 1. Get plant catalog
curl http://localhost:8001/plants/catalog

# 2. Register plant
curl -X POST http://localhost:8001/plants/register \
  -F "user_id=USER001" \
  -F "plant_type=bamboo" \
  -F "location=Mumbai, Maharashtra, India" \
  -F "gps_latitude=19.0760" \
  -F "gps_longitude=72.8777" \
  -F "name=Satyam" \
  -F "email=satyam@example.com"

# Response:
{
  "success": true,
  "plant_id": "PLANT_A1B2C3D4",
  "points_earned": 30,
  "total_points": 30,
  "message": "Plant registered! You earned 30 points.",
  "next_step": "Upload planting photo to earn 20 more points"
}
```

### **Day 1: Planting Photo (+20 points)**

```bash
curl -X POST http://localhost:8001/plants/PLANT_A1B2C3D4/planting-photo \
  -F "image=@/path/to/plant_photo.jpg" \
  -F "gps_latitude=19.0760" \
  -F "gps_longitude=72.8777"

# Response:
{
  "success": true,
  "verified": true,
  "plant_species": "Bamboo",
  "confidence": 95,
  "points_earned": 20,
  "total_points": 50,
  "message": "Planting verified! You earned 20 points.",
  "next_step": "Water your plant daily to earn 5 points per day"
}
```

### **Day 2-30: Daily Watering (+5 points/day + streak bonuses)**

```bash
curl -X POST http://localhost:8001/plants/PLANT_A1B2C3D4/water \
  -F "video=@/path/to/watering_video.mp4" \
  -F "gps_latitude=19.0760" \
  -F "gps_longitude=72.8777"

# Response:
{
  "success": true,
  "verified": true,
  "points_earned": 5,
  "total_points": 55,
  "streak": {
    "current": 1,
    "longest": 1,
    "total_waterings": 1
  },
  "message": "Watering verified! You earned 5 points."
}

# Day 7 (Streak milestone):
{
  "points_earned": 15,  // 5 + 10 bonus
  "streak": {"current": 7},
  "message": "Watering verified! You earned 15 points. 🎉 Streak bonus: 10 points!"
}
```

### **Week 1: Health Scan (+5 points, max 2/week)**

```bash
curl -X POST http://localhost:8001/plants/PLANT_A1B2C3D4/health-scan \
  -F "image=@/path/to/plant_leaves.jpg"

# Response:
{
  "success": true,
  "health_score": 85,
  "overall_health": "Good",
  "issues_detected": ["nitrogen_deficiency"],
  "organic_remedies": [
    {
      "remedy_type": "Cow Dung Tea",
      "ingredients": ["1kg cow dung", "10 liters water"],
      "application": "Dilute 1:10 before applying"
    }
  ],
  "points_earned": 5,
  "total_points": 100,
  "message": "Health scan complete! You earned 5 points."
}
```

### **Day 12: Apply Remedy (+20-25 points)**

```bash
curl -X POST http://localhost:8001/plants/PLANT_A1B2C3D4/remedy-apply \
  -F "remedy_type=nitrogen_deficiency" \
  -F "image=@/path/to/remedy_application.jpg"

# Response:
{
  "success": true,
  "remedy_type": "nitrogen_deficiency",
  "points_earned": 25,
  "total_points": 125,
  "remedy_details": {
    "name": "Cow Dung Tea",
    "preparation": ["Mix cow dung in water", "Let it ferment for 3-5 days", ...],
    "application_frequency": "Once every 2 weeks"
  },
  "message": "Remedy applied! You earned 25 points."
}
```

### **Day 15: Add Protection (+10 points, one-time)**

```bash
curl -X POST http://localhost:8001/plants/PLANT_A1B2C3D4/protection \
  -F "protection_type=bamboo_netting" \
  -F "image=@/path/to/netting_photo.jpg"

# Response:
{
  "success": true,
  "protection_type": "bamboo_netting",
  "points_earned": 10,
  "total_points": 135,
  "message": "Protection added! You earned 10 points."
}
```

### **Check User Points & History**

```bash
# Get current points balance
curl http://localhost:8001/users/USER001/points

# Get full history
curl http://localhost:8001/users/USER001/history

# Get plant details
curl http://localhost:8001/plants/PLANT_A1B2C3D4
```

---

## 📈 Points Breakdown (6 Month Example)

| Activity | Points | Frequency | 6-Month Total |
|----------|--------|-----------|---------------|
| Plant Purchase | 30 | One-time | 30 |
| Planting Photo | 20 | One-time | 20 |
| Daily Watering | 5 | 180 days | 900 |
| 7-Day Streak Bonus | 10 | 25 times | 250 |
| 30-Day Streak Bonus | 50 | 6 times | 300 |
| Health Scans | 5 | 48 scans | 240 |
| Remedy Applications | 25 | 4 times | 100 |
| Protection/Netting | 10 | One-time | 10 |
| **TOTAL** | | | **1,850 points** |

**After 6 months**: 1,850 points → **1,850 Joyo Coins** (1:1 conversion)

---

## 🎯 What Still Needs Frontend Integration

### **Phase 3 - Frontend Updates Needed:**

1. **Update Worker UI** (`frontend/app/worker/page.tsx`):
   - Replace dev endpoints with new Joyo API calls
   - Add video recording for watering
   - Add plant catalog selection
   - Show points earned & streak info

2. **Create Joyo Dashboard**:
   - User points balance display
   - Plant care calendar
   - Streak tracker visualization
   - Activity history timeline

3. **Add Remedies UI**:
   - Display organic remedy recipes
   - Step-by-step application guide
   - Before/after photo upload

4. **CSR Dashboard** (NGO portal):
   - Connect to `/stats/csr` endpoint
   - Show total environmental impact
   - Display active users & plants

---

## 🔧 Testing the APIs

### Using Python requests:

```python
import requests

# Register plant
response = requests.post('http://localhost:8001/plants/register', data={
    'user_id': 'TEST_USER_001',
    'plant_type': 'bamboo',
    'location': 'Mumbai, India',
    'gps_latitude': 19.0760,
    'gps_longitude': 72.8777,
    'name': 'Test User'
})

print(response.json())

# Upload planting photo
with open('plant_photo.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8001/plants/PLANT_ID/planting-photo',
        files={'image': f},
        data={
            'gps_latitude': 19.0760,
            'gps_longitude': 72.8777
        }
    )

print(response.json())
```

### Using curl (see examples above)

### Using Postman:
1. Import: `http://localhost:8001/openapi.json`
2. Test each endpoint interactively

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Frontend (Next.js)                  │
│  • Worker Portal (plant care)               │
│  • NGO Dashboard (monitoring)               │
│  • Corporate Dashboard (CSR stats)          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Joyo Core API (FastAPI)                │
│      http://localhost:8001                  │
│                                             │
│  Endpoints:                                 │
│  • POST /plants/register                    │
│  • POST /plants/{id}/planting-photo         │
│  • POST /plants/{id}/water                  │
│  • POST /plants/{id}/health-scan            │
│  • POST /plants/{id}/remedy-apply           │
│  • POST /plants/{id}/protection             │
│  • GET  /users/{id}/points                  │
│  • GET  /users/{id}/history                 │
│  • GET  /stats/csr                          │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      AI Services (OpenAI GPT-4o)            │
│  • PlantRecognitionAI (species ID)          │
│  • PlantHealthAI (deficiency detection)     │
│  • PlantVerificationAI (same plant check)   │
│  • GeoVerificationAI (GPS consistency)      │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Database (SQLite)                      │
│  • users, plants, activities                │
│  • points_ledger, streaks                   │
│  • health_scans, remedies_applied           │
│  • coins, nfts                              │
└─────────────────────────────────────────────┘
```

---

## 🎓 Next Steps

### **Immediate (You can do now):**
1. ✅ Test core APIs using curl/Postman
2. ✅ Register test user & plant
3. ✅ Upload sample images/videos
4. ✅ Verify points are being tracked

### **Short-term (Frontend):**
1. Update Worker UI to call new APIs
2. Add video recording capability
3. Show real-time points & streaks
4. Display plant catalog

### **Medium-term (Features):**
1. Coin conversion flow (after 6 months)
2. Burn/donate coin options
3. CSR sponsor dashboard
4. Admin review portal

### **Long-term (Scale):**
1. Telegram bot integration
2. Mobile app (React Native)
3. NFT marketplace
4. Multi-language support

---

## 🐛 Troubleshooting

### Database not initializing?
```bash
rm joyo_app.db
python database.py
```

### AI services failing?
- Check `OPENAI_API_KEY` in `.env`
- Verify API key has GPT-4o access
- Check OpenAI API credits

### Video verification not working?
- Ensure `opencv-python` is installed
- Check video format (mp4, avi supported)
- Verify video file size < 50MB

### GPS verification failing?
- GPS coordinates must be within 50m of registered location
- Use actual device GPS, not manually entered coordinates
- Verify latitude/longitude format

---

## 📝 API Response Codes

- `200` - Success
- `400` - Bad request (invalid parameters)
- `404` - Resource not found (user/plant)
- `422` - Validation error (missing required fields)
- `500` - Server error (check logs)

---

## 🎉 Summary

**You now have a fully functional Joyo Environment Mini App backend!**

✅ **Database**: 9 tables tracking everything
✅ **APIs**: 15+ endpoints for complete user flow
✅ **AI**: Plant recognition, health scans, verification
✅ **Points**: Full ledger with streaks & bonuses
✅ **Blockchain**: Algorand NFT minting ready

**Voice Note Features Implemented:**
- ✅ Plant purchase & registration (+30 pts)
- ✅ Planting photo with AI verification (+20 pts)
- ✅ Daily watering videos with AI (+5 pts/day)
- ✅ Watering streaks with bonuses (7-day: +10, 30-day: +50)
- ✅ Weekly health scans (+5 pts, 2×/week)
- ✅ Organic remedy recommendations (+20-25 pts)
- ✅ Protection/netting tracking (+10 pts)
- ✅ Points ledger & transaction history
- ✅ GPS auto-tagging & location verification
- ✅ User & plant profiles

**Ready for:**
- Frontend integration
- Mobile app development
- Telegram bot
- CSR sponsor onboarding

---

## 💬 Need Help?

Check the interactive API docs:
- Core API: http://localhost:8001/docs
- x402 API: http://localhost:8000/docs

All endpoints have detailed descriptions and example requests!

---

**Made with 🌱 for the Environment**
