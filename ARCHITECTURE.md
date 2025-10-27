# ============================================================================
# AIR QUALITY MONITORING SYSTEM - FULL STACK ARCHITECTURE
# Complete deployment guide for Flask + PostgreSQL + React
# ============================================================================

## 📋 ARCHITECTURE OVERVIEW

### Technology Stack
- **Backend**: Python 3.14, Flask 3.0+ (RESTful API)
- **Database**: PostgreSQL 12+ (Time-series optimized)
- **Frontend**: React 18.3, Vite 5.3 (Modern SPA)
- **ML Models**: scikit-learn 1.7.2, XGBoost 3.1.1
- **Deployment**: Render (recommended) or AWS/Azure

### System Architecture
```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│   (Vite + SPA)  │
└────────┬────────┘
         │ HTTP/REST
         │
┌────────▼────────┐
│   Flask API     │ (Port 5000)
│   (RESTful)     │
└────────┬────────┘
         │ SQL
         │
┌────────▼────────┐       ┌──────────────┐
│   PostgreSQL    │◄──────┤  ML Models   │
│   (Database)    │       │  (.pkl files)│
└─────────────────┘       └──────────────┘
```

---

## 🚀 QUICK START

### Prerequisites
1. Python 3.14+ installed
2. Node.js 18+ and npm installed
3. PostgreSQL 12+ installed and running
4. Git installed

### Step 1: Clone and Setup

```bash
cd "c:\Users\Samson Jose\Desktop\api integration"
```

### Step 2: Backend Setup

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat

# Install Python dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env
# Edit .env and add your DATABASE_URL
```

### Step 3: Database Setup

```powershell
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE air_quality_db;

# Exit psql
\q

# Initialize schema
cd backend\database
psql -U postgres -d air_quality_db -f schema.sql

# Or use Python:
python db_manager.py
```

### Step 4: Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start development server
npm run dev
```

### Step 5: Start Backend API

```bash
# From project root
cd backend
python api.py
```

### Step 6: Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/

---

## 📁 PROJECT STRUCTURE

```
api integration/
├── backend/
│   ├── database/
│   │   ├── schema.sql          # PostgreSQL schema
│   │   └── db_manager.py       # Database operations
│   ├── api.py                  # Flask REST API
│   └── __init__.py
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── StationsPage.jsx
│   │   │   ├── PredictionsPage.jsx
│   │   │   └── AnalyticsPage.jsx
│   │   ├── services/
│   │   │   └── api.js          # API service layer
│   │   ├── App.jsx
│   │   ├── App.css
│   │   ├── index.css
│   │   └── main.jsx
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── models/
│   ├── linear_regression_model.pkl
│   ├── ensemble_model.pkl
│   ├── scaler.pkl
│   └── metrics.json
├── data_preprocessing.py
├── ml_pipeline.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🗄️ DATABASE SCHEMA

### Key Tables

**stations** - Monitoring station information
- `station_id` (PK)
- `station_name`, `city`, `state`
- `latitude`, `longitude`
- `data_source`, `is_active`

**air_quality_data** - Time-series measurements
- `id` (PK), `station_id` (FK)
- `recorded_at` (indexed)
- `pollutant_id`, `pollutant_avg`
- `aqi`, `aqi_category_id`
- `temperature`, `humidity`, `wind_speed`

**predictions** - ML predictions
- `id` (PK), `station_id` (FK)
- `predicted_for`, `predicted_aqi`
- `model_name`, `confidence_lower/upper`

### Optimizations
- **Indexes**: On `recorded_at`, `station_id`, `pollutant_id`
- **Materialized Views**: Latest readings, daily stats
- **Partitioning**: Monthly partitions for large datasets (optional)

---

## 🔌 API ENDPOINTS

### Health & System
- `GET /api/health` - Health check
- `GET /` - API documentation

### Stations
- `GET /api/stations` - Get all stations
- `GET /api/stations/<id>` - Get station details
- `GET /api/cities` - Get cities list

### Data
- `GET /api/data/latest` - Latest readings
- `GET /api/data/station/<id>` - Station data
- `GET /api/data/city/<city>` - City data
- `GET /api/data/timeseries` - Time-series data

### Predictions
- `POST /api/predict` - Generate prediction
- `GET /api/predictions` - Get predictions
- `GET /api/predictions/<id>` - Station predictions

### Analytics
- `GET /api/analytics/summary` - System summary
- `GET /api/analytics/city/<city>` - City analytics
- `GET /api/analytics/trends` - Pollutant trends

---

## 🎨 FRONTEND FEATURES

### Dashboard
- Real-time AQI readings
- System statistics cards
- PM2.5 trends chart
- City filtering
- Latest readings table

### Stations Page
- All monitoring stations
- Station details viewer
- Recent readings per station
- Location information

### Predictions Page
- ML-powered AQI predictions
- Feature input form
- Confidence intervals
- Recent predictions list

### Analytics Page
- Pollutant trend charts
- City comparisons
- Time period selection
- Min/max ranges
- Distribution charts

---

## 🤖 MACHINE LEARNING INTEGRATION

### Available Models
1. **Linear Regression** (BEST - RMSE 33.75)
2. **Random Forest** (RMSE 36.58)
3. **XGBoost** (RMSE 43.35)
4. **Ensemble Stacking** (RMSE 34.83)

### Prediction Workflow
1. Frontend sends features to `/api/predict`
2. Backend loads model from `models/` directory
3. Features scaled using saved scaler
4. Model generates prediction + confidence interval
5. Prediction saved to database
6. Result returned to frontend

### Model Files
- `linear_regression_model.pkl` - Best performing model
- `scaler.pkl` - Feature scaler (StandardScaler)
- `metrics.json` - Model performance metrics

---

## 🚢 DEPLOYMENT

### Option 1: Render (Recommended)

#### Backend Deployment
1. Create new Web Service on Render
2. Connect GitHub repository
3. Build command: `pip install -r requirements.txt`
4. Start command: `gunicorn backend.api:app`
5. Add environment variables:
   - `DATABASE_URL` (from Render PostgreSQL)
   - `FLASK_ENV=production`
   - `PORT=10000`

#### Database Deployment
1. Create PostgreSQL database on Render
2. Copy DATABASE_URL to backend service
3. Run schema initialization:
   ```bash
   psql $DATABASE_URL -f backend/database/schema.sql
   ```

#### Frontend Deployment
1. Create new Static Site on Render
2. Build command: `cd frontend && npm install && npm run build`
3. Publish directory: `frontend/dist`
4. Add environment variable:
   - `VITE_API_URL=https://your-backend.onrender.com/api`

### Option 2: Docker (Local/Cloud)

```dockerfile
# Backend Dockerfile
FROM python:3.14-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "backend.api:app"]
```

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build
FROM nginx:alpine
COPY --from=0 /app/dist /usr/share/nginx/html
```

### Option 3: AWS/Azure

#### AWS Setup
1. EC2 for backend (t3.medium)
2. RDS PostgreSQL for database
3. S3 + CloudFront for frontend
4. Load balancer for scaling

#### Azure Setup
1. App Service for backend
2. Azure Database for PostgreSQL
3. Static Web Apps for frontend
4. Application Insights for monitoring

---

## 🔒 SECURITY BEST PRACTICES

### Backend Security
- Use environment variables for secrets
- Enable CORS only for trusted origins
- Implement rate limiting
- Validate all input data
- Use prepared statements (SQL injection prevention)

### Database Security
- Use strong passwords
- Enable SSL connections
- Regular backups
- Restrict network access
- Use read-only users for queries

### Frontend Security
- Sanitize user input
- Use HTTPS only
- Implement CSP headers
- Regular dependency updates

---

## 🔧 CONFIGURATION

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
FLASK_ENV=production
SECRET_KEY=random-secret-key
PORT=5000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
```

---

## 📊 MONITORING & MAINTENANCE

### Database Maintenance
```sql
-- Refresh materialized views (daily)
SELECT refresh_materialized_views();

-- Get database statistics
SELECT * FROM get_db_statistics();

-- Vacuum analyze (weekly)
VACUUM ANALYZE air_quality_data;
```

### Application Monitoring
- Check `/api/health` endpoint regularly
- Monitor database size and performance
- Track API response times
- Set up alerts for errors

### Model Retraining
- Retrain monthly with new data
- Compare performance metrics
- Update models in production
- Maintain model version history

---

## 🐛 TROUBLESHOOTING

### Database Connection Errors
```bash
# Check PostgreSQL is running
psql -U postgres -d air_quality_db

# Verify DATABASE_URL format
# postgresql://username:password@hostname:port/database
```

### CORS Errors
- Check `CORS_ORIGINS` in .env
- Verify frontend URL matches
- Check Flask-CORS configuration

### Model Loading Errors
- Verify models exist in `models/` directory
- Check file permissions
- Ensure scikit-learn version matches

### Frontend Build Errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📈 PERFORMANCE OPTIMIZATION

### Database Optimization
- Use indexes on frequently queried columns
- Enable query caching
- Implement connection pooling
- Use materialized views for complex queries

### API Optimization
- Implement response caching
- Use pagination for large datasets
- Enable gzip compression
- Optimize database queries

### Frontend Optimization
- Code splitting
- Lazy loading
- Image optimization
- CDN for static assets

---

## 📝 TESTING

### Backend Testing
```bash
# Run tests
pytest backend/tests/

# Test API endpoints
curl http://localhost:5000/api/health
```

### Frontend Testing
```bash
cd frontend
npm run test
npm run lint
```

---

## 🔄 CONTINUOUS DEPLOYMENT

### GitHub Actions (Example)
```yaml
name: Deploy
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Render
        run: curl ${{ secrets.RENDER_DEPLOY_HOOK }}
```

---

## 📞 SUPPORT

For issues or questions:
1. Check this documentation
2. Review error logs
3. Check GitHub Issues
4. Contact: your-email@example.com

---

## 📄 LICENSE

This project is for educational and research purposes.

---

**Built with ❤️ using Flask, PostgreSQL, and React**
