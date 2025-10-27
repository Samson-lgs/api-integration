# ☁️ Cloud Air Quality Data Collector

Automated air quality data collection system deployed on **Render** cloud platform with **PostgreSQL** database. Collects data from **CPCB**, **OpenWeather**, and **IQAir** APIs automatically every hour.

## 🌟 Features

- ✅ **Automatic Data Collection** - Runs every hour without manual intervention
- ✅ **Multi-Source Integration** - CPCB + OpenWeather + IQAir APIs
- ✅ **PostgreSQL Database** - Cloud-hosted persistent storage
- ✅ **REST API** - Easy data access via HTTP endpoints
- ✅ **Real-time Monitoring** - Live logs and metrics
- ✅ **Scalable** - Handles growing data automatically
- ✅ **24/7 Availability** - Always-on cloud service

## 📊 Data Coverage

- **CPCB**: 420+ monitoring stations across India
- **OpenWeather**: 15 major cities with weather parameters
- **IQAir**: 10 major cities
- **Pollutants**: PM2.5, PM10, NO2, SO2, CO, O3, NH3
- **Additional Data**: Temperature, humidity, pressure, wind speed

## 🚀 Quick Start

### Prerequisites
- Render account (https://render.com)
- GitHub account
- API keys (already configured in project)

### Deployment Steps

1. **Push to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

2. **Create PostgreSQL Database on Render**
   - Go to Render Dashboard
   - New + → PostgreSQL
   - Name: `air-quality-db`
   - Copy Internal Database URL

3. **Deploy Web Service**
   - New + → Web Service
   - Connect GitHub repo
   - Add environment variables:
     - `DATABASE_URL`: [Your PostgreSQL URL]
     - `CPCB_API_KEY`: `579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd`
     - `OPENWEATHER_API_KEY`: `528f129d20a5e514729cbf24b2449e44`
     - `IQAIR_API_KEY`: `102c31e0-0f3c-4865-b4f3-2b4a57e78c40`
   - Deploy!

4. **Verify Deployment**
   ```bash
   curl https://your-service.onrender.com/health
   ```

## 📡 API Endpoints

### GET /
API documentation and available endpoints

### GET /health
Service health check and database status

### POST /collect
Manually trigger data collection

### GET /stats
Database statistics and counts

### GET /latest?limit=20
Get latest air quality readings

### GET /city/<city_name>
Get data for specific city (e.g., `/city/Delhi`)

## 📊 Example Usage

### Python
```python
import requests

# Get latest data
response = requests.get('https://your-service.onrender.com/latest')
data = response.json()

# Get Delhi data
response = requests.get('https://your-service.onrender.com/city/Delhi')
delhi_data = response.json()

# Trigger manual collection
response = requests.post('https://your-service.onrender.com/collect')
result = response.json()
```

### JavaScript
```javascript
// Get latest data
fetch('https://your-service.onrender.com/latest')
  .then(response => response.json())
  .then(data => console.log(data));

// Get statistics
fetch('https://your-service.onrender.com/stats')
  .then(response => response.json())
  .then(stats => console.log(stats));
```

## 🗄️ Database Access

Connect directly to PostgreSQL for advanced queries:

```python
import psycopg2
import pandas as pd

# Use DATABASE_URL from Render
conn = psycopg2.connect(DATABASE_URL)

# Query data
df = pd.read_sql("""
    SELECT * FROM air_quality_data 
    WHERE city = 'Delhi' 
    AND recorded_at > NOW() - INTERVAL '24 hours'
""", conn)

# Use for ML model
X = df[['pollutant_avg', 'temperature', 'humidity']]
y = df['aqi']
```

## 🔄 Automatic Collection Schedule

- **Frequency**: Every 1 hour
- **Sources**: CPCB, OpenWeather, IQAir
- **Records per run**: 1000+ data points
- **Storage**: Persistent PostgreSQL database

## 📁 Project Structure

```
air-quality-collector/
├── app.py                      # Flask web service
├── cloud_collector.py          # Data collection logic
├── requirements.txt            # Python dependencies
├── Procfile                    # Render deployment config
├── runtime.txt                 # Python version
├── RENDER_DEPLOYMENT_GUIDE.md  # Detailed deployment guide
└── README_CLOUD.md            # This file
```

## 🔧 Configuration

### Environment Variables (Render)
- `DATABASE_URL` - PostgreSQL connection string
- `CPCB_API_KEY` - CPCB API authentication
- `OPENWEATHER_API_KEY` - OpenWeather API key
- `IQAIR_API_KEY` - IQAir API key
- `PORT` - Service port (default: 10000)

### Modify Collection Frequency

Edit `app.py`:
```python
# Change from 1 hour to 30 minutes
scheduler.add_job(func=scheduled_collection, trigger="interval", minutes=30)
```

## 📊 Database Schema

### stations
- station_id, station_name, city, state, country
- latitude, longitude, data_source
- created_at, updated_at

### air_quality_data
- id, station_id, recorded_at, data_source
- pollutant_id, pollutant_avg, pollutant_min, pollutant_max
- aqi, aqi_category
- temperature, humidity, pressure, wind_speed
- created_at

## 💰 Cost

**Free Tier:**
- Web Service: 750 hours/month free
- PostgreSQL: 90 days free trial
- Perfect for testing and development

**Paid Tier:**
- ~$14/month for production use
- Unlimited data storage
- Always-on service

## 🎯 Use Cases

1. **Air Quality Prediction**
   - Train ML models on collected data
   - Predict future AQI values

2. **Real-time Monitoring**
   - Dashboard integration
   - Alert systems

3. **Data Analysis**
   - Historical trends
   - City comparisons
   - Pollutant correlations

4. **Research**
   - Environmental studies
   - Health impact analysis

## 📞 Support

- **Deployment Issues**: See RENDER_DEPLOYMENT_GUIDE.md
- **API Questions**: Check endpoint documentation at `/`
- **Database Help**: Render PostgreSQL docs

## ✅ Deployment Checklist

- [ ] GitHub repo created
- [ ] PostgreSQL database on Render
- [ ] Web service deployed
- [ ] Environment variables set
- [ ] Health check passes
- [ ] First collection successful
- [ ] Hourly schedule working

## 🎉 Success!

Once deployed, your system:
- ✅ Collects data automatically every hour
- ✅ Stores in cloud PostgreSQL database
- ✅ Provides REST API for access
- ✅ Runs 24/7 without intervention
- ✅ Ready for AQI prediction models

**Your cloud-based air quality data collection system is live!** 🚀

---

For detailed deployment instructions, see: **RENDER_DEPLOYMENT_GUIDE.md**
