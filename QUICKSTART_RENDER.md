# 🚀 RENDER CLOUD DEPLOYMENT - QUICK START

## ✅ Everything is Ready for Cloud Deployment!

Your air quality data collection system is now configured for **Render cloud deployment** with **PostgreSQL** database and **automatic hourly data collection** from CPCB, OpenWeather, and IQAir APIs.

---

## 📦 What's Been Created

### Core Application Files
1. **`app.py`** - Flask web service with REST API endpoints
2. **`cloud_collector.py`** - Multi-source data collector (CPCB + OpenWeather + IQAir)

### Deployment Configuration
3. **`Procfile`** - Render deployment instructions
4. **`runtime.txt`** - Python 3.11 specification
5. **`requirements.txt`** - All Python dependencies
6. **`.gitignore`** - Excludes local files from git

### Documentation
7. **`RENDER_DEPLOYMENT_GUIDE.md`** - Complete step-by-step deployment guide
8. **`README_CLOUD.md`** - Cloud project documentation

---

## 🎯 What the System Does

### Automatic Collection (Every Hour)
- 📡 **CPCB**: 420+ stations across India
- 🌤️ **OpenWeather**: 15 major cities with weather data
- 🌍 **IQAir**: 10 major cities

### Data Storage
- 💾 **PostgreSQL**: Cloud database on Render
- 📊 **Schema**: Stations + Air Quality Data tables
- 🔄 **Auto-update**: Hourly scheduled collection

### REST API Endpoints
- `GET /` - API documentation
- `GET /health` - Health check
- `POST /collect` - Manual trigger
- `GET /stats` - Database statistics
- `GET /latest` - Latest readings
- `GET /city/<name>` - City-specific data

---

## 🚀 3-STEP DEPLOYMENT

### Step 1: Push to GitHub (2 minutes)

```bash
cd "c:\Users\Samson Jose\Desktop\api integration"

# Initialize git repository
git init

# Add all files
git add .

# Commit
git commit -m "Air Quality Collector - Ready for Render"

# Create GitHub repo at https://github.com/new
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/air-quality-collector.git
git push -u origin main
```

### Step 2: Create PostgreSQL Database (3 minutes)

1. Go to https://dashboard.render.com
2. Click **"New +"** → **"PostgreSQL"**
3. Settings:
   - Name: `air-quality-db`
   - Region: Singapore (closest to India)
   - Plan: Free
4. Click **"Create Database"**
5. **COPY** the "Internal Database URL" (Important!)

### Step 3: Deploy Web Service (5 minutes)

1. In Render Dashboard: **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure:
   - Name: `air-quality-collector`
   - Region: Singapore
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:app`
4. **Add Environment Variables**:

```
DATABASE_URL = [Paste your PostgreSQL URL from Step 2]
CPCB_API_KEY = 579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd
OPENWEATHER_API_KEY = 528f129d20a5e514729cbf24b2449e44
IQAIR_API_KEY = 102c31e0-0f3c-4865-b4f3-2b4a57e78c40
PORT = 10000
```

5. Click **"Create Web Service"**
6. Wait 5-10 minutes for deployment

---

## ✅ Verify Deployment

Once deployed, test these URLs (replace with your actual URL):

### 1. Health Check
```
https://air-quality-collector.onrender.com/health
```
Should return: `{"status": "healthy", "database": "connected"}`

### 2. Trigger Collection
```bash
curl -X POST https://air-quality-collector.onrender.com/collect
```

### 3. View Statistics
```
https://air-quality-collector.onrender.com/stats
```

### 4. Get Latest Data
```
https://air-quality-collector.onrender.com/latest?limit=10
```

### 5. Get City Data
```
https://air-quality-collector.onrender.com/city/Delhi
```

---

## 📊 How It Works

```
┌─────────────────────────────────────────────────────┐
│  Render Cloud Platform (24/7)                       │
│                                                      │
│  ┌────────────────────────────────────────────┐    │
│  │  Flask Web Service (app.py)                 │    │
│  │                                              │    │
│  │  ┌──────────────────────────────────────┐  │    │
│  │  │  Scheduler (Every 1 Hour)             │  │    │
│  │  │                                        │  │    │
│  │  │  cloud_collector.py                   │  │    │
│  │  │  ├── CPCB API      ──→ 420 stations   │  │    │
│  │  │  ├── OpenWeather   ──→  15 cities     │  │    │
│  │  │  └── IQAir         ──→  10 cities     │  │    │
│  │  └──────────────────────────────────────┘  │    │
│  │               ↓                              │    │
│  │  ┌──────────────────────────────────────┐  │    │
│  │  │  REST API Endpoints                   │  │    │
│  │  │  /health, /stats, /latest, /city/*   │  │    │
│  │  └──────────────────────────────────────┘  │    │
│  └────────────────────────────────────────────┘    │
│                      ↓                               │
│  ┌────────────────────────────────────────────┐    │
│  │  PostgreSQL Database                        │    │
│  │  ├── stations (430+ stations)              │    │
│  │  └── air_quality_data (growing hourly)    │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

---

## 🎯 After Deployment

### Access Your Data

**Via API:**
```python
import requests

# Get latest data
response = requests.get('https://your-service.onrender.com/latest')
data = response.json()
print(f"Total records: {data['count']}")
```

**Via Database:**
```python
import psycopg2
import pandas as pd

# Connect to your cloud database
conn = psycopg2.connect(DATABASE_URL)

# Query data
df = pd.read_sql("""
    SELECT * FROM air_quality_data 
    WHERE city = 'Delhi' 
    ORDER BY recorded_at DESC 
    LIMIT 100
""", conn)

# Use for ML model
print(df.head())
```

### Build ML Model
```python
# Load data from cloud
df = pd.read_sql("""
    SELECT 
        s.city,
        aq.pollutant_id,
        aq.pollutant_avg,
        aq.aqi,
        aq.temperature,
        aq.humidity
    FROM air_quality_data aq
    JOIN stations s ON aq.station_id = s.station_id
    WHERE aq.recorded_at > NOW() - INTERVAL '7 days'
""", conn)

# Pivot and prepare
pivot = df.pivot_table(
    index=['city', 'temperature', 'humidity'],
    columns='pollutant_id',
    values='pollutant_avg'
).reset_index()

# Train model
from sklearn.ensemble import RandomForestRegressor
X = pivot[['PM2.5', 'PM10', 'NO2', 'temperature', 'humidity']].fillna(0)
y = df['aqi']

model = RandomForestRegressor()
model.fit(X, y)
```

---

## 📈 Monitoring

### View Logs
1. Render Dashboard → Your Service → "Logs"
2. See real-time collection activity
3. Monitor errors and performance

### Check Database
1. Render Dashboard → PostgreSQL → "Connect"
2. Use connection string with pgAdmin or DBeaver
3. Query tables directly

### Metrics
- CPU/Memory usage in Render dashboard
- Request counts and response times
- Database size and performance

---

## 💰 Cost

**Free Tier (Perfect for Start):**
- ✅ Web Service: 750 hours/month
- ✅ PostgreSQL: 90 days free
- ✅ Bandwidth: 100GB/month
- ✅ Good for testing and development

**Upgrade Later ($14/month):**
- Always-on service
- Persistent PostgreSQL
- Unlimited storage

---

## 🎉 SUCCESS CRITERIA

After deployment, you should have:
- ✅ Service live at: `https://your-service.onrender.com`
- ✅ Database populated with air quality data
- ✅ Automatic hourly collection running
- ✅ REST API accessible worldwide
- ✅ Data ready for ML model training

---

## 📞 Need Help?

**Detailed Guide:** See `RENDER_DEPLOYMENT_GUIDE.md`

**Common Issues:**
- Service not starting → Check logs for errors
- Database error → Verify DATABASE_URL
- No data → Check API keys in environment variables
- Rate limits → IQAir has limits, CPCB + OpenWeather will continue

**Resources:**
- Render Docs: https://render.com/docs
- GitHub: Push code first
- Support: Render community forum

---

## ✅ DEPLOYMENT CHECKLIST

Complete these steps:

- [ ] **Step 1**: Push code to GitHub
- [ ] **Step 2**: Create PostgreSQL on Render
- [ ] **Step 3**: Deploy Web Service on Render
- [ ] **Step 4**: Add environment variables
- [ ] **Step 5**: Wait for deployment (5-10 min)
- [ ] **Step 6**: Test /health endpoint
- [ ] **Step 7**: Trigger first collection
- [ ] **Step 8**: Verify data in database
- [ ] **Step 9**: Check hourly schedule works
- [ ] **Step 10**: Start building ML models!

---

## 🚀 READY TO DEPLOY!

All files are configured and ready. Just follow the 3 steps above:

1. **Push to GitHub** (2 min)
2. **Create PostgreSQL** (3 min)
3. **Deploy Web Service** (5 min)

**Total Time: ~10 minutes**

**Your cloud-based air quality data collection system with automatic PostgreSQL storage will be LIVE!** 🎉

---

**See `RENDER_DEPLOYMENT_GUIDE.md` for detailed instructions!**
