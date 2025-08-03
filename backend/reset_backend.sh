#!/bin/bash

# Webhound Backend Reset Script
# This script completely resets the backend environment and starts fresh

set -e  # Exit on any error

echo "🔄 Webhound Backend Reset Script"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to kill processes by name
kill_processes() {
    local process_name=$1
    local pids=$(pgrep -f "$process_name" 2>/dev/null || true)
    
    if [ -n "$pids" ]; then
        print_status "Killing $process_name processes: $pids"
        echo "$pids" | xargs kill -9 2>/dev/null || true
        sleep 1
    else
        print_status "No $process_name processes found"
    fi
}

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0  # Port is in use
    else
        return 1  # Port is free
    fi
}

# Function to wait for port to be free
wait_for_port() {
    local port=$1
    local max_wait=10
    local count=0
    
    while check_port $port && [ $count -lt $max_wait ]; do
        print_status "Waiting for port $port to be free... ($((count + 1))/$max_wait)"
        sleep 1
        count=$((count + 1))
    done
    
    if check_port $port; then
        print_error "Port $port is still in use after $max_wait seconds"
        return 1
    else
        print_success "Port $port is now free"
    fi
}

# Step 1: Kill all related processes
print_status "Step 1: Killing existing processes..."
kill_processes "uvicorn"
kill_processes "python.*main"
kill_processes "python.*webhound"

# Step 2: Wait for ports to be free
print_status "Step 2: Waiting for ports to be free..."
wait_for_port 8000
wait_for_port 8001
wait_for_port 8002

# Step 3: Clean up Python cache
print_status "Step 3: Cleaning Python cache..."
if [ -d "__pycache__" ]; then
    rm -rf __pycache__
    print_success "Removed __pycache__ directory"
else
    print_status "No __pycache__ directory found"
fi

# Step 4: Clean up database files (optional)
print_status "Step 4: Cleaning database files..."
if [ -f "webhound.db" ]; then
    print_warning "Found existing database: webhound.db"
    read -p "Do you want to delete the database? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f webhound.db
        print_success "Deleted webhound.db"
    else
        print_status "Keeping existing database"
    fi
else
    print_status "No existing database found"
fi

# Step 5: Clean up temporary files
print_status "Step 5: Cleaning temporary files..."
rm -f test_*.db 2>/dev/null || true
rm -f temp_*.db 2>/dev/null || true
rm -f /tmp/webhound_dataset_*.csv 2>/dev/null || true

# Step 6: Check Python environment
print_status "Step 6: Checking Python environment..."
if ! command_exists python; then
    print_error "Python is not installed or not in PATH"
    exit 1
fi

python_version=$(python --version 2>&1)
print_success "Using $python_version"

# Step 7: Check if virtual environment is activated
print_status "Step 7: Checking virtual environment..."
if [[ "$VIRTUAL_ENV" == "" ]]; then
    print_warning "Virtual environment not detected"
    if [ -d "venv" ]; then
        print_status "Found venv directory, activating..."
        source venv/bin/activate
        print_success "Virtual environment activated"
    else
        print_error "No virtual environment found. Please create one first:"
        echo "  python -m venv venv"
        echo "  source venv/bin/activate"
        echo "  pip install -r requirements.txt"
        exit 1
    fi
else
    print_success "Virtual environment is active: $VIRTUAL_ENV"
fi

# Step 8: Check dependencies
print_status "Step 8: Checking dependencies..."
if [ -f "requirements.txt" ]; then
    print_status "Checking if all requirements are installed..."
    missing_deps=$(pip check 2>&1 || true)
    if [ -n "$missing_deps" ]; then
        print_warning "Some dependencies may be missing or have conflicts"
        echo "$missing_deps"
        read -p "Do you want to reinstall requirements? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            pip install -r requirements.txt
            print_success "Requirements reinstalled"
        fi
    else
        print_success "All dependencies are properly installed"
    fi
else
    print_warning "No requirements.txt found"
fi

# Step 9: Test database functionality
print_status "Step 9: Testing database functionality..."
python -c "
from database import JobDatabase
import tempfile
import os

# Test with temporary database
test_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
test_db.close()

try:
    db = JobDatabase(test_db.name)
    db.create_job('test-123', 'test query')
    job = db.get_job('test-123')
    if job and job['query'] == 'test query':
        print('✅ Database test passed')
    else:
        print('❌ Database test failed')
        exit(1)
finally:
    os.unlink(test_db.name)
" 2>/dev/null

if [ $? -eq 0 ]; then
    print_success "Database functionality verified"
else
    print_error "Database test failed"
    exit 1
fi

# Step 10: Start the server
print_status "Step 10: Starting the server..."
print_status "Starting uvicorn server on http://localhost:8000"
print_status "Press Ctrl+C to stop the server"

# Start the server in the background and capture its PID
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait a moment for the server to start
sleep 3

# Check if server started successfully
if kill -0 $SERVER_PID 2>/dev/null; then
    print_success "Server started successfully (PID: $SERVER_PID)"
    
    # Test the health endpoint
    print_status "Testing server health..."
    if curl -s http://localhost:8000/api/health >/dev/null 2>&1; then
        print_success "Server is responding to health checks"
    else
        print_warning "Server may not be fully ready yet"
    fi
    
    echo ""
    echo "🎉 Backend reset complete!"
    echo "=========================="
    echo "Server is running on: http://localhost:8000"
    echo "Health check: http://localhost:8000/api/health"
    echo "API docs: http://localhost:8000/docs"
    echo ""
    echo "To stop the server, run: kill $SERVER_PID"
    echo "Or press Ctrl+C in this terminal"
    
    # Wait for the server process
    wait $SERVER_PID
else
    print_error "Failed to start server"
    exit 1
fi 