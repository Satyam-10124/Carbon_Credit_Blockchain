# 🌐 API ENDPOINTS - Quick Reference for Frontend

**Base URL:** `https://your-app.up.railway.app` (update after deployment)

---

## 📋 CORE ENDPOINTS

### Health & Info
- `GET /` - API information
- `GET /health` - Health check

### Plants
- `GET /plants/catalog` - List available plants (NO AUTH)
- `POST /plants/register` - Register new plant
- `GET /plants/{plant_id}` - Get plant details
- `GET /plants/user/{user_id}` - Get user's plants
- `POST /plants/{plant_id}/planting-photo` - Upload photo

### Activities
- `POST /plants/{plant_id}/water` - Record watering (+5 pts)
- `POST /plants/{plant_id}/health-scan` - Health scan (+5 pts, max 2/week)
- `POST /plants/{plant_id}/remedy-apply` - Apply remedy (+20-25 pts)
- `POST /plants/{plant_id}/protection` - Add protection (+10 pts)

### Rewards
- `GET /users/{user_id}/points` - Get points balance
- `GET /users/{user_id}/history` - Points transaction history
- `POST /coins/convert` - Convert points to coins (after 6 months)

### Stats
- `GET /stats` - Overall system statistics
- `GET /stats/csr` - CSR dashboard data

---

## 🔑 REQUEST EXAMPLES

### TypeScript/React
```typescript
// Health Check
const health = await fetch(`${API_URL}/health`);
const data = await health.json();

// Register Plant
const formData = new FormData();
formData.append('user_id', 'USER123');
formData.append('plant_type', 'bamboo');
formData.append('location', 'Mumbai, India');
formData.append('gps_latitude', '19.0760');
formData.append('gps_longitude', '72.8777');

const response = await fetch(`${API_URL}/plants/register`, {
  method: 'POST',
  body: formData
});

// Record Watering
const waterData = new FormData();
waterData.append('gps_latitude', '19.0760');
waterData.append('gps_longitude', '72.8777');

const waterResponse = await fetch(`${API_URL}/plants/PLANT_123/water`, {
  method: 'POST',
  body: waterData
});
```

---

## 📝 RESPONSE FORMATS

### Success Response
```json
{
  "success": true,
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2025-11-22T12:00:00"
}
```

### Error Response
```json
{
  "success": false,
  "error": "error_code",
  "message": "Human readable error message",
  "details": {...}
}
```

---

## 🚀 FRONTEND INTEGRATION CHECKLIST

- [ ] Update `NEXT_PUBLIC_API_URL` in `.env.local`
- [ ] Test all endpoints with Postman/curl
- [ ] Handle loading states
- [ ] Handle error states
- [ ] Show success messages
- [ ] Add retry logic for failed requests
- [ ] Implement request timeout (30 seconds)
- [ ] Add request/response logging (dev only)

---

## ⚡ RATE LIMITS (After deployment)
- General: 100 requests/hour per IP
- Plant registration: 10/minute per IP
- Watering: 1/day per plant
- Health scan: 2/week per plant

---

## 📞 SUPPORT
For API issues: Check logs with `railway logs`  
For bugs: Create GitHub issue  
For questions: team@carbonchain.io
