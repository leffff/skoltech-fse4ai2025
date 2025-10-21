#!/bin/bash

# BLIP Image Captioning Frontend Runner
# Description: Starts the Streamlit frontend application

set -e  # Exit on any error

echo "========================================"
echo "   BLIP Frontend Application Starter"
echo "========================================"

# Change to frontend directory
cd "$(dirname "$0")/frontend"

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

# Check if backend is running
echo "Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running and healthy"
else
    echo "⚠️  Backend is not running on localhost:8000"
    echo "   Make sure to start the backend first with: ./run_backend.sh"
    echo "   Or update the backend URL in the frontend app"
fi

# Display application information
echo ""
echo "🚀 Starting Streamlit frontend..."
echo "📍 Local URL: http://localhost:8501"
echo "📝 Application: BLIP Image Captioning"
echo ""
echo "Press Ctrl+C to stop the application"
echo "========================================"

# Start the Streamlit application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0