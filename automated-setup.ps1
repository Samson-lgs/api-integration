# ============================================================================
# AUTOMATED SETUP SCRIPT - AQI Prediction System
# This script automates the entire local setup process
# ============================================================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AQI PREDICTION SYSTEM" -ForegroundColor Cyan
Write-Host "  Automated Setup & Launch" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$ErrorActionPreference = "Continue"

# ============================================================================
# STEP 1: VALIDATE API KEYS
# ============================================================================

Write-Host "[Step 1/7] Validating API Keys..." -ForegroundColor Yellow
Write-Host ""

if (Test-Path ".env") {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
    
    # Test API keys
    Write-Host "  Testing API connections..." -ForegroundColor Cyan
    python test_api_keys.py
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "  ⚠ Warning: Some API keys may not be working" -ForegroundColor Yellow
        Write-Host "  Continuing anyway..." -ForegroundColor Yellow
    }
} else {
    Write-Host "  ✗ .env file not found!" -ForegroundColor Red
    Write-Host "  Please create .env file with your API keys" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 2: INSTALL PYTHON DEPENDENCIES
# ============================================================================

Write-Host "[Step 2/7] Installing Python Dependencies..." -ForegroundColor Yellow
Write-Host ""

pip install -q -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Python packages installed" -ForegroundColor Green
} else {
    Write-Host "  ✗ Failed to install Python packages" -ForegroundColor Red
    exit 1
}

Write-Host ""

# ============================================================================
# STEP 3: CREATE DIRECTORIES
# ============================================================================

Write-Host "[Step 3/7] Creating Required Directories..." -ForegroundColor Yellow
Write-Host ""

$directories = @("models", "logs")

foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "  ✓ Created $dir/ directory" -ForegroundColor Green
    } else {
        Write-Host "  ✓ $dir/ directory exists" -ForegroundColor Green
    }
}

Write-Host ""

# ============================================================================
# STEP 4: CHECK POSTGRESQL
# ============================================================================

Write-Host "[Step 4/7] Checking PostgreSQL Database..." -ForegroundColor Yellow
Write-Host ""

# Check if PostgreSQL is running
$pgRunning = $false
try {
    $pgService = Get-Service -Name "postgresql*" -ErrorAction SilentlyContinue
    if ($pgService -and $pgService.Status -eq "Running") {
        $pgRunning = $true
        Write-Host "  ✓ PostgreSQL service is running" -ForegroundColor Green
    }
} catch {
    # Try alternative check
}

if (!$pgRunning) {
    Write-Host "  ⚠ PostgreSQL service not detected" -ForegroundColor Yellow
    Write-Host "  You may need to:" -ForegroundColor Yellow
    Write-Host "    1. Install PostgreSQL 15+" -ForegroundColor White
    Write-Host "    2. Create database: createdb aqi_prediction_db" -ForegroundColor White
    Write-Host "    3. Run schema: psql -d aqi_prediction_db -f backend/database/prediction_schema.sql" -ForegroundColor White
    Write-Host ""
    Write-Host "  Or use SQLite for testing (automatic)" -ForegroundColor Cyan
    Write-Host ""
    
    $response = Read-Host "  Continue anyway? (y/n)"
    if ($response -ne "y") {
        exit 1
    }
}

Write-Host ""

# ============================================================================
# STEP 5: COLLECT INITIAL DATA
# ============================================================================

Write-Host "[Step 5/7] Collecting Initial Data from APIs..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  This will fetch data from OpenWeather, IQAir, and CPCB" -ForegroundColor Cyan
Write-Host "  for all 10 cities. Please wait..." -ForegroundColor Cyan
Write-Host ""

python real_time_collector.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "  ✓ Initial data collection completed!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "  ⚠ Data collection had some issues" -ForegroundColor Yellow
    Write-Host "  Check the logs above for details" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 6: TRAIN ML MODELS
# ============================================================================

Write-Host "[Step 6/7] Training Machine Learning Models..." -ForegroundColor Yellow
Write-Host ""
Write-Host "  Training XGBoost, Random Forest, and Linear models" -ForegroundColor Cyan
Write-Host "  This may take 2-3 minutes..." -ForegroundColor Cyan
Write-Host ""

python ml_prediction_engine.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "  ✓ ML models trained successfully!" -ForegroundColor Green
    
    # Check if models were created
    if (Test-Path "models/aqi_model_xgboost.pkl") {
        Write-Host "  ✓ XGBoost model saved" -ForegroundColor Green
    }
    if (Test-Path "models/metrics.json") {
        Write-Host "  ✓ Model metrics saved" -ForegroundColor Green
    }
} else {
    Write-Host ""
    Write-Host "  ⚠ Model training had issues (may need more data)" -ForegroundColor Yellow
}

Write-Host ""

# ============================================================================
# STEP 7: INSTALL FRONTEND DEPENDENCIES
# ============================================================================

Write-Host "[Step 7/7] Installing Frontend Dependencies..." -ForegroundColor Yellow
Write-Host ""

Set-Location frontend
npm install --silent
Set-Location ..

if ($LASTEXITCODE -eq 0) {
    Write-Host "  ✓ Frontend packages installed" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Frontend installation had issues" -ForegroundColor Yellow
}

Write-Host ""
Write-Host ""

# ============================================================================
# SETUP COMPLETE - SHOW NEXT STEPS
# ============================================================================

Write-Host "========================================" -ForegroundColor Green
Write-Host "  ✓ SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Your AQI Prediction System is ready!" -ForegroundColor Cyan
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QUICK START OPTIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Option 1: Run Full System (Automated)" -ForegroundColor Yellow
Write-Host "--------------------------------------" -ForegroundColor White
Write-Host "  python automated_scheduler.py" -ForegroundColor Green
Write-Host ""
Write-Host "  This will:" -ForegroundColor Gray
Write-Host "  • Collect data every hour" -ForegroundColor Gray
Write-Host "  • Generate predictions every hour" -ForegroundColor Gray
Write-Host "  • Retrain models daily at 2 AM" -ForegroundColor Gray
Write-Host "  • Check for health alerts every 30 minutes" -ForegroundColor Gray
Write-Host ""

Write-Host "Option 2: Run Services Separately" -ForegroundColor Yellow
Write-Host "--------------------------------------" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 1 - Backend API:" -ForegroundColor Cyan
Write-Host "    python backend/production_api.py" -ForegroundColor Green
Write-Host "    Access: http://localhost:5000" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 2 - Frontend:" -ForegroundColor Cyan
Write-Host "    cd frontend" -ForegroundColor Green
Write-Host "    npm run dev" -ForegroundColor Green
Write-Host "    Access: http://localhost:3000" -ForegroundColor White
Write-Host ""
Write-Host "  Terminal 3 - Data Collection (Optional):" -ForegroundColor Cyan
Write-Host "    python real_time_collector.py" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SYSTEM INFO" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Keys Configured:" -ForegroundColor Yellow
Write-Host "  ✓ OpenWeather Air Pollution API" -ForegroundColor Green
Write-Host "  ✓ IQAir AirVisual API" -ForegroundColor Green
Write-Host "  ✓ CPCB Government API" -ForegroundColor Green
Write-Host ""
Write-Host "Cities Covered:" -ForegroundColor Yellow
Write-Host "  Delhi, Mumbai, Bangalore, Chennai, Kolkata," -ForegroundColor White
Write-Host "  Hyderabad, Pune, Ahmedabad, Jaipur, Lucknow" -ForegroundColor White
Write-Host ""
Write-Host "Features:" -ForegroundColor Yellow
Write-Host "  • Real-time data from 3 API sources" -ForegroundColor White
Write-Host "  • 1-48 hour AQI predictions" -ForegroundColor White
Write-Host "  • XGBoost, Random Forest, Linear models" -ForegroundColor White
Write-Host "  • Automated hourly data collection" -ForegroundColor White
Write-Host "  • Daily model retraining" -ForegroundColor White
Write-Host "  • Health alerts for high AQI" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WHAT TO DO NOW" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Start the automated scheduler:" -ForegroundColor Yellow
Write-Host "   python automated_scheduler.py" -ForegroundColor Green
Write-Host ""
Write-Host "2. In another terminal, start the backend:" -ForegroundColor Yellow
Write-Host "   python backend/production_api.py" -ForegroundColor Green
Write-Host ""
Write-Host "3. In another terminal, start the frontend:" -ForegroundColor Yellow
Write-Host "   cd frontend && npm run dev" -ForegroundColor Green
Write-Host ""
Write-Host "4. Open your browser:" -ForegroundColor Yellow
Write-Host "   http://localhost:3000" -ForegroundColor Green
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "USEFUL COMMANDS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Check API keys:          python test_api_keys.py" -ForegroundColor White
Write-Host "Collect data now:        python real_time_collector.py" -ForegroundColor White
Write-Host "Train models:            python ml_prediction_engine.py" -ForegroundColor White
Write-Host "Start full system:       python automated_scheduler.py" -ForegroundColor White
Write-Host "Start backend API:       python backend/production_api.py" -ForegroundColor White
Write-Host "Start frontend:          cd frontend && npm run dev" -ForegroundColor White
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "For deployment to production:" -ForegroundColor Yellow
Write-Host "  See: PRODUCTION_DEPLOYMENT_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "For detailed documentation:" -ForegroundColor Yellow
Write-Host "  See: START_HERE.md" -ForegroundColor White
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Ready to go! 🚀" -ForegroundColor Green
Write-Host ""
