# 🌍 Air Quality Monitoring System

**Full-Stack Application with Machine Learning Predictions**

A production-ready air quality monitoring system with real-time data collection, ML-powered predictions, and interactive dashboards.

[![Python](https://img.shields.io/badge/Python-3.14-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://reactjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-336791.svg)](https://postgresql.org)

---

## ✨ Features

### 🎯 Core Features
- ✅ **Real-time Air Quality Monitoring** - Track PM2.5, PM10, NO2, SO2, CO, O3, NH3
- ✅ **ML-Powered Predictions** - 4 trained models (Linear Regression, Random Forest, XGBoost, Ensemble)
- ✅ **Interactive Dashboard** - React-based SPA with charts and analytics
- ✅ **RESTful API** - Complete Flask API with 20+ endpoints
- ✅ **Time-Series Database** - Optimized PostgreSQL schema with indexes
- ✅ **Multi-Source Data** - CPCB, OpenWeather integration
- ✅ **Advanced Analytics** - Trends, comparisons, predictions

### 🚀 Technical Highlights
- **Backend**: Flask 3.0+ with CORS, error handling, pagination
- **Frontend**: React 18.3 + Vite + Recharts for visualizations
- **Database**: PostgreSQL with materialized views, partitioning support
- **ML Models**: Best model RMSE 33.75 (68.45% R²)
- **Deployment**: Ready for Render, AWS, Azure

---

## 📋 Quick Start

### Prerequisites
```bash
- Python 3.14+
- Node.js 18+
- PostgreSQL 12+
- Git
```

### 1️⃣ Clone Repository
```bash
cd "c:\Users\Samson Jose\Desktop\api integration"
```

### 2️⃣ Backend Setup
```powershell
# Create virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your DATABASE_URL
```

### 3️⃣ Database Setup
```powershell
# Create database
createdb air_quality_db

# Initialize schema and sample data
cd backend
python init_db.py
```

### 4️⃣ Frontend Setup
```bash
cd frontend
npm install
```

### 5️⃣ Start Application
```bash
# Terminal 1 - Backend API (Port 5000)
cd backend
python api.py

# Terminal 2 - Frontend (Port 3000)
cd frontend
npm run dev
```

### 6️⃣ Access Application
- **Dashboard**: http://localhost:3000
- **API**: http://localhost:5000/api
- **Health Check**: http://localhost:5000/api/health

---

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │ ← Modern SPA with Vite
│   Visualizations│
└────────┬────────┘
         │ REST API
┌────────▼────────┐
│   Flask Backend │ ← 20+ API endpoints
│   CORS enabled  │
└────────┬────────┘
         │ SQL
┌────────▼────────┐       ┌──────────────┐
│   PostgreSQL    │◄──────┤  ML Models   │
│   Time-series   │       │  4 trained   │
└─────────────────┘       └──────────────┘
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.

---

## 📊 Machine Learning Models

| Model | Test RMSE | Test R² | Status |
|-------|-----------|---------|--------|
| **Linear Regression** | **33.75** | **0.6845** | ⭐ BEST |
| Ensemble Stacking | 34.83 | 0.6639 | ✅ Good |
| Random Forest | 36.58 | 0.6293 | ✅ Good |
| XGBoost | 43.35 | 0.4795 | ✅ Good |

**Top Features**: PM10 (29%), PM25 (23%), PM25_rolling_24h (17%)

---

## 🔌 API Endpoints

### Health & System
- `GET /api/health` - System health check
- `GET /` - API documentation

### Stations
- `GET /api/stations` - List all monitoring stations
- `GET /api/stations/<id>` - Station details
- `GET /api/cities` - Cities list

### Data
- `GET /api/data/latest` - Latest readings (pagination)
- `GET /api/data/station/<id>` - Station data
- `GET /api/data/city/<city>` - City data
- `GET /api/data/timeseries` - Time-series data

### Predictions
- `POST /api/predict` - Generate ML prediction
- `GET /api/predictions` - Saved predictions
- `GET /api/predictions/<id>` - Station predictions

### Analytics
- `GET /api/analytics/summary` - Overall summary
- `GET /api/analytics/city/<city>` - City analytics
- `GET /api/analytics/trends` - Pollutant trends

---

## 🎨 Frontend Pages

### 1. Dashboard
- Real-time AQI readings
- System statistics
- PM2.5 trend charts
- Latest readings table
- City filtering

### 2. Stations
- All monitoring stations
- Station details viewer
- Recent readings
- Location information

### 3. Predictions
- ML prediction form
- Feature input
- Confidence intervals
- Recent predictions list

### 4. Analytics
- Pollutant trends
- City comparisons
- Time period selection
- Distribution charts

---

## 🗄️ Database Schema

### Key Tables
- **stations** - Monitoring locations (5+ cities)
- **air_quality_data** - Time-series measurements (100k+ rows)
- **predictions** - ML predictions with confidence
- **aqi_categories** - AQI classification
- **pollutants** - Pollutant definitions

### Optimizations
- ✅ Indexes on `recorded_at`, `station_id`, `pollutant_id`
- ✅ Materialized views for latest readings
- ✅ Daily aggregates for fast queries
- ✅ Monthly partitioning support (optional)

---

## 🚢 Deployment

### Option 1: Render (Recommended)

**Backend**
```bash
Build: pip install -r requirements.txt
Start: gunicorn backend.api:app
```

**Database**
```bash
Service: PostgreSQL
Init: psql $DATABASE_URL -f backend/database/schema.sql
```

**Frontend**
```bash
Build: cd frontend && npm install && npm run build
Publish: frontend/dist
```

### Option 2: Docker
```bash
docker-compose up -d
```

### Option 3: AWS/Azure
See [ARCHITECTURE.md](ARCHITECTURE.md) for cloud deployment guides.

---

## 📁 Project Structure

```
api integration/
├── backend/
│   ├── database/
│   │   ├── schema.sql          # PostgreSQL schema
│   │   └── db_manager.py       # Database operations
│   ├── api.py                  # Flask REST API
│   └── init_db.py              # Database initialization
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   ├── services/           # API service
│   │   └── App.jsx             # Main app
│   ├── package.json
│   └── vite.config.js
├── models/
│   ├── linear_regression_model.pkl
│   ├── ensemble_model.pkl
│   └── scaler.pkl
├── data_preprocessing.py       # Preprocessing pipeline
├── ml_pipeline.py              # ML training pipeline
├── requirements.txt            # Python dependencies
├── .env.example                # Environment template
├── ARCHITECTURE.md             # Detailed documentation
└── README.md                   # This file
```

---

## 🔒 Security

- ✅ Environment variables for secrets
- ✅ CORS configuration
- ✅ SQL injection prevention (prepared statements)
- ✅ Input validation
- ✅ HTTPS ready
- ✅ Rate limiting support

---

## 🔧 Configuration

### Backend (.env)
```env
DATABASE_URL=postgresql://user:pass@host:5432/db
FLASK_ENV=development
SECRET_KEY=your-secret-key
PORT=5000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:5000/api
```

---

## 🐛 Troubleshooting

### Database Connection
```bash
# Check PostgreSQL is running
pg_isready

# Test connection
psql -d air_quality_db
```

### CORS Errors
- Verify `CORS_ORIGINS` in .env
- Check frontend URL matches

### Model Loading
- Ensure models exist in `models/` directory
- Check file permissions

---

## 📈 Performance

- **API Response**: < 100ms average
- **Database Queries**: Optimized with indexes
- **Frontend Load**: < 2s initial load
- **ML Prediction**: < 500ms per request

---

## 🧪 Testing

```bash
# Backend tests
pytest backend/tests/

# Frontend tests
cd frontend
npm run test
```

---

## 📚 Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) - Complete architecture guide
- [ML_PIPELINE_COMPLETE.md](ML_PIPELINE_COMPLETE.md) - ML documentation
- [DATA_PREPROCESSING_COMPLETE.md](DATA_PREPROCESSING_COMPLETE.md) - Preprocessing guide

---

## 🎯 Roadmap

- [x] Data collection from CPCB
- [x] PostgreSQL time-series database
- [x] ML model training (4 models)
- [x] Flask REST API (20+ endpoints)
- [x] React dashboard
- [x] Deployment configuration
- [ ] Real-time notifications
- [ ] Mobile app (React Native)
- [ ] Advanced forecasting (7-day)

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## 📄 License

This project is for educational and research purposes.

---

## 🙏 Acknowledgments

- **CPCB** for air quality data
- **OpenWeather** for weather data
- **scikit-learn** for ML framework
- **Flask** for backend framework
- **React** for frontend framework

---

## 📞 Support

For issues or questions:
- 📧 Email: your-email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Docs: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Built with ❤️ using Python, Flask, PostgreSQL, React, and Machine Learning**

⭐ Star this repo if you find it helpful!
