# Deployment Guide - Air Quality Monitoring System

This guide covers containerization with Docker, cloud deployment on Render, automated retraining pipelines, and RESTful API endpoints.

## Table of Contents
1. [Docker Containerization](#docker-containerization)
2. [Local Development with Docker](#local-development-with-docker)
3. [Cloud Deployment on Render](#cloud-deployment-on-render)
4. [Automated Retraining Pipeline](#automated-retraining-pipeline)
5. [RESTful API Endpoints](#restful-api-endpoints)
6. [Environment Configuration](#environment-configuration)
7. [Monitoring & Administration](#monitoring--administration)

---

## Docker Containerization

### Architecture Overview

The application is containerized into 5 services:

1. **PostgreSQL Database** - Time-series optimized data storage
2. **Backend API** - Flask REST API with ML predictions
3. **Frontend** - React SPA with Nginx
4. **Data Collector** - Background worker for data collection
5. **Model Retrainer** - Automated ML model retraining

### Docker Files

#### Backend Dockerfile (`Dockerfile.backend`)
- Multi-stage build for optimized image size
- Python 3.11-slim base image
- Installs all dependencies from `requirements.txt`
- Non-root user for security
- Health check on `/api/health` endpoint
- Exposed port: 5000

#### Frontend Dockerfile (`Dockerfile.frontend`)
- Multi-stage build: Node.js builder + Nginx runtime
- Builds React app with Vite
- Serves static files with Nginx
- Configured proxy to backend API
- Gzip compression enabled
- Exposed port: 80

#### PostgreSQL Dockerfile (`Dockerfile.postgres`)
- PostgreSQL 15-alpine image
- Automatically initializes schema on first run
- Persistent volume for data storage

---

## Local Development with Docker

### Prerequisites
- Docker Desktop 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### Quick Start

1. **Clone the repository**
```powershell
git clone https://github.com/Samson-lgs/api-integration.git
cd api-integration
```

2. **Create environment file**
```powershell
Copy-Item .env.example .env
```

3. **Edit .env file** with your configuration:
```env
# Database
POSTGRES_DB=air_quality_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password

# Flask
FLASK_ENV=development
SECRET_KEY=your_secret_key_here
CORS_ORIGINS=http://localhost:3000,http://localhost

# ML Configuration
AUTO_RETRAIN=true
RETRAIN_INTERVAL_HOURS=24
MIN_NEW_SAMPLES=100

# Data Collection
COLLECTION_INTERVAL_MINUTES=60
```

4. **Build and start all services**
```powershell
docker-compose up -d --build
```

5. **Verify services are running**
```powershell
docker-compose ps
```

Expected output:
```
NAME                        STATUS              PORTS
air_quality_backend         Up (healthy)        0.0.0.0:5000->5000/tcp
air_quality_collector       Up                  
air_quality_db              Up (healthy)        0.0.0.0:5432->5432/tcp
air_quality_frontend        Up (healthy)        0.0.0.0:80->80/tcp
air_quality_retrainer       Up                  
```

6. **Access the application**
- Frontend: http://localhost
- Backend API: http://localhost:5000
- API Health: http://localhost:5000/api/health

### Common Docker Commands

**View logs:**
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f collector
docker-compose logs -f retrainer
```

**Restart services:**
```powershell
docker-compose restart backend
docker-compose restart frontend
```

**Stop all services:**
```powershell
docker-compose down
```

**Stop and remove volumes (clean slate):**
```powershell
docker-compose down -v
```

**Execute commands in containers:**
```powershell
# Access backend shell
docker-compose exec backend bash

# Access database
docker-compose exec postgres psql -U postgres -d air_quality_db

# Run database migrations
docker-compose exec backend python backend/init_db.py
```

**View resource usage:**
```powershell
docker stats
```

---

## Cloud Deployment on Render

### Prerequisites
- Render account (https://render.com)
- GitHub repository
- Domain name (optional)

### Deployment Steps

#### Option 1: Infrastructure as Code (Recommended)

1. **Push code to GitHub**
```powershell
git add .
git commit -m "feat: Add Docker containerization and cloud deployment"
git push origin main
```

2. **Connect Render to GitHub**
- Go to https://dashboard.render.com
- Click "New" → "Blueprint"
- Connect your GitHub repository
- Render will automatically detect `render.yaml`

3. **Review Configuration**
The `render.yaml` file defines:
- PostgreSQL database (Standard plan, 10GB storage)
- Backend API web service (auto-scaling 1-3 instances)
- Frontend web service
- Data collector worker
- Model retrainer worker

4. **Set Environment Variables**
Render will auto-generate:
- `DATABASE_URL` (from PostgreSQL service)
- `SECRET_KEY` (randomly generated)
- `POSTGRES_PASSWORD` (randomly generated)

Custom variables to set:
- `CORS_ORIGINS`: Your frontend URL (e.g., https://air-quality-monitor.onrender.com)
- `COLLECTION_INTERVAL_MINUTES`: 60
- `RETRAIN_INTERVAL_HOURS`: 24

5. **Deploy**
- Click "Apply"
- Render will build and deploy all services
- Initial deployment takes 10-15 minutes

6. **Verify Deployment**
```powershell
# Test backend health
curl https://your-backend-url.onrender.com/api/health

# Test frontend
curl https://your-frontend-url.onrender.com
```

#### Option 2: Manual Deployment

**Database:**
1. New → PostgreSQL
2. Name: air-quality-postgres
3. Plan: Standard
4. Region: Oregon (or closest to users)
5. Create Database

**Backend API:**
1. New → Web Service
2. Connect repository
3. Build Command: `docker build -f Dockerfile.backend -t backend .`
4. Start Command: `python backend/api.py`
5. Plan: Standard
6. Environment Variables:
   - Add DATABASE_URL from database
   - Add other variables from .env.example
7. Create Web Service

**Frontend:**
1. New → Static Site
2. Build Command: `cd frontend && npm install && npm run build`
3. Publish Directory: `frontend/dist`
4. Environment Variables:
   - VITE_API_URL: Your backend URL
5. Create Static Site

**Workers:**
- Repeat for collector and retrainer services
- Select "Background Worker" type
- Set appropriate start commands

### Scaling Configuration

**Automatic Scaling (render.yaml):**
```yaml
scaling:
  minInstances: 1
  maxInstances: 3
  targetCPUPercent: 75
  targetMemoryPercent: 80
```

**Manual Scaling:**
- Go to service settings
- Adjust instance count
- Save changes

### Domain Configuration

1. **Custom Domain:**
   - Go to service settings
   - Add custom domain
   - Update DNS records (CNAME or A record)

2. **SSL Certificate:**
   - Automatically provisioned by Render
   - Renews automatically

---

## Automated Retraining Pipeline

### Overview

The automated retraining pipeline (`automated_retraining.py`) continuously monitors for new data and triggers model retraining based on:

1. **Time-based**: Every N hours (configurable)
2. **Data-based**: When minimum new samples threshold is reached
3. **Performance-based**: When model performance degrades

### How It Works

```
┌─────────────────┐
│  New Data       │
│  Arrives        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Data Collector │◄─── Runs hourly (configurable)
│  (scheduled_    │
│   collector.py) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  PostgreSQL DB  │
│  Stores data    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Retrainer      │◄─── Checks every hour
│  (automated_    │
│   retraining.py)│
└────────┬────────┘
         │
         ├─ Check new data count
         ├─ Check time since last training
         └─ Check performance metrics
         │
         ▼
    Trigger needed?
         │
    ┌────┴────┐
    │  YES    │  NO → Wait
    │         │
    ▼         │
┌─────────────────┐
│  Fetch Data     │
│  from Database  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Train Models   │
│  - Linear Reg   │
│  - Random Forest│
│  - Gradient Boost
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Evaluate       │
│  - RMSE         │
│  - R² Score     │
│  - MAE          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Save Models    │
│  - Version bump │
│  - Metrics log  │
│  - Metadata     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Reload     │
│  Models (auto)  │
└─────────────────┘
```

### Configuration

**Environment Variables:**

```env
# Retraining frequency
RETRAIN_INTERVAL_HOURS=24          # Check every 24 hours

# Minimum new samples required
MIN_NEW_SAMPLES=100                # At least 100 new samples

# Performance threshold
PERFORMANCE_THRESHOLD=0.1          # 10% RMSE increase triggers retrain

# Model path
MODEL_PATH=./models                # Where to save trained models
```

### Model Versioning

Each retraining creates:
- **New model files**: `{model_name}_model.pkl`
- **Metrics file**: `models/metrics.json`
- **Metadata file**: `models/metadata.json`

Example metadata.json:
```json
{
  "last_training_time": "2025-10-28T10:30:00",
  "last_data_timestamp": "2025-10-28T09:45:00",
  "training_samples": 15420,
  "model_versions": {
    "linear_regression": 5,
    "random_forest": 5,
    "gradient_boosting": 5
  }
}
```

### Manual Trigger

**Via API:**
```powershell
curl -X POST http://localhost:5000/api/admin/models/reload
```

**Via Docker:**
```powershell
docker-compose exec retrainer python automated_retraining.py
```

### Monitoring Retraining

**View logs:**
```powershell
# Docker
docker-compose logs -f retrainer

# Direct file
tail -f logs/retraining.log
```

**Check metrics:**
```powershell
curl http://localhost:5000/api/admin/models
```

---

## RESTful API Endpoints

### Base URL
- Local: `http://localhost:5000`
- Production: `https://your-app.onrender.com`

### Endpoint Categories

#### 1. Health & Status
```
GET /api/health
```
Returns API health status, database connection, and loaded models.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-28T10:30:00",
  "database": "connected",
  "models_loaded": 4,
  "version": "1.0.0"
}
```

---

#### 2. Predictions (ML)

**Make Prediction:**
```
POST /api/predict
Content-Type: application/json

{
  "pm25": 45.2,
  "pm10": 68.5,
  "no2": 32.1,
  "so2": 8.5,
  "co": 1.2,
  "o3": 45.0,
  "temperature": 28.5,
  "humidity": 65.0,
  "wind_speed": 5.2,
  "latitude": 28.6139,
  "longitude": 77.2090
}
```

**Response:**
```json
{
  "status": "success",
  "predictions": {
    "linear_regression": 125.5,
    "random_forest": 128.3,
    "gradient_boosting": 126.8,
    "ensemble": 126.9
  },
  "confidence_interval": {
    "lower": 118.2,
    "upper": 135.6
  },
  "aqi_category": "Unhealthy for Sensitive Groups",
  "health_implications": "...",
  "recommendations": ["..."]
}
```

**Get Prediction History:**
```
GET /api/predictions?limit=50
GET /api/predictions/{station_id}
```

---

#### 3. Data Retrieval

**Latest Data:**
```
GET /api/data/latest?limit=20
```

**Station Data:**
```
GET /api/data/station/{station_id}?hours=24
```

**City Data:**
```
GET /api/data/city/{city}?days=7
```

**Time Series:**
```
GET /api/data/timeseries?station_id={id}&start_date={date}&end_date={date}
```

---

#### 4. Stations & Cities

**List Stations:**
```
GET /api/stations
```

**Station Details:**
```
GET /api/stations/{station_id}
```

**List Cities:**
```
GET /api/cities
```

---

#### 5. Analytics

**Summary Statistics:**
```
GET /api/analytics/summary
```

**City Analytics:**
```
GET /api/analytics/city/{city}?days=30
```

**Trends Analysis:**
```
GET /api/analytics/trends?pollutant=pm25&period=7d
```

---

#### 6. Administration

**Model Information:**
```
GET /api/admin/models
```

**Reload Models:**
```
POST /api/admin/models/reload
```

**System Statistics:**
```
GET /api/admin/stats
```

**Data Cleanup:**
```
POST /api/admin/data/cleanup
Content-Type: application/json

{
  "retention_days": 90
}
```

**Refresh Materialized Views:**
```
POST /api/admin/refresh-views
```

---

#### 7. Monitoring

**Metrics Endpoint (Prometheus Compatible):**
```
GET /api/monitoring/metrics
```

**Response:**
```json
{
  "status": "success",
  "timestamp": "2025-10-28T10:30:00",
  "metrics": {
    "total_readings": 150420,
    "readings_last_hour": 245,
    "readings_last_day": 5880,
    "avg_pm25_last_hour": 42.5,
    "max_aqi_last_hour": 185,
    "models_loaded": 4
  }
}
```

---

## Environment Configuration

### Required Variables

**Database:**
```env
DATABASE_URL=postgresql://user:password@host:5432/database
POSTGRES_DB=air_quality_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password
```

**Flask:**
```env
FLASK_ENV=production
FLASK_APP=backend/api.py
SECRET_KEY=your-secret-key-here
CORS_ORIGINS=https://your-frontend.com
PORT=5000
```

**ML Models:**
```env
MODEL_PATH=./models
AUTO_RETRAIN=true
RETRAIN_INTERVAL_HOURS=24
MIN_NEW_SAMPLES=100
PERFORMANCE_THRESHOLD=0.1
```

**Data Collection:**
```env
COLLECTION_INTERVAL_MINUTES=60
CPCB_API_KEY=your_api_key_here
OPENWEATHER_API_KEY=your_api_key_here
```

### Security Best Practices

1. **Never commit .env files** - Use .env.example as template
2. **Use strong passwords** - Minimum 16 characters
3. **Rotate secrets regularly** - Every 90 days
4. **Use environment-specific configs** - Different values for dev/prod
5. **Enable HTTPS only** - In production
6. **Implement rate limiting** - Prevent API abuse

---

## Monitoring & Administration

### Health Checks

**Docker:**
```powershell
docker-compose ps
docker inspect --format='{{json .State.Health}}' air_quality_backend
```

**API:**
```powershell
curl http://localhost:5000/api/health
```

### Log Management

**View logs:**
```powershell
# Docker logs
docker-compose logs -f

# Application logs
cat logs/retraining.log
cat logs/app.log
```

**Log rotation (Linux):**
```bash
# /etc/logrotate.d/air-quality
/app/logs/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

### Database Maintenance

**Backup:**
```powershell
# Docker
docker-compose exec postgres pg_dump -U postgres air_quality_db > backup.sql

# Render
pg_dump $DATABASE_URL > backup.sql
```

**Restore:**
```powershell
docker-compose exec -T postgres psql -U postgres air_quality_db < backup.sql
```

**Vacuum:**
```powershell
docker-compose exec postgres psql -U postgres -d air_quality_db -c "VACUUM ANALYZE;"
```

### Performance Monitoring

**Database queries:**
```sql
-- Slow queries
SELECT * FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Connection count
SELECT count(*) FROM pg_stat_activity;

-- Table sizes
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

**Resource usage:**
```powershell
docker stats --no-stream
```

---

## Troubleshooting

### Common Issues

**1. Container won't start:**
```powershell
# Check logs
docker-compose logs backend

# Rebuild
docker-compose up -d --build --force-recreate
```

**2. Database connection failed:**
```powershell
# Verify database is running
docker-compose ps postgres

# Check connection
docker-compose exec backend python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
```

**3. Models not loading:**
```powershell
# Check models directory
docker-compose exec backend ls -la models/

# Reload models
curl -X POST http://localhost:5000/api/admin/models/reload
```

**4. Frontend can't reach backend:**
- Check CORS_ORIGINS in .env
- Verify nginx.conf proxy settings
- Check Docker network: `docker network inspect api-integration_app_network`

### Getting Help

- GitHub Issues: https://github.com/Samson-lgs/api-integration/issues
- Documentation: See README.md files
- Logs: Check `logs/` directory

---

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database initialized with schema
- [ ] ML models trained and saved
- [ ] Docker images built successfully
- [ ] Health checks passing
- [ ] SSL certificate configured
- [ ] Domain DNS records updated
- [ ] Monitoring alerts set up
- [ ] Backup strategy implemented
- [ ] Load testing completed
- [ ] Documentation updated
- [ ] Team trained on operations

---

## Next Steps

1. **Production Optimization:**
   - Enable Redis caching
   - Set up CDN for frontend
   - Implement rate limiting
   - Add API authentication

2. **Monitoring Enhancement:**
   - Integrate with Prometheus
   - Set up Grafana dashboards
   - Configure alerting (PagerDuty, Slack)
   - Implement APM (New Relic, DataDog)

3. **Feature Additions:**
   - Mobile app
   - Email notifications
   - API webhooks
   - Data export features

---

**Last Updated:** October 28, 2025  
**Version:** 1.0.0  
**Maintained by:** Air Quality Monitoring Team
