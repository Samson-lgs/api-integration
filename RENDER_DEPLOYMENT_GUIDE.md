# Air Quality Data Collection - Render Deployment Guide

## 🚀 Deploying to Render with PostgreSQL

This guide will help you deploy the Air Quality Data Collection system to Render cloud platform with automatic data fetching from CPCB, OpenWeather, and IQAir APIs.

---

## 📋 Prerequisites

1. **Render Account** - Sign up at https://render.com (free tier available)
2. **GitHub Account** - To deploy from repository
3. **API Keys** (you already have these):
   - CPCB: `579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd`
   - OpenWeather: `528f129d20a5e514729cbf24b2449e44`
   - IQAir: `102c31e0-0f3c-4865-b4f3-2b4a57e78c40`

---

## 🔧 Step-by-Step Deployment

### Step 1: Prepare Your Code

All necessary files are already created:
- ✅ `app.py` - Flask web service with API endpoints
- ✅ `cloud_collector.py` - Data collection from all 3 APIs
- ✅ `requirements.txt` - Python dependencies
- ✅ `Procfile` - Render deployment configuration
- ✅ `runtime.txt` - Python version specification

### Step 2: Create GitHub Repository

1. Go to https://github.com and create a new repository
2. Name it: `air-quality-collector`
3. Initialize as public or private
4. Push your code:

```bash
cd "c:\Users\Samson Jose\Desktop\api integration"
git init
git add .
git commit -m "Initial commit - Air Quality Collector"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/air-quality-collector.git
git push -u origin main
```

### Step 3: Create PostgreSQL Database on Render

1. Log in to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Configure database:
   - **Name**: `air-quality-db`
   - **Database**: `air_quality`
   - **User**: `air_quality_user`
   - **Region**: Choose closest to India (Singapore recommended)
   - **Plan**: Free tier (sufficient to start)
4. Click **"Create Database"**
5. Wait for database to be created (2-3 minutes)
6. **IMPORTANT**: Copy the **"Internal Database URL"** - you'll need this!

### Step 4: Deploy Web Service on Render

1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:

   **Basic Settings:**
   - **Name**: `air-quality-collector`
   - **Region**: Same as database (Singapore)
   - **Branch**: `main`
   - **Root Directory**: Leave blank
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free tier

   **Environment Variables** (click "Add Environment Variable"):
   
   Add these one by one:
   
   | Key | Value |
   |-----|-------|
   | `DATABASE_URL` | [Paste Internal Database URL from Step 3] |
   | `CPCB_API_KEY` | `579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd` |
   | `OPENWEATHER_API_KEY` | `528f129d20a5e514729cbf24b2449e44` |
   | `IQAIR_API_KEY` | `102c31e0-0f3c-4865-b4f3-2b4a57e78c40` |
   | `PORT` | `10000` |

4. Click **"Create Web Service"**
5. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Start the service
   - Deploy at: `https://air-quality-collector.onrender.com`

### Step 5: Verify Deployment

Once deployed (5-10 minutes), test your endpoints:

1. **Health Check**:
   ```
   https://your-service.onrender.com/health
   ```

2. **Trigger Manual Collection**:
   ```
   POST https://your-service.onrender.com/collect
   ```

3. **View Statistics**:
   ```
   https://your-service.onrender.com/stats
   ```

4. **Get Latest Data**:
   ```
   https://your-service.onrender.com/latest?limit=20
   ```

5. **Get City Data**:
   ```
   https://your-service.onrender.com/city/Delhi
   ```

---

## 🤖 Automatic Data Collection

The system automatically collects data **every 1 hour** from all 3 APIs:
- CPCB (up to 1000 records)
- OpenWeather (15 major cities)
- IQAir (10 major cities)

**Scheduler Configuration** (in `app.py`):
```python
scheduler.add_job(func=scheduled_collection, trigger="interval", hours=1)
```

To change frequency, modify the hours value and redeploy.

---

## 📊 API Endpoints

### 1. Home (`GET /`)
Returns API documentation and available endpoints.

### 2. Health Check (`GET /health`)
Returns service status and database connectivity.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "stations": 450
}
```

### 3. Manual Collection (`POST /collect`)
Triggers immediate data collection from all sources.

**Response:**
```json
{
  "status": "success",
  "stations": 450,
  "data_points": 3500
}
```

### 4. Statistics (`GET /stats`)
Returns comprehensive database statistics.

**Response:**
```json
{
  "total_stations": 450,
  "total_data_points": 3500,
  "by_source": [
    {"source": "CPCB", "stations": 420, "data_points": 3000},
    {"source": "OpenWeather", "stations": 15, "data_points": 300},
    {"source": "IQAir", "stations": 10, "data_points": 200}
  ],
  "pollutants": [
    {"pollutant": "PM2.5", "count": 500},
    {"pollutant": "PM10", "count": 450}
  ]
}
```

### 5. Latest Data (`GET /latest?limit=20`)
Returns the most recent air quality readings.

**Parameters:**
- `limit` (optional): Number of records (default: 20)

### 6. City Data (`GET /city/<city_name>`)
Returns all data for a specific city.

**Example:** `/city/Delhi`

---

## 🗄️ Database Schema

### `stations` Table
- `station_id` (Primary Key) - Unique station identifier
- `station_name` - Full station name
- `city` - City name
- `state` - State name
- `country` - Country (India)
- `latitude`, `longitude` - GPS coordinates
- `data_source` - CPCB/OpenWeather/IQAir
- `created_at`, `updated_at` - Timestamps

### `air_quality_data` Table
- `id` (Primary Key) - Auto-increment ID
- `station_id` (Foreign Key) - Links to stations
- `recorded_at` - Measurement timestamp
- `data_source` - Source of data
- `pollutant_id` - PM2.5, PM10, NO2, SO2, CO, O3, NH3
- `pollutant_avg` - Average concentration
- `pollutant_min`, `pollutant_max` - Min/max values
- `aqi` - Air Quality Index
- `aqi_category` - Good/Moderate/Poor/etc.
- `temperature`, `humidity`, `pressure`, `wind_speed` - Weather data
- `created_at` - Record creation time

---

## 📈 Monitoring Your Deployment

### View Logs
1. Go to Render Dashboard
2. Select your web service
3. Click "Logs" tab
4. Monitor real-time data collection

### Check Database
1. Go to your PostgreSQL database in Render
2. Click "Connect" → "External Connection"
3. Use any PostgreSQL client (pgAdmin, DBeaver, etc.) to query data

### View Metrics
- Render provides built-in metrics for:
  - CPU usage
  - Memory usage
  - Request count
  - Response times

---

## 💰 Cost Estimate

**Free Tier (Sufficient for Testing):**
- Web Service: Free (750 hours/month)
- PostgreSQL: Free (90 days, then $7/month)
- Bandwidth: 100 GB/month free

**Paid Tier (For Production):**
- Web Service: $7/month (always on)
- PostgreSQL: $7/month (persistent storage)
- Total: ~$14/month

---

## 🔧 Troubleshooting

### Service Not Starting
- Check logs for errors
- Verify all environment variables are set
- Ensure DATABASE_URL is correct

### Data Not Collecting
- Check API keys are valid
- Verify internet connectivity
- Check rate limits on APIs

### Database Connection Error
- Verify DATABASE_URL format
- Ensure database is running
- Check if database accepts connections

### IQAir Rate Limits
- IQAir free tier has limits
- System will continue with CPCB + OpenWeather
- Consider upgrading IQAir plan if needed

---

## 🚀 Next Steps After Deployment

### 1. Test the System
```bash
# Health check
curl https://your-service.onrender.com/health

# Trigger collection
curl -X POST https://your-service.onrender.com/collect

# Get stats
curl https://your-service.onrender.com/stats

# Get Delhi data
curl https://your-service.onrender.com/city/Delhi
```

### 2. Access Your Data

**Via API:**
```python
import requests

# Get latest data
response = requests.get('https://your-service.onrender.com/latest')
data = response.json()
print(data)
```

**Via Database:**
```python
import psycopg2
import pandas as pd

conn = psycopg2.connect("YOUR_DATABASE_URL")
df = pd.read_sql("SELECT * FROM air_quality_data LIMIT 100", conn)
print(df)
```

### 3. Build Your ML Model
```python
# Connect to your cloud database
df = pd.read_sql("""
    SELECT * FROM air_quality_data 
    WHERE recorded_at > NOW() - INTERVAL '7 days'
""", conn)

# Train model
# ... your ML code here
```

---

## 📞 Support & Resources

**Render Documentation:**
- https://render.com/docs
- https://render.com/docs/deploy-flask

**API Documentation:**
- CPCB: https://api.data.gov.in
- OpenWeather: https://openweathermap.org/api
- IQAir: https://www.iqair.com/air-pollution-data-api

**Monitoring:**
- Render Dashboard: https://dashboard.render.com
- Service Logs: Real-time in dashboard
- Database Metrics: Available in PostgreSQL dashboard

---

## ✅ Deployment Checklist

- [ ] GitHub repository created and code pushed
- [ ] PostgreSQL database created on Render
- [ ] Database URL copied
- [ ] Web service created on Render
- [ ] All environment variables configured
- [ ] Service deployed successfully
- [ ] Health check endpoint returns success
- [ ] Manual collection triggered successfully
- [ ] Data visible in database
- [ ] Automatic hourly collection working

---

## 🎉 SUCCESS!

Once deployed, your system will:
- ✅ Automatically collect data every hour
- ✅ Store data in PostgreSQL cloud database
- ✅ Provide REST API for data access
- ✅ Run 24/7 on Render cloud
- ✅ Scale automatically as needed

**Your Air Quality Data Collection system is now LIVE in the cloud!** 🚀
