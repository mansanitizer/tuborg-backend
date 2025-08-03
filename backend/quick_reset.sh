#!/bin/bash

# Quick Backend Reset Script
# Fast reset without prompts for development

echo "⚡ Quick Backend Reset"
echo "======================"

# Ensure we're in the right directory
cd "$(dirname "$0")"

# Activate virtual environment if not already active
if [[ "$VIRTUAL_ENV" == "" ]]; then
    if [ -d "venv" ]; then
        echo "Activating virtual environment..."
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found"
        exit 1
    fi
fi

# Kill existing processes
echo "Killing existing processes..."
pkill -f "uvicorn" 2>/dev/null || true
pkill -f "python.*main" 2>/dev/null || true

# Clean cache
echo "Cleaning cache..."
rm -rf __pycache__ 2>/dev/null || true

# Wait for port to be free
echo "Waiting for port 8000..."
sleep 2

# Test imports before starting
echo "Testing imports..."
python -c "import pandas as pd; import fastapi; print('✅ All imports successful')" || {
    echo "❌ Import test failed"
    exit 1
}

# Start server with explicit virtual environment
echo "Starting server..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Using virtual environment: $VIRTUAL_ENV"
    exec "$VIRTUAL_ENV/bin/python" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    echo "No virtual environment detected, using system python"
    exec python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
fi 