# Quick Start Script for Local Development
# Run this to set up and test the system locally

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AQI Prediction System - Quick Start" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "[1/8] Checking Python version..." -ForegroundColor Yellow
python --version

# Check if .env exists
Write-Host ""
Write-Host "[2/8] Checking environment variables..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✓ .env file found" -ForegroundColor Green
} else {
    Write-Host "✗ .env file not found. Creating template..." -ForegroundColor Red
    
    $envContent = @"
# Database Configuration
DATABASE_URL=postgresql://localhost:5432/aqi_prediction_db

# API Keys (Register at respective platforms)
OPENWEATHER_API_KEY=your_key_here
IQAIR_API_KEY=your_key_here
CPCB_API_KEY=your_key_here

# Flask Configuration
FLASK_ENV=development
SECRET_KEY=dev_secret_key_12345
"@
    
    $envContent | Out-File -FilePath ".env" -Encoding UTF8
    Write-Host "✓ Created .env template. Please add your API keys!" -ForegroundColor Yellow
}

# Install Python dependencies
Write-Host ""
Write-Host "[3/8] Installing Python dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Create models directory
Write-Host ""
Write-Host "[4/8] Creating models directory..." -ForegroundColor Yellow
if (!(Test-Path "models")) {
    New-Item -ItemType Directory -Path "models" | Out-Null
    Write-Host "✓ Created models/ directory" -ForegroundColor Green
} else {
    Write-Host "✓ models/ directory already exists" -ForegroundColor Green
}

# Check PostgreSQL
Write-Host ""
Write-Host "[5/8] Checking PostgreSQL database..." -ForegroundColor Yellow
Write-Host "Make sure PostgreSQL is running and database 'aqi_prediction_db' exists" -ForegroundColor Yellow
Write-Host ""
Write-Host "To create database, run:" -ForegroundColor Cyan
Write-Host "  createdb aqi_prediction_db" -ForegroundColor White
Write-Host "  psql -d aqi_prediction_db -f backend/database/prediction_schema.sql" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter when database is ready"

# Install frontend dependencies
Write-Host ""
Write-Host "[6/8] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green

# Test API keys
Write-Host ""
Write-Host "[7/8] Testing API configuration..." -ForegroundColor Yellow

$envVars = Get-Content .env | Where-Object { $_ -match '=' -and $_ -notmatch '^#' }
$hasOpenWeather = $envVars | Where-Object { $_ -match 'OPENWEATHER_API_KEY' -and $_ -notmatch 'your_key_here' }
$hasIQAir = $envVars | Where-Object { $_ -match 'IQAIR_API_KEY' -and $_ -notmatch 'your_key_here' }

if ($hasOpenWeather) {
    Write-Host "✓ OpenWeather API key configured" -ForegroundColor Green
} else {
    Write-Host "✗ OpenWeather API key not configured" -ForegroundColor Red
    Write-Host "  Get key at: https://openweathermap.org/api" -ForegroundColor Yellow
}

if ($hasIQAir) {
    Write-Host "✓ IQAir API key configured" -ForegroundColor Green
} else {
    Write-Host "✗ IQAir API key not configured" -ForegroundColor Red
    Write-Host "  Get key at: https://www.iqair.com/air-pollution-data-api" -ForegroundColor Yellow
}

# Show next steps
Write-Host ""
Write-Host "[8/8] Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Register for API keys (if not done):" -ForegroundColor Yellow
Write-Host "   - OpenWeather: https://openweathermap.org/api" -ForegroundColor White
Write-Host "   - IQAir: https://www.iqair.com/air-pollution-data-api" -ForegroundColor White
Write-Host ""
Write-Host "2. Update .env file with your API keys" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Start the system:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   # Terminal 1 - Start Backend API" -ForegroundColor Cyan
Write-Host "   python backend/production_api.py" -ForegroundColor White
Write-Host ""
Write-Host "   # Terminal 2 - Start Data Collector (optional)" -ForegroundColor Cyan
Write-Host "   python real_time_collector.py" -ForegroundColor White
Write-Host ""
Write-Host "   # Terminal 3 - Start Frontend" -ForegroundColor Cyan
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "4. Train ML models:" -ForegroundColor Yellow
Write-Host "   python ml_prediction_engine.py" -ForegroundColor White
Write-Host ""
Write-Host "5. Run automated scheduler:" -ForegroundColor Yellow
Write-Host "   python automated_scheduler.py" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Access Points:" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Green
Write-Host "Backend API: http://localhost:5000" -ForegroundColor Green
Write-Host "API Health: http://localhost:5000/api/health" -ForegroundColor Green
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
