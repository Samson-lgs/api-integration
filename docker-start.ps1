# Quick start script for Docker deployment (Windows PowerShell)

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Air Quality Monitoring System" -ForegroundColor Cyan
Write-Host "Docker Quick Start" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
try {
    docker --version | Out-Null
    Write-Host "✅ Docker is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not installed. Please install Docker Desktop first." -ForegroundColor Red
    exit 1
}

# Check if Docker Compose is installed
try {
    docker-compose --version | Out-Null
    Write-Host "✅ Docker Compose is installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker Compose is not installed." -ForegroundColor Red
    exit 1
}

Write-Host ""

# Check if .env file exists
if (!(Test-Path .env)) {
    Write-Host "📝 Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "⚠️  Please edit .env file with your configuration before proceeding" -ForegroundColor Yellow
    Write-Host "   Especially update:" -ForegroundColor Yellow
    Write-Host "   - POSTGRES_PASSWORD" -ForegroundColor Yellow
    Write-Host "   - SECRET_KEY" -ForegroundColor Yellow
    Write-Host "   - API keys if needed" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter after editing .env file to continue"
}

Write-Host "✅ Environment file configured" -ForegroundColor Green
Write-Host ""

# Create necessary directories
Write-Host "📁 Creating directories..." -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path logs | Out-Null
New-Item -ItemType Directory -Force -Path models | Out-Null
Write-Host "✅ Directories created" -ForegroundColor Green
Write-Host ""

# Build Docker images
Write-Host "🔨 Building Docker images..." -ForegroundColor Cyan
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to build Docker images" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker images built successfully" -ForegroundColor Green
Write-Host ""

# Start services
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to start services" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Services started successfully" -ForegroundColor Green
Write-Host ""

# Wait for services to be healthy
Write-Host "⏳ Waiting for services to be healthy..." -ForegroundColor Cyan
Start-Sleep -Seconds 10

# Check service status
Write-Host "📊 Service Status:" -ForegroundColor Cyan
docker-compose ps
Write-Host ""

# Check backend health
Write-Host "🔍 Checking backend health..." -ForegroundColor Cyan
$maxRetries = 30
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000/api/health" -TimeoutSec 2 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend is healthy" -ForegroundColor Green
            $healthy = $true
            break
        }
    } catch {
        # Continue waiting
    }
    $retryCount++
    Write-Host "Waiting for backend... ($retryCount/$maxRetries)" -ForegroundColor Yellow
    Start-Sleep -Seconds 2
}

if (!$healthy) {
    Write-Host "⚠️  Backend health check timeout. Check logs with: docker-compose logs backend" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "🎉 Deployment Complete!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application:" -ForegroundColor Cyan
Write-Host "  Frontend: http://localhost" -ForegroundColor White
Write-Host "  Backend API: http://localhost:5000" -ForegroundColor White
Write-Host "  API Health: http://localhost:5000/api/health" -ForegroundColor White
Write-Host ""
Write-Host "Useful commands:" -ForegroundColor Cyan
Write-Host "  View logs: docker-compose logs -f" -ForegroundColor White
Write-Host "  Stop services: docker-compose down" -ForegroundColor White
Write-Host "  Restart services: docker-compose restart" -ForegroundColor White
Write-Host "  View status: docker-compose ps" -ForegroundColor White
Write-Host ""
Write-Host "Documentation: See DEPLOYMENT.md for detailed instructions" -ForegroundColor Cyan
Write-Host ""
