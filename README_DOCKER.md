# Docker Deployment - Quick Start Guide

Complete containerization for the Air Quality Monitoring System with automated retraining and cloud deployment support.

## 🚀 Quick Start (5 Minutes)

### Windows (PowerShell)
```powershell
# 1. Clone the repository
git clone https://github.com/Samson-lgs/api-integration.git
cd api-integration

# 2. Run quick start script
.\docker-start.ps1
```

### Linux/Mac (Bash)
```bash
# 1. Clone the repository
git clone https://github.com/Samson-lgs/api-integration.git
cd api-integration

# 2. Make script executable and run
chmod +x docker-start.sh
./docker-start.sh
```

### Manual Setup
```bash
# 1. Create environment file
cp .env.example .env
# Edit .env with your settings

# 2. Build and start
docker-compose up -d --build

# 3. Verify
docker-compose ps
```

## 📦 What's Included

### 5 Docker Services

1. **PostgreSQL Database** (Port 5432)
   - Time-series optimized schema
   - Automatic initialization
   - Persistent storage

2. **Flask Backend API** (Port 5000)
   - RESTful endpoints
   - ML model integration
   - Auto-scaling ready

3. **React Frontend** (Port 80)
   - Nginx web server
   - Optimized build
   - API proxy configured

4. **Data Collector** (Background Worker)
   - Hourly data collection
   - Multi-source integration
   - Error handling & retry

5. **Model Retrainer** (Background Worker)
   - Automated retraining
   - Performance monitoring
   - Model versioning

## 🔧 Configuration

### Environment Variables (.env)

**Required:**
```env
POSTGRES_PASSWORD=your_secure_password
SECRET_KEY=your_secret_key_change_in_production
```

**Optional (with defaults):**
```env
POSTGRES_DB=air_quality_db
POSTGRES_USER=postgres
FLASK_ENV=production
PORT=5000
COLLECTION_INTERVAL_MINUTES=60
RETRAIN_INTERVAL_HOURS=24
MIN_NEW_SAMPLES=100
```

See `.env.example` for complete configuration options.

## 🎯 Access Points

After starting with `docker-compose up -d`:

- **Frontend**: http://localhost
- **Backend API**: http://localhost:5000
- **API Health**: http://localhost:5000/api/health
- **API Docs**: http://localhost:5000/api (interactive)

## 📊 Useful Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart a service
docker-compose restart backend

# View status
docker-compose ps
```

### Logs & Debugging
```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f collector
docker-compose logs -f retrainer

# View last 100 lines
docker-compose logs --tail=100 backend
```

### Database Operations
```bash
# Access PostgreSQL shell
docker-compose exec postgres psql -U postgres -d air_quality_db

# Run database backup
docker-compose exec postgres pg_dump -U postgres air_quality_db > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres air_quality_db < backup.sql

# Check database size
docker-compose exec postgres psql -U postgres -d air_quality_db -c "\l+"
```

### Container Management
```bash
# Access backend shell
docker-compose exec backend bash

# Run Python script in backend
docker-compose exec backend python backend/init_db.py

# View resource usage
docker stats

# Clean up unused resources
docker system prune -a
```

## 🔄 Automated Retraining

The retrainer service automatically:

1. **Monitors** new data arrivals every hour
2. **Evaluates** if retraining is needed:
   - Minimum 100 new samples
   - 24 hours since last training
   - Performance degradation detected
3. **Trains** multiple models (Linear, RF, GB)
4. **Evaluates** model performance (RMSE, R², MAE)
5. **Saves** best models with versioning
6. **Updates** API with new models

### Manual Retraining Trigger
```bash
# Trigger immediate retraining
docker-compose exec retrainer python automated_retraining.py

# Check retraining logs
docker-compose logs -f retrainer

# View model metrics
curl http://localhost:5000/api/admin/models
```

## 🌐 Cloud Deployment

### Deploy to Render (Recommended)

1. **Push to GitHub:**
```bash
git add .
git commit -m "feat: Add Docker deployment"
git push origin main
```

2. **Connect to Render:**
   - Go to https://dashboard.render.com
   - New → Blueprint
   - Connect GitHub repo
   - Render detects `render.yaml` automatically

3. **Deploy:**
   - Review configuration
   - Click "Apply"
   - Wait 10-15 minutes for deployment

See `DEPLOYMENT.md` for detailed cloud deployment instructions.

### Deploy to Heroku

```bash
# Install Heroku CLI
# https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Add PostgreSQL
heroku addons:create heroku-postgresql:standard-0

# Deploy
git push heroku main

# Scale workers
heroku ps:scale web=1 worker=1
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Docker Network                       │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌───────────┐    ┌───────────┐    ┌──────────────┐   │
│  │  Frontend │    │  Backend  │    │  PostgreSQL  │   │
│  │  (Nginx)  │───▶│  (Flask)  │───▶│   Database   │   │
│  │  Port 80  │    │ Port 5000 │    │  Port 5432   │   │
│  └───────────┘    └───────────┘    └──────────────┘   │
│                          │                   ▲          │
│                          │                   │          │
│                    ┌─────┴─────┐       ┌────┴────┐    │
│                    │           │       │         │     │
│              ┌─────▼────┐ ┌───▼────┐  │         │     │
│              │ Collector│ │Retrainer│  │         │     │
│              │ (Worker) │ │(Worker) │  │         │     │
│              └──────────┘ └────────┘  └─────────┘     │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## 🛡️ Security Best Practices

1. **Environment Variables:**
   - Never commit `.env` to version control
   - Use strong passwords (16+ characters)
   - Rotate secrets every 90 days

2. **Database:**
   - Use non-default passwords
   - Enable SSL in production
   - Regular backups

3. **API:**
   - CORS properly configured
   - Rate limiting enabled
   - HTTPS only in production

4. **Docker:**
   - Non-root user in containers
   - Multi-stage builds for smaller images
   - Regular security updates

## 📈 Monitoring & Health Checks

### Built-in Health Checks
- Backend: `/api/health` (30s interval)
- Frontend: `/` (30s interval)
- Database: `pg_isready` (10s interval)

### View Health Status
```bash
# Check all services
docker-compose ps

# Detailed health status
docker inspect --format='{{json .State.Health}}' air_quality_backend | python -m json.tool
```

### Metrics Endpoint
```bash
curl http://localhost:5000/api/monitoring/metrics
```

## 🐛 Troubleshooting

### Services Not Starting

```bash
# Check logs for errors
docker-compose logs

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Database Connection Issues

```bash
# Verify database is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Test connection
docker-compose exec backend python -c "import psycopg2; psycopg2.connect('postgresql://postgres:password@postgres:5432/air_quality_db')"
```

### Frontend Can't Reach Backend

```bash
# Check nginx configuration
docker-compose exec frontend cat /etc/nginx/conf.d/default.conf

# Verify CORS settings in .env
cat .env | grep CORS_ORIGINS

# Check network
docker network inspect api-integration_app_network
```

### Models Not Loading

```bash
# Check models directory
docker-compose exec backend ls -la models/

# Verify model files
docker-compose exec backend python -c "import pickle; pickle.load(open('models/linear_regression_model.pkl', 'rb'))"

# Reload models via API
curl -X POST http://localhost:5000/api/admin/models/reload
```

## 📚 Documentation

- **Deployment Guide**: `DEPLOYMENT.md` - Complete deployment instructions
- **API Documentation**: `API_DOCUMENTATION.md` - All endpoints and examples
- **Architecture**: `ARCHITECTURE.md` - System design and architecture
- **Full-Stack Guide**: `README_FULLSTACK.md` - Frontend + Backend details

## 🔗 Related Files

```
.
├── Dockerfile.backend          # Backend container definition
├── Dockerfile.frontend         # Frontend container definition
├── Dockerfile.postgres         # Database container definition
├── docker-compose.yml          # Service orchestration
├── nginx.conf                  # Nginx configuration
├── render.yaml                 # Render deployment config
├── .dockerignore              # Files to exclude from build
├── .env.example               # Environment template
├── docker-start.sh            # Linux/Mac quick start
└── docker-start.ps1           # Windows quick start
```

## 📝 Notes

- **First Run**: Initial setup takes 5-10 minutes (database initialization, model loading)
- **Disk Space**: Requires ~2GB for Docker images and data
- **Memory**: Minimum 4GB RAM recommended
- **Ports**: Ensure ports 80, 5000, 5432 are available

## 🆘 Getting Help

1. **Check Documentation**: See `DEPLOYMENT.md` for detailed instructions
2. **View Logs**: `docker-compose logs -f`
3. **GitHub Issues**: https://github.com/Samson-lgs/api-integration/issues
4. **Health Check**: http://localhost:5000/api/health

## 🎉 What's Next?

After successful deployment:

1. ✅ Access frontend at http://localhost
2. ✅ Test API at http://localhost:5000/api/health
3. ✅ View monitoring at http://localhost:5000/api/monitoring/metrics
4. ✅ Check model status at http://localhost:5000/api/admin/models
5. ✅ Deploy to cloud (see `DEPLOYMENT.md`)

---

**Version**: 1.0.0  
**Last Updated**: October 28, 2025  
**Docker Compose Version**: 3.8  
**Supported Platforms**: Windows, Linux, macOS
