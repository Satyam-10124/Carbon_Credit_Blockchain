#!/bin/bash

# Complete System Test Runner
# This script sets up and runs all system tests

echo "=================================================="
echo "🚀 Carbon Credit - Complete System Test Runner"
echo "=================================================="
echo ""

# Check if we're in the right directory
if [ ! -f "test_complete_system.py" ]; then
    echo "❌ Error: test_complete_system.py not found"
    echo "Please run this script from the Carbon_Credit_Blockchain directory"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 not found"
    echo "Please install Python 3"
    exit 1
fi

# Check/create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update required packages
echo "📦 Installing required packages..."
pip install --upgrade pip > /dev/null 2>&1
pip install -q psycopg2-binary requests openai python-dotenv algosdk opencv-python mediapipe

echo "✅ Environment ready"
echo ""

# Run the test
echo "🧪 Running complete system test..."
echo ""
python3 test_complete_system.py

# Capture exit code
TEST_EXIT_CODE=$?

echo ""
echo "=================================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo "✅ All tests completed successfully!"
else
    echo "⚠️  Some tests failed (exit code: $TEST_EXIT_CODE)"
fi
echo "=================================================="

exit $TEST_EXIT_CODE
