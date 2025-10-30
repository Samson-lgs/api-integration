# Automated Setup Script for AQI Prediction System
# Simplified version that works reliably

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AQI PREDICTION SYSTEM - AUTO SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Validate API Keys
Write-Host "[1/6] Validating API Keys..." -ForegroundColor Yellow
python test_api_keys.py

Write-Host ""

# Step 2: Install Python Dependencies  
Write-Host "[2/6] Installing Python Dependencies..." -ForegroundColor Yellow
pip install -q -r requirements.txt
Write-Host "  Done!" -ForegroundColor Green

Write-Host ""

# Step 3: Create Directories
Write-Host "[3/6] Creating Directories..." -ForegroundColor Yellow
if (!(Test-Path "models")) { New-Item -ItemType Directory -Path "models" | Out-Null }
if (!(Test-Path "logs")) { New-Item -ItemType Directory -Path "logs" | Out-Null }
Write-Host "  Done!" -ForegroundColor Green

Write-Host ""

# Step 4: Collect Initial Data
Write-Host "[4/6] Collecting Data from APIs..." -ForegroundColor Yellow
Write-Host "  Fetching from OpenWeather, IQAir, and CPCB..." -ForegroundColor Cyan
python real_time_collector.py

Write-Host ""

# Step 5: Train ML Models
Write-Host "[5/6] Training ML Models..." -ForegroundColor Yellow
Write-Host "  Training XGBoost, Random Forest models..." -ForegroundColor Cyan
python ml_prediction_engine.py

Write-Host ""

# Step 6: Install Frontend
Write-Host "[6/6] Installing Frontend..." -ForegroundColor Yellow
cd frontend
npm install --silent
cd ..
Write-Host "  Done!" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host ""
Write-Host "Option 1 - Run Full Automated System:" -ForegroundColor Cyan
Write-Host "  python automated_scheduler.py" -ForegroundColor Green
Write-Host ""
Write-Host "Option 2 - Run Services Separately:" -ForegroundColor Cyan
Write-Host "  Terminal 1: python backend/production_api.py" -ForegroundColor Green
Write-Host "  Terminal 2: cd frontend && npm run dev" -ForegroundColor Green
Write-Host ""
Write-Host "Access at: http://localhost:3000" -ForegroundColor White
Write-Host ""
