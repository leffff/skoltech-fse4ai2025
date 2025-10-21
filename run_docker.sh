#!/bin/bash

echo "🚀 BLIP Image Captioning - Docker Deployment"
echo "============================================"

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker could not be found. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is available (new plugin style)
if docker compose version &> /dev/null; then
    COMPOSE_CMD="docker compose"
    echo "✅ Using Docker Compose plugin"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker-compose"
    echo "✅ Using docker-compose standalone"
else
    echo "❌ Docker Compose could not be found."
    echo "   For Docker Compose plugin, make sure you have Docker Desktop or Docker Engine v20.10+"
    echo "   Or install docker-compose standalone: https://docs.docker.com/compose/install/"
    exit 1
fi

# Build and start services
echo "Building and starting Docker containers..."
$COMPOSE_CMD up --build -d

echo ""
echo "✅ Services are starting up..."
echo "📊 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🎨 Frontend App: http://localhost:8501"
echo ""
echo "To view logs: $COMPOSE_CMD logs -f"
echo "To stop: $COMPOSE_CMD down"
echo ""

# Wait a bit and check health
echo "Waiting for services to start..."
sleep 15

echo "Checking service status..."
$COMPOSE_CMD ps

echo ""
echo "⏳ The first startup might take a few minutes to download the BLIP model..."
echo "   Check logs with: $COMPOSE_CMD logs -f backend"