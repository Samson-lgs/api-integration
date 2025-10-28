#!/bin/bash
# Quick start script for Docker deployment

echo "======================================"
echo "Air Quality Monitoring System"
echo "Docker Quick Start"
echo "======================================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before proceeding"
    echo "   Especially update:"
    echo "   - POSTGRES_PASSWORD"
    echo "   - SECRET_KEY"
    echo "   - API keys if needed"
    echo ""
    read -p "Press Enter after editing .env file to continue..."
fi

echo "✅ Environment file configured"
echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p models
echo "✅ Directories created"
echo ""

# Build Docker images
echo "🔨 Building Docker images..."
docker-compose build
if [ $? -ne 0 ]; then
    echo "❌ Failed to build Docker images"
    exit 1
fi
echo "✅ Docker images built successfully"
echo ""

# Start services
echo "🚀 Starting services..."
docker-compose up -d
if [ $? -ne 0 ]; then
    echo "❌ Failed to start services"
    exit 1
fi
echo "✅ Services started successfully"
echo ""

# Wait for services to be healthy
echo "⏳ Waiting for services to be healthy..."
sleep 10

# Check service status
echo "📊 Service Status:"
docker-compose ps
echo ""

# Check backend health
echo "🔍 Checking backend health..."
MAX_RETRIES=30
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -s http://localhost:5000/api/health > /dev/null 2>&1; then
        echo "✅ Backend is healthy"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for backend... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    echo "⚠️  Backend health check timeout. Check logs with: docker-compose logs backend"
fi

echo ""
echo "======================================"
echo "🎉 Deployment Complete!"
echo "======================================"
echo ""
echo "Access the application:"
echo "  Frontend: http://localhost"
echo "  Backend API: http://localhost:5000"
echo "  API Health: http://localhost:5000/api/health"
echo ""
echo "Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart services: docker-compose restart"
echo "  View status: docker-compose ps"
echo ""
echo "Documentation: See DEPLOYMENT.md for detailed instructions"
echo ""
