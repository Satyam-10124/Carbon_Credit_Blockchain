#!/bin/bash
# Quick Deploy Script for Carbon Credit API

echo "🚀 Carbon Credit API - Quick Deploy to Railway"
echo "=============================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo "📦 Install with: npm install -g @railway/cli"
    echo "   or: brew install railway"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "🔐 Not logged in to Railway. Logging in..."
    railway login
fi

echo "✅ Logged in to Railway"
echo ""

# Check critical files
echo "📋 Checking deployment files..."
if [ ! -f "Dockerfile" ]; then
    echo "❌ Dockerfile not found!"
    exit 1
fi
echo "✅ Dockerfile found"

if [ ! -f "railway.json" ]; then
    echo "❌ railway.json not found!"
    exit 1
fi
echo "✅ railway.json found"

echo ""
echo "🔧 Pre-deployment Checklist:"
echo "=============================================="
echo ""

# Check if env vars are ready
echo "⚠️  IMPORTANT: Make sure you have these environment variables ready:"
echo ""
echo "  REQUIRED:"
echo "  - DATABASE_URL (PostgreSQL connection string)"
echo "  - ALGO_MNEMONIC (25 word Algorand wallet mnemonic)"
echo "  - OPENAI_API_KEY (OpenAI API key)"
echo "  - ALGO_NETWORK (testnet or mainnet)"
echo "  - ALGOD_URL (Algorand API URL)"
echo "  - NFT_IMAGE_URL (Default NFT image URL)"
echo ""
echo "  OPTIONAL:"
echo "  - OPENWEATHER_API_KEY"
echo "  - GOOGLE_MAPS_API_KEY"
echo "  - PAYMENT_ADDRESS (for x402)"
echo ""

read -p "Do you have all required environment variables? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Please set up environment variables first!"
    echo "   You can set them after deployment with:"
    echo "   railway variables set KEY=VALUE"
    exit 1
fi

echo ""
echo "🚀 Deploying to Railway..."
echo "=============================================="
echo ""

# Deploy
railway up

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deployment successful!"
    echo ""
    echo "📝 Next steps:"
    echo "  1. Set environment variables:"
    echo "     railway variables set DATABASE_URL='...'"
    echo "     railway variables set ALGO_MNEMONIC='...'"
    echo "     railway variables set OPENAI_API_KEY='...'"
    echo ""
    echo "  2. Get your app URL:"
    echo "     railway domain"
    echo ""
    echo "  3. Check logs:"
    echo "     railway logs"
    echo ""
    echo "  4. Test health endpoint:"
    echo "     curl https://your-app.up.railway.app/health"
    echo ""
else
    echo "❌ Deployment failed!"
    echo "   Check logs with: railway logs"
    exit 1
fi
