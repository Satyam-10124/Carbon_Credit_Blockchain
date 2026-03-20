#!/bin/bash

# Real Coinbase x402 Protocol - Launch Script
# Starts the Carbon Credit API with official x402 payments

echo "======================================================================"
echo "🚀 REAL COINBASE x402 PROTOCOL"
echo "======================================================================"
echo ""
echo "Official Specification: https://github.com/coinbase/x402"
echo "Ecosystem: https://x402.org/ecosystem"
echo ""
echo "This uses the REAL x402 protocol by Coinbase:"
echo "  • HTTP 402 Payment Required"
echo "  • X-PAYMENT header (base64 encoded)"
echo "  • X-PAYMENT-RESPONSE header"
echo "  • Facilitator integration (/verify, /settle)"
echo "  • USDC payments on Base L2"
echo ""
echo "======================================================================"

# Check for virtual environment
if [ -d "venv" ]; then
    echo "🔧 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found!"
    echo "   Create one with: python3 -m venv venv"
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install flask flask-cors requests algosdk >/dev/null 2>&1

# Check environment variables
if [ -z "$PAYMENT_ADDRESS" ]; then
    echo ""
    echo "⚠️  Warning: PAYMENT_ADDRESS not set"
    echo "   Using default: 0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
    echo "   Set your own: export PAYMENT_ADDRESS='0xYourAddress'"
    export PAYMENT_ADDRESS="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb0"
fi

if [ -z "$X402_FACILITATOR_URL" ]; then
    echo "   Using Coinbase facilitator: https://facilitator.base.org"
    export X402_FACILITATOR_URL="https://facilitator.base.org"
fi

echo ""
echo "======================================================================"
echo "🎯 Configuration:"
echo "======================================================================"
echo "Payment Address: $PAYMENT_ADDRESS"
echo "Facilitator: $X402_FACILITATOR_URL"
echo "Network: Base L2"
echo "Currency: USDC"
echo ""
echo "======================================================================"
echo ""

# Offer demo or API
echo "What would you like to run?"
echo ""
echo "1. 📚 Demo - See how real x402 works"
echo "2. 🚀 API Server - Start the Carbon Credit API"
echo "3. 📖 View Documentation"
echo ""
read -p "Enter choice (1/2/3): " choice

case $choice in
    1)
        echo ""
        echo "======================================================================"
        echo "📚 RUNNING REAL x402 DEMO"
        echo "======================================================================"
        echo ""
        python3 demo_real_x402.py
        ;;
    2)
        echo ""
        echo "======================================================================"
        echo "🚀 STARTING API SERVER WITH REAL x402"
        echo "======================================================================"
        echo ""
        python3 api_with_real_x402.py
        ;;
    3)
        echo ""
        echo "======================================================================"
        echo "📖 DOCUMENTATION"
        echo "======================================================================"
        echo ""
        if command -v bat &> /dev/null; then
            bat REAL_X402_GUIDE.md
        elif command -v less &> /dev/null; then
            less REAL_X402_GUIDE.md
        else
            cat REAL_X402_GUIDE.md
        fi
        ;;
    *)
        echo "Invalid choice. Exiting."
        exit 1
        ;;
esac

echo ""
echo "======================================================================"
echo "✅ Session complete!"
echo "======================================================================"
