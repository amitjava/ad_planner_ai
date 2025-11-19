#!/bin/bash
# Smart Ad Planner - Run Script

set -e

echo "🚀 Starting Smart Ad Planner..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -q -r requirements-minimal.txt

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GEMINI_API_KEY"
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check for Gemini API key
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY not set in .env file"
    exit 1
fi

# Create necessary directories
mkdir -p exports vector_store

echo "✅ Environment ready!"
echo "Starting server at http://localhost:8000"
echo ""

# Run the application
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
