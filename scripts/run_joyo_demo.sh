#!/bin/bash

# Joyo AI Services - Quick Demo Launcher

echo "======================================================================"
echo "🌱 JOYO AI SERVICES - PHASE 1 DEMO"
echo "======================================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Please create .env with your API keys"
    exit 1
fi

# Install/update requirements
echo "📦 Installing Joyo AI requirements..."
pip install -q -r joyo_ai_services/requirements.txt

# Run demo
echo ""
echo "🚀 Launching Joyo AI Demo..."
echo "======================================================================"
echo ""

python3 joyo_ai_services/demo_complete_system.py

echo ""
echo "======================================================================"
echo "✅ Demo complete!"
echo "======================================================================"
