# ============================================================================
# AIR QUALITY MONITORING SYSTEM - QUICK START SCRIPT
# Run this script to verify your setup
# ============================================================================

Write-Output ""
Write-Output "="*80
Write-Output " AIR QUALITY MONITORING SYSTEM - SETUP VERIFICATION"
Write-Output "="*80
Write-Output ""

# Check Python
Write-Output "1️⃣ Checking Python..."
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Output "   ✅ $pythonVersion"
} else {
    Write-Output "   ❌ Python not found! Please install Python 3.14+"
    exit 1
}

# Check Node.js
Write-Output ""
Write-Output "2️⃣ Checking Node.js..."
$nodeVersion = node --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Output "   ✅ Node.js $nodeVersion"
} else {
    Write-Output "   ❌ Node.js not found! Please install Node.js 18+"
    exit 1
}

# Check PostgreSQL
Write-Output ""
Write-Output "3️⃣ Checking PostgreSQL..."
$pgResult = psql --version 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Output "   ✅ $pgResult"
} else {
    Write-Output "   ⚠️  PostgreSQL command not found (may still be installed)"
}

# Check Virtual Environment
Write-Output ""
Write-Output "4️⃣ Checking Python Virtual Environment..."
if (Test-Path ".venv") {
    Write-Output "   ✅ Virtual environment exists at .venv"
} else {
    Write-Output "   ⚠️  Virtual environment not found"
    Write-Output "   Creating virtual environment..."
    python -m venv .venv
    if ($LASTEXITCODE -eq 0) {
        Write-Output "   ✅ Virtual environment created"
    } else {
        Write-Output "   ❌ Failed to create virtual environment"
        exit 1
    }
}

# Check .env file
Write-Output ""
Write-Output "5️⃣ Checking Environment Configuration..."
if (Test-Path ".env") {
    Write-Output "   ✅ .env file exists"
} else {
    Write-Output "   ⚠️  .env file not found"
    Write-Output "   Copying .env.example to .env..."
    Copy-Item .env.example .env
    Write-Output "   ✅ Created .env file"
    Write-Output "   ⚠️  IMPORTANT: Edit .env and add your DATABASE_URL"
}

# Check Backend Dependencies
Write-Output ""
Write-Output "6️⃣ Checking Backend Dependencies..."
if (Test-Path ".venv\Scripts\python.exe") {
    $flaskInstalled = & .venv\Scripts\python.exe -c "import flask" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Output "   ✅ Backend dependencies installed"
    } else {
        Write-Output "   ⚠️  Backend dependencies not installed"
        Write-Output "   Run: .venv\Scripts\Activate.ps1"
        Write-Output "   Then: pip install -r requirements.txt"
    }
} else {
    Write-Output "   ⚠️  Virtual environment Python not found"
}

# Check Frontend Dependencies
Write-Output ""
Write-Output "7️⃣ Checking Frontend Dependencies..."
if (Test-Path "frontend\node_modules") {
    Write-Output "   ✅ Frontend dependencies installed"
} else {
    Write-Output "   ⚠️  Frontend dependencies not installed"
    Write-Output "   Run: cd frontend && npm install"
}

# Check ML Models
Write-Output ""
Write-Output "8️⃣ Checking ML Models..."
$modelCount = 0
if (Test-Path "models\linear_regression_model.pkl") { $modelCount++ }
if (Test-Path "models\random_forest_model.pkl") { $modelCount++ }
if (Test-Path "models\xgboost_model.pkl") { $modelCount++ }
if (Test-Path "models\ensemble_model.pkl") { $modelCount++ }
if (Test-Path "models\scaler.pkl") { $modelCount++ }

if ($modelCount -ge 5) {
    Write-Output "   ✅ All ML models found ($modelCount/5)"
} else {
    Write-Output "   ⚠️  Some ML models missing ($modelCount/5)"
    Write-Output "   Models will be loaded when available"
}

# Summary
Write-Output ""
Write-Output "="*80
Write-Output " SETUP SUMMARY"
Write-Output "="*80
Write-Output ""

Write-Output "📋 Next Steps:"
Write-Output ""
Write-Output "1. Install Backend Dependencies (if not done):"
Write-Output "   .venv\Scripts\Activate.ps1"
Write-Output "   pip install -r requirements.txt"
Write-Output ""
Write-Output "2. Install Frontend Dependencies (if not done):"
Write-Output "   cd frontend"
Write-Output "   npm install"
Write-Output ""
Write-Output "3. Configure Database:"
Write-Output "   Edit .env and set DATABASE_URL"
Write-Output "   Example: DATABASE_URL=postgresql://postgres:password@localhost:5432/air_quality_db"
Write-Output ""
Write-Output "4. Initialize Database with Sample Data:"
Write-Output "   cd backend"
Write-Output "   python init_db.py"
Write-Output ""
Write-Output "5. Start Backend API (Terminal 1):"
Write-Output "   cd backend"
Write-Output "   python api.py"
Write-Output ""
Write-Output "6. Start Frontend (Terminal 2):"
Write-Output "   cd frontend"
Write-Output "   npm run dev"
Write-Output ""
Write-Output "7. Access Application:"
Write-Output "   Dashboard: http://localhost:3000"
Write-Output "   API: http://localhost:5000/api"
Write-Output "   Health: http://localhost:5000/api/health"
Write-Output ""
Write-Output "="*80
Write-Output " 📚 DOCUMENTATION"
Write-Output "="*80
Write-Output ""
Write-Output "- ARCHITECTURE.md - Complete deployment guide"
Write-Output "- README_FULLSTACK.md - Full-stack README"
Write-Output "- FULLSTACK_COMPLETE.md - Implementation summary"
Write-Output "- ML_PIPELINE_COMPLETE.md - ML documentation"
Write-Output ""
Write-Output "="*80
Write-Output " ✅ SETUP VERIFICATION COMPLETE!"
Write-Output "="*80
Write-Output ""
