# RESTful API Endpoints - Quick Reference

Base URL: `http://localhost:5000` (local) or `https://your-app.onrender.com` (production)

## Table of Contents
- [Health & Status](#health--status)
- [Predictions (ML)](#predictions-ml)
- [Data Retrieval](#data-retrieval)
- [Stations & Cities](#stations--cities)
- [Analytics](#analytics)
- [Administration](#administration)
- [Monitoring](#monitoring)

---

## Health & Status

### Check API Health
```http
GET /api/health
```

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

## Predictions (ML)

### Make AQI Prediction
```http
POST /api/predict
Content-Type: application/json
```

**Request Body:**
```json
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
  "health_implications": "People with respiratory or heart disease, the elderly and children should limit prolonged outdoor exertion.",
  "recommendations": [
    "Limit outdoor activities",
    "Use air purifiers indoors",
    "Wear N95 masks when going outside"
  ]
}
```

### Get Prediction History
```http
GET /api/predictions?limit=50&offset=0
```

### Get Station Predictions
```http
GET /api/predictions/{station_id}
```

---

## Data Retrieval

### Get Latest Data
```http
GET /api/data/latest?limit=20
```

**Query Parameters:**
- `limit` (optional): Number of records (default: 20)

**Response:**
```json
{
  "status": "success",
  "count": 20,
  "data": [
    {
      "station_id": "STN001",
      "station_name": "Delhi Connaught Place",
      "city": "Delhi",
      "pm25": 45.2,
      "pm10": 68.5,
      "no2": 32.1,
      "aqi": 125,
      "aqi_category": "Unhealthy for Sensitive Groups",
      "timestamp": "2025-10-28T10:30:00"
    }
  ]
}
```

### Get Station Data
```http
GET /api/data/station/{station_id}?hours=24
```

**Query Parameters:**
- `hours` (optional): Hours of historical data (default: 24)

### Get City Data
```http
GET /api/data/city/{city}?days=7
```

**Query Parameters:**
- `days` (optional): Days of historical data (default: 7)

### Get Time Series Data
```http
GET /api/data/timeseries?station_id={id}&start_date={date}&end_date={date}
```

**Query Parameters:**
- `station_id` (required): Station identifier
- `start_date` (required): Start date (YYYY-MM-DD)
- `end_date` (required): End date (YYYY-MM-DD)

---

## Stations & Cities

### List All Stations
```http
GET /api/stations
```

**Response:**
```json
{
  "status": "success",
  "count": 50,
  "stations": [
    {
      "station_id": "STN001",
      "station_name": "Delhi Connaught Place",
      "city": "Delhi",
      "state": "Delhi",
      "latitude": 28.6139,
      "longitude": 77.2090,
      "active": true
    }
  ]
}
```

### Get Station Details
```http
GET /api/stations/{station_id}
```

### List All Cities
```http
GET /api/cities
```

**Response:**
```json
{
  "status": "success",
  "cities": [
    {
      "city": "Delhi",
      "state": "Delhi",
      "station_count": 15,
      "avg_aqi": 125.5
    }
  ]
}
```

---

## Analytics

### Get Summary Statistics
```http
GET /api/analytics/summary
```

**Response:**
```json
{
  "status": "success",
  "summary": {
    "total_stations": 50,
    "total_cities": 10,
    "total_readings": 150000,
    "avg_aqi_today": 105.2,
    "avg_pm25_today": 38.5,
    "worst_city": "Delhi",
    "best_city": "Shimla"
  }
}
```

### Get City Analytics
```http
GET /api/analytics/city/{city}?days=30
```

**Query Parameters:**
- `days` (optional): Days to analyze (default: 30)

**Response:**
```json
{
  "status": "success",
  "city": "Delhi",
  "period_days": 30,
  "analytics": {
    "avg_aqi": 135.5,
    "max_aqi": 285,
    "min_aqi": 45,
    "avg_pm25": 55.2,
    "good_days": 5,
    "unhealthy_days": 20,
    "hazardous_days": 5
  }
}
```

### Get Trends Analysis
```http
GET /api/analytics/trends?pollutant=pm25&period=7d
```

**Query Parameters:**
- `pollutant` (required): Pollutant name (pm25, pm10, no2, etc.)
- `period` (optional): Time period (7d, 30d, 90d, default: 7d)

---

## Administration

### Get Model Information
```http
GET /api/admin/models
```

**Response:**
```json
{
  "status": "success",
  "models_loaded": ["linear_regression", "random_forest", "gradient_boosting", "ensemble"],
  "scaler_loaded": true,
  "total_models": 4,
  "metrics": {
    "linear_regression": {
      "test_rmse": 33.75,
      "test_r2": 0.6845,
      "version": 5,
      "timestamp": "2025-10-28T08:00:00"
    }
  }
}
```

### Reload ML Models
```http
POST /api/admin/models/reload
```

**Response:**
```json
{
  "status": "success",
  "message": "Models reloaded successfully",
  "models_loaded": ["linear_regression", "random_forest", "gradient_boosting", "ensemble"]
}
```

### Get System Statistics
```http
GET /api/admin/stats
```

**Response:**
```json
{
  "status": "success",
  "database": {
    "total_stations": 50,
    "total_readings": 150420,
    "total_predictions": 8520,
    "total_cities": 10,
    "earliest_reading": "2025-10-01T00:00:00",
    "latest_reading": "2025-10-28T10:30:00"
  },
  "recent_activity": [
    {"date": "2025-10-28", "count": 1200},
    {"date": "2025-10-27", "count": 1180}
  ],
  "models": {
    "loaded": 4,
    "available": ["linear_regression", "random_forest", "gradient_boosting", "ensemble"]
  }
}
```

### Clean Up Old Data
```http
POST /api/admin/data/cleanup
Content-Type: application/json
```

**Request Body:**
```json
{
  "retention_days": 90
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Deleted 5420 old records",
  "retention_days": 90
}
```

### Refresh Materialized Views
```http
POST /api/admin/refresh-views
```

**Response:**
```json
{
  "status": "success",
  "message": "Materialized views refreshed successfully",
  "views_refreshed": ["latest_station_readings", "daily_air_quality_stats"]
}
```

---

## Monitoring

### Get Monitoring Metrics
```http
GET /api/monitoring/metrics
```

**Response (Prometheus Compatible):**
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

## Error Responses

All endpoints return consistent error responses:

**400 Bad Request:**
```json
{
  "status": "error",
  "message": "Invalid input parameters",
  "error": "pm25 is required"
}
```

**404 Not Found:**
```json
{
  "status": "error",
  "message": "Resource not found",
  "error": "Station STN999 not found"
}
```

**500 Internal Server Error:**
```json
{
  "status": "error",
  "message": "Internal server error",
  "error": "Database connection failed"
}
```

---

## Authentication (Optional)

If authentication is enabled, include the token in headers:

```http
Authorization: Bearer {your_jwt_token}
```

---

## Rate Limiting

Default rate limits:
- **Public endpoints**: 60 requests/minute
- **Admin endpoints**: 20 requests/minute
- **Prediction endpoints**: 30 requests/minute

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 55
X-RateLimit-Reset: 1698480000
```

---

## Testing the API

### Using cURL

**Health Check:**
```bash
curl http://localhost:5000/api/health
```

**Make Prediction:**
```bash
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{
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
  }'
```

**Get Latest Data:**
```bash
curl http://localhost:5000/api/data/latest?limit=10
```

### Using PowerShell

**Health Check:**
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/health" -Method Get
```

**Make Prediction:**
```powershell
$body = @{
    pm25 = 45.2
    pm10 = 68.5
    no2 = 32.1
    so2 = 8.5
    co = 1.2
    o3 = 45.0
    temperature = 28.5
    humidity = 65.0
    wind_speed = 5.2
    latitude = 28.6139
    longitude = 77.2090
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/predict" `
  -Method Post `
  -Body $body `
  -ContentType "application/json"
```

---

## API Versioning

Current version: **v1**

Future versions will be accessible at: `/api/v2/...`

---

## Support

For issues or questions:
- GitHub: https://github.com/Samson-lgs/api-integration/issues
- Documentation: See DEPLOYMENT.md and README.md

---

**Last Updated:** October 28, 2025  
**API Version:** 1.0.0
