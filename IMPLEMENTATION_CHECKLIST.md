# AQI Prediction System - Implementation Checklist

## Overview
Track your progress from setup to production deployment.

---

## Phase 1: API Registration (Est. Time: 30 min + 1-2 days wait)

### OpenWeather API ⭐ CRITICAL
- [ ] Visit https://openweathermap.org/
- [ ] Create account
- [ ] Verify email
- [ ] Subscribe to "Air Pollution API" (FREE plan)
- [ ] Copy API key
- [ ] Paste in `.env` file
- [ ] Test: Run `python test_api_keys.py`

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### IQAir API ⭐ CRITICAL
- [ ] Visit https://www.iqair.com/air-pollution-data-api
- [ ] Request "Community Edition" (FREE)
- [ ] Fill application form
- [ ] Wait for approval email (1-2 days)
- [ ] Copy API key from email
- [ ] Paste in `.env` file
- [ ] Test: Run `python test_api_keys.py`

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### CPCB API (OPTIONAL)
- [ ] Visit https://data.gov.in/
- [ ] Register account
- [ ] Search for "air quality" datasets
- [ ] Request API access
- [ ] Wait for approval (3-7 days)
- [ ] Copy API key
- [ ] Paste in `.env` file

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete | ⬜ Skipped

---

## Phase 2: Local Environment Setup (Est. Time: 1 hour)

### Python Environment
- [ ] Python 3.11+ installed
- [ ] Create virtual environment: `python -m venv venv`
- [ ] Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify installation: `python --version`

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### PostgreSQL Database
- [ ] PostgreSQL 15+ installed
- [ ] PostgreSQL server running
- [ ] Create database: `createdb aqi_prediction_db`
- [ ] Run schema: `psql -d aqi_prediction_db -f backend/database/prediction_schema.sql`
- [ ] Verify tables: `psql -d aqi_prediction_db -c "\dt"`
- [ ] Update `DATABASE_URL` in `.env`

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Environment Configuration
- [ ] Create `.env` file in project root
- [ ] Add `OPENWEATHER_API_KEY`
- [ ] Add `IQAIR_API_KEY`
- [ ] Add `CPCB_API_KEY` (optional)
- [ ] Add `DATABASE_URL`
- [ ] Add `FLASK_ENV=development`
- [ ] Add `SECRET_KEY=dev_secret_123`
- [ ] Verify: Check `.env` file exists and has correct format

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Frontend Setup
- [ ] Node.js 18+ installed
- [ ] Navigate to `frontend/` directory
- [ ] Run: `npm install`
- [ ] Verify: `node_modules/` created
- [ ] Test: `npm run dev` (should start on localhost:3000)

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

## Phase 3: Local Testing (Est. Time: 30 minutes)

### Validate API Keys
- [ ] Run: `python test_api_keys.py`
- [ ] See ✓ for OpenWeather API
- [ ] See ✓ for IQAir API
- [ ] Fix any errors shown

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Test Data Collection
- [ ] Run: `python real_time_collector.py`
- [ ] Watch console for "Collecting data from OpenWeather..."
- [ ] Watch console for "Collecting data from IQAir..."
- [ ] Check database: `SELECT COUNT(*) FROM raw_air_quality_data;`
- [ ] Should see 20-30 records per city
- [ ] Verify no errors in console

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Train ML Models
- [ ] Run: `python ml_prediction_engine.py`
- [ ] Wait for "Training XGBoost model..."
- [ ] See model evaluation metrics (MAE, RMSE, R²)
- [ ] Check `models/` directory created
- [ ] Verify files: `aqi_model_xgboost.pkl`, `aqi_scaler_xgboost.pkl`, `metrics.json`

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Test Production API
- [ ] Open Terminal 1
- [ ] Run: `python backend/production_api.py`
- [ ] See "Running on http://127.0.0.1:5000"
- [ ] Test in browser: http://localhost:5000/api/health
- [ ] Should see: `{"status": "healthy"}`
- [ ] Test: http://localhost:5000/api/cities
- [ ] Should see list of cities with AQI

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Test Frontend
- [ ] Open Terminal 2 (keep API running in Terminal 1)
- [ ] Run: `cd frontend && npm run dev`
- [ ] See "Local: http://localhost:3000"
- [ ] Open browser: http://localhost:3000
- [ ] Dashboard page loads
- [ ] See "Latest Air Quality Readings" table
- [ ] See PM2.5 Trends chart
- [ ] See health advisory
- [ ] Click "Predictions" - see 48-hour forecast
- [ ] Click "Compare Cities" - see comparison

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Test Automated Scheduler
- [ ] Stop backend API (Ctrl+C in Terminal 1)
- [ ] Run: `python automated_scheduler.py`
- [ ] See "HOURLY DATA COLLECTION STARTED"
- [ ] Wait 1-2 minutes for completion
- [ ] See "PREDICTION GENERATION STARTED"
- [ ] See "Scheduler is now running"
- [ ] Leave running for 10 minutes
- [ ] Verify no errors
- [ ] Stop with Ctrl+C

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

## Phase 4: Production Deployment (Est. Time: 2 hours)

### Render Account Setup
- [ ] Visit https://render.com/
- [ ] Sign up with GitHub account
- [ ] Connect your repository
- [ ] Verify email

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### PostgreSQL Database on Render
- [ ] Click "New +" → "PostgreSQL"
- [ ] Name: `aqi-postgres`
- [ ] Database: `aqi_prediction_db`
- [ ] User: `aqi_user`
- [ ] Region: Oregon
- [ ] Plan: Starter ($7/month) or Free
- [ ] Click "Create Database"
- [ ] Wait for database to be ready
- [ ] Copy "Internal Database URL"
- [ ] Save URL for next steps

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Run Database Schema (Remote)
- [ ] Go to Render dashboard → PostgreSQL service
- [ ] Click "Connect" → Copy connection string
- [ ] Open local terminal
- [ ] Run: `psql <connection_string> -f backend/database/prediction_schema.sql`
- [ ] Should see "CREATE TABLE" messages
- [ ] Verify: `psql <connection_string> -c "\dt"`
- [ ] Should see 7 tables

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Deploy Backend API
- [ ] Click "New +" → "Web Service"
- [ ] Connect GitHub repository
- [ ] Name: `aqi-prediction-api`
- [ ] Environment: Python 3
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python backend/production_api.py`
- [ ] Plan: Starter ($7/month)
- [ ] Add Environment Variables:
  - [ ] `DATABASE_URL` - paste from PostgreSQL
  - [ ] `OPENWEATHER_API_KEY` - your key
  - [ ] `IQAIR_API_KEY` - your key
  - [ ] `FLASK_ENV` - `production`
  - [ ] `SECRET_KEY` - generate random string
- [ ] Click "Create Web Service"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Copy service URL (e.g., `https://aqi-prediction-api.onrender.com`)
- [ ] Test: Visit `<URL>/api/health` in browser

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Deploy Scheduler Worker
- [ ] Click "New +" → "Background Worker"
- [ ] Connect GitHub repository
- [ ] Name: `aqi-scheduler`
- [ ] Environment: Python 3
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `python automated_scheduler.py`
- [ ] Plan: Starter ($7/month)
- [ ] Add same environment variables as backend
- [ ] Click "Create Background Worker"
- [ ] Wait for deployment
- [ ] Check logs for "HOURLY DATA COLLECTION STARTED"

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Deploy Frontend
- [ ] Click "New +" → "Static Site"
- [ ] Connect GitHub repository
- [ ] Name: `aqi-prediction-frontend`
- [ ] Build Command: `cd frontend && npm install && npm run build`
- [ ] Publish Directory: `frontend/dist`
- [ ] Add Environment Variable:
  - [ ] `VITE_API_URL` - backend URL from above
- [ ] Click "Create Static Site"
- [ ] Wait for deployment (5-10 minutes)
- [ ] Copy frontend URL (e.g., `https://aqi-prediction-frontend.onrender.com`)
- [ ] Visit URL in browser
- [ ] Dashboard should load with live data

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

## Phase 5: Verification & Monitoring (Est. Time: 1 week)

### Day 1: Immediate Checks
- [ ] Visit frontend URL - dashboard loads
- [ ] Check API health: `<backend-url>/api/health`
- [ ] Check cities endpoint: `<backend-url>/api/cities`
- [ ] Verify data in database (Render console)
- [ ] Check scheduler logs (Render dashboard)
- [ ] Look for "HOURLY DATA COLLECTION COMPLETED"
- [ ] Look for "PREDICTION GENERATION COMPLETED"

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Day 2-7: Daily Monitoring
- [ ] **Day 2**: Check data collected for 24 hours
- [ ] **Day 3**: Verify predictions generated
- [ ] **Day 4**: Check model retraining logs (2 AM)
- [ ] **Day 5**: Verify no errors in last 3 days
- [ ] **Day 6**: Check API rate limits not exceeded
- [ ] **Day 7**: Final verification - system stable

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Performance Validation
- [ ] Check `collection_logs` table: `SELECT * FROM collection_logs ORDER BY timestamp DESC LIMIT 10;`
- [ ] Should see hourly successful collections
- [ ] Check predictions: `SELECT COUNT(*) FROM aqi_predictions;`
- [ ] Should have 48 predictions per city (10 cities = 480 total)
- [ ] Verify model performance: `SELECT * FROM model_metadata WHERE is_active = TRUE;`
- [ ] MAE < 30, RMSE < 50, R² > 0.70
- [ ] Test API response time: Should be < 500ms
- [ ] Frontend loads in < 2 seconds

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

## Phase 6: Go Live! (Est. Time: 1 hour)

### Final Pre-Launch Checks
- [ ] All services running (green in Render dashboard)
- [ ] No errors in logs for 24 hours
- [ ] Database has data from last 7 days
- [ ] Predictions available for all cities
- [ ] Frontend accessible and responsive
- [ ] API responding in < 500ms
- [ ] Models retrained successfully

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

### Launch Activities
- [ ] Announce to stakeholders
- [ ] Share frontend URL
- [ ] Document API endpoints
- [ ] Set up monitoring alerts
- [ ] Schedule weekly check-ins
- [ ] Plan for scaling (if needed)

**Status**: ⬜ Not Started | ⬜ In Progress | ⬜ Complete

---

## Troubleshooting Reference

### Problem: API Keys Not Working
- [ ] Re-run `python test_api_keys.py`
- [ ] Check for typos in `.env`
- [ ] Verify keys copied completely
- [ ] Check API dashboard for usage limits
- [ ] For OpenWeather: Wait 10 minutes after creation

### Problem: No Data Collected
- [ ] Check `collection_logs` table for errors
- [ ] Verify `DATABASE_URL` is correct
- [ ] Check API rate limits
- [ ] Ensure scheduler is running
- [ ] Check Render worker logs

### Problem: No Predictions
- [ ] Verify models are trained: Check `models/` directory
- [ ] Run `python ml_prediction_engine.py` manually
- [ ] Check sufficient data: Need 100+ records
- [ ] Verify predictions table: `SELECT COUNT(*) FROM aqi_predictions;`

### Problem: Frontend Not Loading
- [ ] Check `VITE_API_URL` environment variable
- [ ] Verify backend is running
- [ ] Check browser console for errors
- [ ] Test API directly: `<backend-url>/api/health`
- [ ] Verify CORS settings in backend

### Problem: Database Connection Failed
- [ ] Check `DATABASE_URL` format
- [ ] Verify PostgreSQL service is running
- [ ] Check network connectivity
- [ ] Verify database credentials
- [ ] Check Render database logs

---

## Cost Tracking

### Development (Local)
- OpenWeather API: **FREE**
- IQAir API: **FREE**
- PostgreSQL (Local): **FREE**
- **Total: $0/month** ✅

### Production (Render)
- PostgreSQL Database: **$7/month**
- Backend API Web Service: **$7/month**
- Scheduler Background Worker: **$7/month**
- Frontend Static Site: **FREE**
- **Total: $21/month** 💰

### Alternative: Render Free Tier
- All services: **FREE**
- Limitations: 
  - Spins down after 15 minutes inactivity
  - 750 hours/month (shared across services)
  - Slower performance
- **Total: $0/month** (good for testing)

---

## Success Metrics

### Data Collection ✅
- [ ] 24 data points per city per day
- [ ] <1 hour latency
- [ ] 95%+ success rate
- [ ] All 3 API sources working

### ML Models ✅
- [ ] MAE < 30 AQI points
- [ ] RMSE < 50 AQI points
- [ ] R² Score > 0.70
- [ ] Daily retraining successful

### API Performance ✅
- [ ] Response time < 500ms
- [ ] 99% uptime
- [ ] All 14 endpoints working
- [ ] No errors in 24 hours

### User Experience ✅
- [ ] Dashboard loads < 2 seconds
- [ ] All pages accessible
- [ ] Charts rendering correctly
- [ ] Data updating hourly

---

## Overall Project Status

### Phase Completion
- [ ] Phase 1: API Registration - ___% complete
- [ ] Phase 2: Local Setup - ___% complete
- [ ] Phase 3: Local Testing - ___% complete
- [ ] Phase 4: Production Deployment - ___% complete
- [ ] Phase 5: Verification & Monitoring - ___% complete
- [ ] Phase 6: Go Live! - ___% complete

### Overall Progress: ___% Complete

---

## Next Action Items

**Today:**
1. ____________________________
2. ____________________________
3. ____________________________

**This Week:**
1. ____________________________
2. ____________________________
3. ____________________________

**This Month:**
1. ____________________________
2. ____________________________
3. ____________________________

---

## Notes & Issues

**Date** | **Issue/Note** | **Resolution**
---------|----------------|---------------
         |                |
         |                |
         |                |

---

## Contact & Support

- **Documentation**: See `PRODUCTION_DEPLOYMENT_GUIDE.md`
- **API Keys**: See `API_KEY_REGISTRATION_GUIDE.md`
- **Technical Details**: See `COMPLETE_IMPLEMENTATION_SUMMARY.md`
- **Quick Reference**: See `START_HERE.md`

---

**Last Updated**: ___________  
**Current Phase**: ___________  
**Estimated Completion**: ___________

---

🎯 **Goal**: Production-ready AQI prediction system serving 10 cities with 48-hour forecasts!
