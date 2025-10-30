# Production Deployment Guide - AQI Prediction System

## System Architecture

The production system consists of:

1. **PostgreSQL Database** - Stores raw air quality data and predictions
2. **Production API** (`backend/production_api.py`) - Serves data and predictions
3. **Data Collector** (`real_time_collector.py`) - Fetches from OpenWeather, IQAir, CPCB
4. **ML Engine** (`ml_prediction_engine.py`) - Trains models and generates predictions
5. **Automated Scheduler** (`automated_scheduler.py`) - Runs hourly collection & daily retraining
6. **React Frontend** - Interactive dashboard with predictions

## Pre-Deployment Setup

### 1. Register for API Keys (CRITICAL)

#### OpenWeather API (Air Pollution)
- Visit: https://openweathermap.org/api
- Sign up for free account
- Subscribe to "Air Pollution API" (Free tier: 60 calls/min)
- Copy your API key
- **Cost**: FREE (1,000 calls/day)

#### IQAir API (AirVisual)
- Visit: https://www.iqair.com/air-pollution-data-api
- Request free Community plan
- **Cost**: FREE (10,000 calls/month)

#### CPCB API (Optional - Government Data)
- Visit: https://data.gov.in/
- Register for API access
- Search for "air quality" datasets
- **Cost**: FREE

### 2. Prepare Environment Variables

Create a `.env` file with:

```env
# Database
DATABASE_URL=postgresql://user:password@host:5432/aqi_prediction_db

# API Keys
OPENWEATHER_API_KEY=your_openweather_key_here
IQAIR_API_KEY=your_iqair_key_here
CPCB_API_KEY=your_cpcb_key_here

# Flask
FLASK_ENV=production
SECRET_KEY=your_secret_key_here
```

## Deployment Steps

### Option 1: Deploy to Render (Recommended)

#### Step 1: Create Render Account
1. Go to https://render.com/
2. Sign up with GitHub account
3. Link your repository

#### Step 2: Create PostgreSQL Database
1. Click "New +" → "PostgreSQL"
2. Name: `aqi-postgres`
3. Database: `aqi_prediction_db`
4. User: `aqi_user`
5. Region: Oregon
6. Plan: **Starter ($7/month)** or Free
7. Click "Create Database"
8. Copy the **Internal Database URL**

#### Step 3: Run Database Schema
1. Connect to database using provided credentials
2. Run the SQL from `backend/database/prediction_schema.sql`

```bash
psql -h <host> -U <user> -d aqi_prediction_db -f backend/database/prediction_schema.sql
```

Or use Render's built-in SQL console.

#### Step 4: Deploy Backend API
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Settings:
   - **Name**: `aqi-prediction-api`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python backend/production_api.py`
   - **Plan**: Starter ($7/month)
4. Add Environment Variables:
   - `DATABASE_URL` - paste from Step 2
   - `OPENWEATHER_API_KEY` - your key
   - `IQAIR_API_KEY` - your key
   - `CPCB_API_KEY` - your key (if available)
   - `FLASK_ENV` - production
5. Click "Create Web Service"

#### Step 5: Deploy Data Collector Worker
1. Click "New +" → "Background Worker"
2. Settings:
   - **Name**: `aqi-scheduler`
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python automated_scheduler.py`
   - **Plan**: Starter ($7/month)
3. Add same environment variables as Step 4
4. Click "Create Worker"

#### Step 6: Deploy Frontend
1. Click "New +" → "Static Site"
2. Settings:
   - **Name**: `aqi-prediction-frontend`
   - **Build Command**: `cd frontend && npm install && npm run build`
   - **Publish Directory**: `frontend/dist`
3. Add Environment Variable:
   - `VITE_API_URL` - your backend URL from Step 4 (e.g., `https://aqi-prediction-api.onrender.com`)
4. Click "Create Static Site"

### Option 2: Deploy with Docker (Alternative)

```bash
# Build and run all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

## Post-Deployment Verification

### 1. Check API Health
```bash
curl https://your-api-url.onrender.com/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "message": "API and database operational",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

### 2. Verify Data Collection
Check the `collection_logs` table:

```sql
SELECT * FROM collection_logs ORDER BY timestamp DESC LIMIT 10;
```

You should see successful collection entries every hour.

### 3. Check Predictions
```bash
curl https://your-api-url.onrender.com/api/predictions/Delhi
```

### 4. Monitor Logs
In Render dashboard:
- Go to your services
- Click "Logs" tab
- Look for:
  - `HOURLY DATA COLLECTION COMPLETED`
  - `PREDICTION GENERATION COMPLETED`
  - `MODEL RETRAINING COMPLETED`

## System Operation Schedule

The automated scheduler runs:

| Task | Frequency | Time |
|------|-----------|------|
| Data Collection | Hourly | :00 minutes |
| Prediction Generation | Hourly | :15 minutes |
| Model Retraining | Daily | 2:00 AM |
| Health Alerts | Every 30 min | - |

## Monitoring & Maintenance

### 1. Check System Stats
```bash
curl https://your-api-url.onrender.com/api/stats
```

### 2. Monitor API Rate Limits
- OpenWeather: 60 calls/min (monitor in logs)
- IQAir: 10,000 calls/month (check usage at IQAir dashboard)

### 3. Database Maintenance
Run cleanup monthly to remove old data:

```sql
SELECT cleanup_old_data();
```

### 4. Model Performance
Check model metrics:

```bash
curl https://your-api-url.onrender.com/api/model-info
```

Look for:
- **MAE** (Mean Absolute Error) - should be < 30
- **RMSE** - should be < 50
- **R² Score** - should be > 0.7

## Cost Estimate (Render)

| Service | Plan | Monthly Cost |
|---------|------|--------------|
| PostgreSQL | Starter | $7 |
| Backend API | Starter | $7 |
| Scheduler Worker | Starter | $7 |
| Frontend | Free | $0 |
| **TOTAL** | | **$21/month** |

Alternative: Use Free tier for all services (with limitations)

## Troubleshooting

### Issue: No data being collected
- Check API keys in environment variables
- Verify worker is running (check logs)
- Check `collection_logs` table for errors

### Issue: No predictions available
- Ensure model has been trained (check `models/` directory)
- Run manual training: `python ml_prediction_engine.py`
- Check prediction worker logs

### Issue: API returning errors
- Check database connection
- Verify DATABASE_URL is correct
- Check API service logs in Render dashboard

### Issue: Frontend not loading
- Verify VITE_API_URL points to correct backend
- Check CORS settings in backend
- Open browser console for errors

## Manual Operations

### Train Models Manually
```bash
python ml_prediction_engine.py
```

### Collect Data Now
```bash
python real_time_collector.py
```

### Generate Predictions
```python
from ml_prediction_engine import AQIPredictionEngine

engine = AQIPredictionEngine(model_type='xgboost')
engine.load_model()
predictions = engine.predict_future('Delhi', hours_ahead=48)
engine.store_predictions(predictions)
```

## Scaling Considerations

### High Traffic
- Upgrade Render plans to "Standard" ($25/month)
- Enable auto-scaling in render.yaml
- Add Redis for caching predictions

### More Cities
- Add cities to `real_time_collector.py` (line 18)
- Ensure API rate limits are not exceeded
- Consider batching API calls

### Better Predictions
- Increase training data retention (currently 30 days)
- Implement LSTM models for time-series
- Add weather forecast data as features

## Support & Updates

- Monitor Render logs daily
- Check prediction accuracy weekly
- Retrain models if performance drops
- Update API keys before expiration

## Security Notes

- Never commit `.env` file
- Rotate API keys every 6 months
- Use environment variables in production
- Enable SSL/HTTPS (automatic on Render)
- Restrict database access to Render services only

## Success Indicators

✅ Data collected every hour
✅ Predictions available for all cities
✅ Model accuracy > 70%
✅ API response time < 500ms
✅ No errors in logs for 24 hours
✅ Frontend displays live data

Your system is now live! 🚀

Monitor at: https://your-frontend-url.onrender.com
