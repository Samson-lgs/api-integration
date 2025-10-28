# 🚀 GO LIVE - Your Personal Deployment Instructions

## ✅ STEP 1: CODE IS ON GITHUB ✓

Your code is successfully pushed to:
**https://github.com/Samson-lgs/api-integration**

---

## 📋 STEP 2: CREATE POSTGRESQL DATABASE ON RENDER

### 2.1 Go to Render
1. Open: **https://dashboard.render.com**
2. Sign in or create free account

### 2.2 Create PostgreSQL Database
1. Click **"New +"** button (top right)
2. Select **"PostgreSQL"**
3. Fill in details:
   ```
   Name: air-quality-db
   Database: air_quality
   User: air_quality_user
   Region: Singapore (closest to India)
   PostgreSQL Version: 16
   Plan: Free
   ```
4. Click **"Create Database"**
5. Wait 2-3 minutes for creation

### 2.3 GET DATABASE URL (IMPORTANT!)
1. Once created, go to database dashboard
2. Scroll down to **"Connections"** section
3. Look for **"Internal Database URL"**
4. Click **"Copy"** button
5. **SAVE THIS URL** - you'll need it in the next step!

The URL looks like:
```
postgresql://user:password@hostname/database
```

---

## 🌐 STEP 3: DEPLOY WEB SERVICE ON RENDER

### 3.1 Create New Web Service
1. In Render Dashboard, click **"New +"** → **"Web Service"**
2. Click **"Connect GitHub"** (if not connected)
3. Authorize Render to access your GitHub
4. Find and select: **"Samson-lgs/api-integration"**
5. Click **"Connect"**

### 3.2 Configure Service
Fill in these details:

**Basic Settings:**
```
Name: air-quality-collector
Region: Singapore
Branch: main
Root Directory: (leave blank)
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

**Instance Type:**
```
Plan: Free
```

### 3.3 Add Environment Variables
Click **"Add Environment Variable"** and add these **5 variables** one by one:

**Variable 1:**
```
Key: DATABASE_URL
Value: [PASTE YOUR POSTGRESQL URL FROM STEP 2.3]
```

**Variable 2:**
```
Key: CPCB_API_KEY
Value: 579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd
```

**Variable 3:**
```
Key: OPENWEATHER_API_KEY
Value: 528f129d20a5e514729cbf24b2449e44
```

**Variable 4:**
```
Key: IQAIR_API_KEY
Value: 102c31e0-0f3c-4865-b4f3-2b4a57e78c40
```

**Variable 5:**
```
Key: PORT
Value: 10000
```

### 3.4 Deploy!
1. Click **"Create Web Service"**
2. Render will start building and deploying
3. Watch the logs (you'll see installation progress)
4. Wait 5-10 minutes for first deployment

---

## ✅ STEP 4: VERIFY YOUR LIVE SERVICE

Once deployment shows "Live" (green dot):

### 4.1 Your Service URL
Render will give you a URL like:
```
https://air-quality-collector.onrender.com
```
or
```
https://air-quality-collector-xxxx.onrender.com
```

### 4.2 Test Health Check
Open in browser or use curl:
```
https://your-service-url.onrender.com/health
```


Should return:
```json
{
  "status": "healthy",
  "database": "connected",
  "stations": 0
}
```

### 4.3 Trigger First Data Collection
Open in browser or use curl:
```bash
curl -X POST https://your-service-url.onrender.com/collect
```

This will collect data from all 3 APIs!

### 4.4 Check Statistics
```
https://your-service-url.onrender.com/stats
```

Should show:
```json
{
  "total_stations": 430+,
  "total_data_points": 1000+,
  "by_source": [...]
}
```

### 4.5 View Latest Data
```
https://your-service-url.onrender.com/latest?limit=10
```

### 4.6 Get City Data
```
https://your-service-url.onrender.com/city/Delhi
```

---

## 🎉 YOU'RE LIVE!

Your air quality data collection system is now:
- ✅ **Live on the internet** at your Render URL
- ✅ **Automatically collecting data** every hour
- ✅ **Storing in PostgreSQL** cloud database
- ✅ **Accessible via REST API** from anywhere
- ✅ **Running 24/7** without your intervention

---

## 📊 MONITORING YOUR LIVE SERVICE

### View Real-Time Logs
1. Go to Render Dashboard
2. Click on your **"air-quality-collector"** service
3. Click **"Logs"** tab
4. Watch data collection in real-time

### Check Database
1. Go to your PostgreSQL database in Render
2. Click **"Connect"** → **"External Connection"**
3. Use these credentials with pgAdmin or any PostgreSQL client

### View Metrics
1. In service dashboard, see:
   - CPU usage
   - Memory usage
   - Request count
   - Uptime

---

## 🔄 AUTOMATIC COLLECTION

Your system now:
- Collects data **every 1 hour** automatically
- Fetches from **CPCB** (420+ stations)
- Fetches from **OpenWeather** (15 cities)
- Fetches from **IQAir** (10 cities)
- Stores everything in **PostgreSQL**

No manual action needed! It runs forever!

---

## 💻 ACCESS YOUR DATA

### Via API (Anywhere)
```python
import requests

# Get latest data
response = requests.get('https://your-service-url.onrender.com/latest')
data = response.json()
print(f"Total: {data['count']} records")
```

### Via Database (Direct)
```python
import psycopg2
import pandas as pd

# Use your DATABASE_URL
conn = psycopg2.connect("your_database_url")
df = pd.read_sql("SELECT * FROM air_quality_data LIMIT 100", conn)
print(df.head())
```

### Build ML Models
```python
# Your data is continuously updated!
# Perfect for real-time AQI prediction

df = pd.read_sql("""
    SELECT * FROM air_quality_data 
    WHERE recorded_at > NOW() - INTERVAL '7 days'
""", conn)

# Train your model
from sklearn.ensemble import RandomForestRegressor
# ... your ML code
```

---

## 🆘 TROUBLESHOOTING

### Service Won't Start
- Check **Logs** tab in Render
- Verify all 5 environment variables are set
- Make sure DATABASE_URL is correct

### No Data Collecting
- Trigger manual collection: `POST /collect`
- Check logs for API errors
- Verify API keys in environment variables

### Database Connection Error
- Verify DATABASE_URL is the Internal URL
- Check database is "Available" in Render
- Try reconnecting database

### Free Tier Limits
- Service sleeps after 15 min of inactivity
- First request after sleep takes ~30 seconds
- Database free for 90 days, then $7/month
- Upgrade to paid tier ($7/month) for always-on service

---

## 💰 COST SUMMARY

**Current (Free Tier):**
- ✅ Web Service: FREE (750 hours/month)
- ✅ PostgreSQL: FREE for 90 days
- ✅ Total: $0/month

**After 90 Days (Recommended):**
- Web Service: $7/month (always-on)
- PostgreSQL: $7/month (persistent)
- Total: $14/month

---

## 🎯 NEXT STEPS

1. ✅ Service is live
2. ✅ Data is collecting hourly
3. ✅ Database is growing
4. 📊 Build your AQI prediction models!
5. 📈 Create dashboards
6. 🚨 Set up alerts for poor air quality

---

## 📞 SUPPORT

**Render Issues:**
- Dashboard: https://dashboard.render.com
- Docs: https://render.com/docs
- Support: https://render.com/support

**Your GitHub Repo:**
- https://github.com/Samson-lgs/api-integration

**Service Endpoints:**
- Replace `your-service-url` with actual Render URL
- All endpoints documented at `/`

---

## ✅ SUCCESS CHECKLIST

After completing all steps:

- [ ] PostgreSQL database created on Render
- [ ] Database URL copied
- [ ] Web service deployed
- [ ] All 5 environment variables added
- [ ] Service shows "Live" (green dot)
- [ ] `/health` endpoint returns healthy
- [ ] First collection triggered successfully
- [ ] `/stats` shows data
- [ ] Automatic hourly collection working
- [ ] You can access data via API

---

## 🎉 CONGRATULATIONS!

**Your Air Quality Data Collection System is LIVE! 🚀**

You now have:
- ✅ Cloud-hosted service on Render
- ✅ PostgreSQL database with air quality data
- ✅ Automatic data collection every hour
- ✅ REST API accessible worldwide
- ✅ Data from 430+ monitoring stations
- ✅ Ready for machine learning models

**Welcome to the cloud! Your AQI prediction project is now operational!** 🌟
