#!/bin/bash

# Unified Carbon Credit & Joyo System Launcher

echo "======================================================================"
echo "🌍 UNIFIED CARBON CREDIT & PLANT VERIFICATION SYSTEM"
echo "======================================================================"
echo ""
echo "This system combines:"
echo "  • Carbon Credit Blockchain (Gesture + NFT)"
echo "  • Joyo AI Services (Plant Recognition + Health + Geo)"
echo "  • Real-time sensors (GPS, Weather, Camera)"
echo "  • Algorand Blockchain (NFT minting)"
echo ""
echo "======================================================================"

# Check virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Check .env
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "   Please create .env with required API keys"
    exit 1
fi

# Run unified system
echo ""
echo "🚀 Launching unified system..."
echo "======================================================================"
echo ""

python3 unified_main.py

echo ""
echo "======================================================================"
echo "✅ Session complete!"
echo "======================================================================"
