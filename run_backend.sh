#!/bin/bash

# BLIP Image Captioning Backend Runner
# Description: Starts the FastAPI backend server

set -e  # Exit on any error

echo "========================================"
echo "   BLIP Backend Server Starter"
echo "========================================"

# Change to backend directory
cd "$(dirname "$0")/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install requirements if needed
echo "Checking dependencies..."
if [ ! -f ".dependencies_installed" ] || [ requirements.txt -nt .dependencies_installed ]; then
    echo "Installing/updating dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .dependencies_installed
    echo "Dependencies installed successfully!"
fi

# Check if BLIP model is available
echo "Checking BLIP model..."
python3 -c "
from transformers import BlipProcessor, BlipForConditionalGeneration
import torch
try:
    processor = BlipProcessor.from_pretrained('Salesforce/blip-image-captioning-base')
    model = BlipForConditionalGeneration.from_pretrained('Salesforce/blip-image-captioning-base')
    print('✅ BLIP model is available')
except Exception as e:
    print('❌ BLIP model loading failed:', str(e))
    exit(1)
"

# Create uploads directory if it doesn't exist
mkdir -p uploads
echo "✅ Uploads directory ready"

# Display server information
echo ""
echo "🚀 Starting FastAPI server..."
echo "📍 Local URL: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "❤️  Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo "========================================"

# Start the FastAPI server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload