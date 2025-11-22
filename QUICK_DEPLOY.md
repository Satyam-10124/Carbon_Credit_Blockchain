# ⚡ QUICK DEPLOY GUIDE - 5 Minutes to Production

Get your API live on Railway in 5 minutes!

---

## 🚀 STEP 1: Install Railway CLI (1 minute)

```bash
npm install -g @railway/cli
# or
brew install railway
```

---

## 🔐 STEP 2: Login to Railway (30 seconds)

```bash
railway login
```

This opens browser for authentication.

---

## 📦 STEP 3: Deploy Your API (1 minute)

```bash
cd /Users/satyamsinghal/Desktop/Face_Cascade/Carbon_Credit_Blockchain

# Quick deploy script
./deploy.sh

# Or manual
railway init
railway up
```

---

## ⚙️ STEP 4: Set Environment Variables (2 minutes)

### Required Variables:

```bash
# Database (get from Railway PostgreSQL service)
railway variables set DATABASE_URL="postgresql://user:pass@host:port/db"

# Algorand Blockchain
railway variables set ALGO_MNEMONIC="your 25 word mnemonic here"
railway variables set ALGO_NETWORK="testnet"
railway variables set ALGOD_URL="https://testnet-api.algonode.cloud"
railway variables set NFT_IMAGE_URL="https://your-cdn.com/nft.jpg"

# OpenAI (get from https://platform.openai.com/api-keys)
railway variables set OPENAI_API_KEY="sk-proj-..."
```

### Optional Variables:

```bash
railway variables set OPENWEATHER_API_KEY="your_key"
railway variables set GOOGLE_MAPS_API_KEY="your_key"
railway variables set PAYMENT_ADDRESS="0x742d35..."
```

---

## ✅ STEP 5: Get Your API URL (30 seconds)

```bash
railway domain
```

**Output:** `https://your-app.up.railway.app`

---

## 🧪 STEP 6: Test Your API (1 minute)

```bash
# Health check
curl https://your-app.up.railway.app/health

# Expected response:
# {
#   "status": "healthy",
#   "database": "connected",
#   "ai_services": "available"
# }

# Get plant catalog
curl https://your-app.up.railway.app/plants/catalog
```

---

## ✅ SUCCESS!

Your API is live! Share this URL with your frontend team:

**`https://your-app.up.railway.app`**

---

## 📱 NEXT: Deploy Frontend

### Update Frontend Environment Variable

**File:** `frontend/.env.local`

```bash
NEXT_PUBLIC_API_URL=https://your-app.up.railway.app
```

### Deploy Frontend to Vercel

```bash
cd frontend
npm install
vercel
```

---

## 🐛 TROUBLESHOOTING

### Issue: "Cannot connect to database"
```bash
# Check DATABASE_URL is set
railway variables get DATABASE_URL

# Should start with: postgresql://
```

### Issue: "OpenAI API key invalid"
```bash
# Check for extra spaces
railway variables get OPENAI_API_KEY

# Should start with: sk-proj-
```

### Issue: "Health check failing"
```bash
# View logs
railway logs

# Restart service
railway restart
```

---

## 📊 MONITORING

### View Logs
```bash
railway logs --follow
```

### Check Status
```bash
railway status
```

### Restart Service
```bash
railway restart
```

---

## 🎯 PRODUCTION CHECKLIST

After deployment, verify:

- [ ] ✅ `/health` returns status: "healthy"
- [ ] ✅ `/plants/catalog` returns 8 plants
- [ ] ✅ No errors in logs (`railway logs`)
- [ ] ✅ Database connected
- [ ] ✅ All environment variables set
- [ ] ✅ Frontend can reach API
- [ ] ✅ CORS configured for your frontend

---

## 💰 COSTS

**Railway Hobby Plan:** $5/month
- 500 hours/month execution time
- 8GB RAM
- 100GB egress

**For 10k users/month:** Hobby plan sufficient  
**For 100k+ users:** Upgrade to Pro ($20/month)

---

## 🆘 NEED HELP?

- **Railway Docs:** https://docs.railway.app
- **Railway Discord:** https://discord.gg/railway
- **API Issues:** Check `railway logs`

---

## 🎉 YOU'RE LIVE!

Your Carbon Credit API is now production-ready and serving traffic!

**API URL:** `https://your-app.up.railway.app`

Share this with your frontend team and start building! 🚀
