#!/bin/bash

# Simple Server Start Script
# This script starts the server with explicit virtual environment

echo "🚀 Starting Webhound Backend Server"
echo "==================================="

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Kill any existing processes
echo "Cleaning up existing processes..."
pkill -f uvicorn 2>/dev/null || true
sleep 2

# Activate virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated: $VIRTUAL_ENV"
else
    echo "❌ Virtual environment not found"
    exit 1
fi

# Test imports
echo "Testing imports..."
python -c "import pandas as pd; import fastapi; print('✅ All imports successful')" || {
    echo "❌ Import test failed"
    exit 1
}

# Start server
echo "Starting server on http://localhost:8000"
echo "Press Ctrl+C to stop"
echo ""

# Use the virtual environment's python directly
"$VIRTUAL_ENV/bin/python" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 