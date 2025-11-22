#!/bin/bash
# Setup script for Carbon Credit Blockchain System

echo "=========================================="
echo "🌍 Carbon Credit Blockchain Setup"
echo "=========================================="
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION detected"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Copy .env.example to .env"
echo "   cp .env.example .env"
echo ""
echo "2. Edit .env with your credentials:"
echo "   - ALGOD_URL (TestNet: https://testnet-api.algonode.cloud)"
echo "   - ALGO_MNEMONIC (25-word mnemonic from funded TestNet account)"
echo "   - OPENAI_API_KEY (optional, from platform.openai.com)"
echo ""
echo "3. Get TestNet ALGO:"
echo "   https://testnet.algoexplorer.io/dispenser"
echo ""
echo "4. Run the system:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "=========================================="
