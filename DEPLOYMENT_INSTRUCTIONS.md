# 🚀 PRODUCTION DEPLOYMENT GUIDE
## Deploy Carbon Credit API to Railway

---

## 📋 PRE-DEPLOYMENT CHECKLIST

### ✅ Required Environment Variables
Make sure you have these ready:

```bash
# CRITICAL - Database
DATABASE_URL=postgresql://user:pass@host:port/dbname

# CRITICAL - Blockchain
ALGO_MNEMONIC=your 25 word mnemonic here
ALGO_NETWORK=testnet  # or mainnet
ALGOD_URL=https://testnet-api.algonode.cloud
NFT_IMAGE_URL=https://your-cdn.com/default-nft.jpg

# CRITICAL - AI Services
OPENAI_API_KEY=sk-proj-...

# OPTIONAL - External APIs
OPENWEATHER_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
PLANET_API_KEY=your_key_here

# OPTIONAL - x402 Payment
PAYMENT_ADDRESS=0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0
X402_FACILITATOR_URL=https://facilitator.base.org
NETWORK=base

# OPTIONAL - File Storage
UPLOAD_DIR=/tmp/joyo_uploads
```

---

## 🚂 DEPLOY TO RAILWAY (Recommended)

### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
# or
brew install railway
```

### Step 2: Login to Railway
```bash
railway login
```

### Step 3: Initialize Project
```bash
cd /Users/satyamsinghal/Desktop/Face_Cascade/Carbon_Credit_Blockchain
railway init
```

### Step 4: Link to Existing Project (or create new)
```bash
# If you have existing Railway project
railway link

# Or create new project
railway init
```

### Step 5: Set Environment Variables
```bash
# Set all required variables
railway variables set DATABASE_URL="postgresql://..."
railway variables set ALGO_MNEMONIC="your 25 words"
railway variables set ALGO_NETWORK="testnet"
railway variables set ALGOD_URL="https://testnet-api.algonode.cloud"
railway variables set NFT_IMAGE_URL="https://your-cdn.com/nft.jpg"
railway variables set OPENAI_API_KEY="sk-proj-..."

# Optional variables
railway variables set OPENWEATHER_API_KEY="your_key"
railway variables set GOOGLE_MAPS_API_KEY="your_key"
railway variables set PAYMENT_ADDRESS="0x742d35..."
```

### Step 6: Deploy!
```bash
railway up
```

### Step 7: Get Your Live URL
```bash
railway domain
# Output: https://your-app.up.railway.app
```

---

## 🌐 ALTERNATIVE: Railway Web Interface

### Option 1: Deploy from GitHub

1. **Push to GitHub:**
```bash
git add Dockerfile railway.json .dockerignore
git commit -m "Add Railway deployment config"
git push origin main
```

2. **Go to Railway:**
   - Visit https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

3. **Configure:**
   - Railway auto-detects `railway.json`
   - Set environment variables in Railway dashboard
   - Click "Deploy"

### Option 2: Deploy from Local

1. Go to https://railway.app
2. Click "New Project" → "Deploy from CLI"
3. Follow CLI instructions above

---

## 🐳 DOCKER LOCAL TESTING

### Build Image
```bash
docker build -t carbon-credit-api .
```

### Run Locally
```bash
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e ALGO_MNEMONIC="your 25 words" \
  -e OPENAI_API_KEY="sk-proj-..." \
  -e ALGO_NETWORK="testnet" \
  -e ALGOD_URL="https://testnet-api.algonode.cloud" \
  -e NFT_IMAGE_URL="https://cdn.example.com/nft.jpg" \
  carbon-credit-api
```

### Test Endpoint
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "connected",
  "ai_services": "available",
  "algorand": "available",
  "timestamp": "2025-11-22T12:00:00"
}
```

---

## 📊 POST-DEPLOYMENT VERIFICATION

### 1. Check Health Endpoint
```bash
curl https://your-app.up.railway.app/health
```

### 2. Check API Root
```bash
curl https://your-app.up.railway.app/
```

### 3. Test Database Connection
```bash
curl https://your-app.up.railway.app/stats
```

### 4. Test Plant Catalog (no auth needed)
```bash
curl https://your-app.up.railway.app/plants/catalog
```

### 5. Check Logs
```bash
railway logs
```

---

## 🔧 CONFIGURATION TUNING

### Scale Workers (for high traffic)
Edit `railway.json`:
```json
{
  "deploy": {
    "startCommand": "gunicorn api_joyo_core:app --workers 8 ..."
  }
}
```

**Workers Formula:** `(2 × CPU cores) + 1`
- Railway Hobby: 4 workers (2 vCPU)
- Railway Pro: 8 workers (4 vCPU)

### Increase Timeout (for long AI requests)
```json
{
  "deploy": {
    "startCommand": "... --timeout 300 ..."
  }
}
```

### Database Connection Pool
In your code, increase pool size for production:
```python
# database_postgres.py
self.connection_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=20,   # Increased from 1
    maxconn=100,  # Increased from 10
    dsn=db_url
)
```

---

## 🚨 CRITICAL SECURITY FIXES

### 1. Remove Hardcoded Database URL
**File:** `database_postgres.py` line 22-25

**BEFORE:**
```python
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:eKdPRaiWEncSUuenBDgAKAVynyhJMatv@shinkansen.proxy.rlwy.net:59097/railway"
)
```

**AFTER:**
```python
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")
```

**DEPLOY THIS FIX IMMEDIATELY!**

### 2. Add Rate Limiting
Install:
```bash
pip install slowapi
```

Add to `api_joyo_core.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address, default_limits=["100/hour"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/plants/register")
@limiter.limit("10/minute")
async def register_plant(...):
    ...
```

### 3. Restrict CORS
**File:** `api_joyo_core.py` line 49-55

**BEFORE:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ❌ DANGEROUS!
    ...
)
```

**AFTER:**
```python
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://your-frontend.vercel.app")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "https://your-app.up.railway.app"],
    ...
)
```

---

## 🎯 MONITORING & MAINTENANCE

### Set up Uptime Monitoring
1. Go to Railway dashboard
2. Click your service
3. Enable "Health Checks"
4. Set path: `/health`

### View Logs
```bash
# Real-time logs
railway logs --follow

# Last 100 lines
railway logs --lines 100
```

### Restart Service
```bash
railway restart
```

### Check Resource Usage
```bash
railway status
```

---

## 📈 SCALING CHECKLIST

### For 10k users/month:
- ✅ Railway Hobby plan ($5/mo)
- ✅ 4 workers
- ✅ 20-50 DB connections

### For 100k users/month:
- ✅ Railway Pro plan ($20/mo)
- ✅ 8 workers
- ✅ 50-100 DB connections
- ✅ Redis caching (add Railway Redis)
- ✅ CDN for images (Cloudflare)

### For 200k+ users/month:
- ✅ AWS/GCP deployment
- ✅ 10-20 instances (auto-scaling)
- ✅ 100-200 DB connections
- ✅ PgBouncer connection pooler
- ✅ Redis cluster (5+ nodes)
- ✅ Load balancer

---

## 🐛 TROUBLESHOOTING

### Issue: "Cannot connect to database"
**Solution:**
```bash
# Check DATABASE_URL is set
railway variables get DATABASE_URL

# Test connection manually
railway run python3 -c "from database_postgres import db; print('Connected!')"
```

### Issue: "OpenAI API key invalid"
**Solution:**
```bash
# Verify key is set correctly (check for spaces)
railway variables get OPENAI_API_KEY

# Test API key
railway run python3 -c "import os; from openai import OpenAI; client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')); print('Valid!')"
```

### Issue: "Port already in use"
**Solution:**
Railway automatically sets PORT environment variable. Ensure your app uses it:
```python
port = int(os.getenv("PORT", 8000))
uvicorn.run(app, host="0.0.0.0", port=port)
```

### Issue: "Out of memory"
**Solution:**
Upgrade Railway plan or reduce workers:
```bash
railway up --plan pro
```

### Issue: "Health check failing"
**Solution:**
```bash
# Check if /health endpoint works locally
docker run -p 8000:8000 carbon-credit-api
curl http://localhost:8000/health

# Check Railway logs
railway logs --filter "health"
```

---

## 🔄 CONTINUOUS DEPLOYMENT

### Auto-deploy on Git Push
1. Connect GitHub repo to Railway
2. Select branch (main/production)
3. Railway auto-deploys on push

### Manual Deploy
```bash
railway up
```

### Rollback
```bash
# View deployments
railway deployments

# Rollback to specific deployment
railway rollback <deployment-id>
```

---

## ✅ DEPLOYMENT COMPLETE CHECKLIST

After deploying, verify:

- [ ] ✅ API responds at `/health`
- [ ] ✅ API root returns info at `/`
- [ ] ✅ Database connection working (`/stats`)
- [ ] ✅ Plant catalog loads (`/plants/catalog`)
- [ ] ✅ Environment variables set correctly
- [ ] ✅ Logs show no errors
- [ ] ✅ Health checks passing
- [ ] ✅ CORS configured for your frontend
- [ ] ✅ Rate limiting enabled
- [ ] ✅ Hardcoded credentials removed
- [ ] ✅ Frontend team has API URL
- [ ] ✅ Documentation updated with live URL

---

## 📞 SUPPORT

### Railway Issues:
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Status: https://status.railway.app

### Your API Issues:
- Check logs: `railway logs`
- Test locally: `docker run ...`
- Verify env vars: `railway variables`

---

## 🎉 SUCCESS!

Your API should now be live at:
**https://your-app.up.railway.app**

Share this URL with your frontend team!

---

## 🚀 NEXT STEPS

1. Deploy frontend to Vercel/Netlify
2. Update frontend API_URL to your Railway URL
3. Test end-to-end flow
4. Enable monitoring/alerts
5. Set up custom domain (optional)
6. Launch! 🎊
