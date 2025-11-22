#!/bin/bash

# Official Coinbase x402 Integration - Launch Script

echo "======================================================================"
echo "🎯 OFFICIAL COINBASE x402 INTEGRATION"
echo "======================================================================"
echo ""
echo "Using the REAL Coinbase x402 Python package"
echo "GitHub: https://github.com/coinbase/x402"
echo "Examples: https://github.com/coinbase/x402/tree/main/examples/python"
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

# Check if x402 is installed
echo "📦 Checking for official x402 package..."
if python -c "import x402" 2>/dev/null; then
    echo "✅ x402 package installed!"
else
    echo "⚠️  x402 package not installed!"
    echo "   Installing now..."
    pip install x402 eth-account web3
fi

# Check environment variables
if [ -f ".env" ]; then
    source .env
    if [ -z "$PRIVATE_KEY" ] || [ -z "$ADDRESS" ]; then
        echo ""
        echo "⚠️  Missing environment variables in .env"
        echo "   Required: PRIVATE_KEY and ADDRESS"
        echo "   See OFFICIAL_X402_GUIDE.md for setup"
        echo ""
    else
        echo "✅ Environment variables loaded"
    fi
else
    echo "⚠️  No .env file found"
    echo "   Copy .env.example to .env and add your keys"
fi

echo ""
echo "======================================================================"
echo "What would you like to run?"
echo "======================================================================"
echo ""
echo "1. 🚀 Flask API Server (Official x402)"
echo "2. ⚡ FastAPI Server (Official x402)"
echo "3. 🤖 Client Demo (Make paid requests)"
echo "4. 📖 View Documentation"
echo "5. 🧪 Test Installation"
echo ""
read -p "Enter choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "======================================================================"
        echo "🚀 STARTING FLASK API WITH OFFICIAL x402"
        echo "======================================================================"
        echo ""
        python api_official_x402.py
        ;;
    2)
        echo ""
        echo "======================================================================"
        echo "⚡ STARTING FASTAPI WITH OFFICIAL x402"
        echo "======================================================================"
        echo ""
        python api_fastapi_official_x402.py
        ;;
    3)
        echo ""
        echo "======================================================================"
        echo "🤖 RUNNING CLIENT DEMO"
        echo "======================================================================"
        echo ""
        python client_official_x402.py
        ;;
    4)
        echo ""
        echo "======================================================================"
        echo "📖 OFFICIAL x402 DOCUMENTATION"
        echo "======================================================================"
        echo ""
        if command -v bat &> /dev/null; then
            bat OFFICIAL_X402_GUIDE.md
        elif command -v less &> /dev/null; then
            less OFFICIAL_X402_GUIDE.md
        else
            cat OFFICIAL_X402_GUIDE.md
        fi
        ;;
    5)
        echo ""
        echo "======================================================================"
        echo "🧪 TESTING INSTALLATION"
        echo "======================================================================"
        echo ""
        python -c "
import sys
try:
    import x402
    print('✅ x402 package:', x402.__version__ if hasattr(x402, '__version__') else 'installed')
except ImportError:
    print('❌ x402 package not installed')
    sys.exit(1)

try:
    from x402.flask.middleware import PaymentMiddleware
    print('✅ Flask middleware: available')
except ImportError:
    print('⚠️  Flask middleware not available')

try:
    from x402.fastapi.middleware import require_payment
    print('✅ FastAPI middleware: available')
except ImportError:
    print('⚠️  FastAPI middleware not available')

try:
    from x402.clients.requests import x402_requests
    print('✅ Requests client: available')
except ImportError:
    print('⚠️  Requests client not available')

try:
    from eth_account import Account
    print('✅ eth_account: available')
except ImportError:
    print('❌ eth_account not installed')
    sys.exit(1)

print('')
print('✅ Official x402 package is properly installed!')
"
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
