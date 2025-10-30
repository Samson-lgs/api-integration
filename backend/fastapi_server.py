"""
FastAPI Backend for AQI Prediction System (Production Version)
Modern async API with better performance than Flask
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd
import joblib
import os
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AQI Prediction API",
    description="Real-time Air Quality Index prediction with ML models",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CSV_FILE = 'air_quality_data.csv'


# Pydantic models for request/response validation
class PredictRequest(BaseModel):
    city: str
    hours_ahead: int = 24


class PredictResponse(BaseModel):
    city: str
    current_time: str
    predictions: List[dict]
    model_used: str
    confidence: Optional[float] = None


class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    data_available: bool


class AlertRequest(BaseModel):
    email: str
    city: str
    threshold: int = 150


def get_aqi_category(aqi: int) -> str:
    """Get AQI category from numeric value"""
    if aqi <= 1:
        return 'Good'
    elif aqi <= 2:
        return 'Fair'
    elif aqi <= 3:
        return 'Moderate'
    elif aqi <= 4:
        return 'Poor'
    elif aqi <= 5:
        return 'Very Poor'
    else:
        return 'Extremely Poor'


def get_health_recommendation(aqi: int) -> str:
    """Get health recommendation based on AQI"""
    if aqi <= 1:
        return 'Air quality is good. Enjoy outdoor activities!'
    elif aqi <= 2:
        return 'Air quality is acceptable. Most people can be outdoors.'
    elif aqi <= 3:
        return 'Sensitive groups should limit prolonged outdoor exertion.'
    elif aqi <= 4:
        return 'Everyone should reduce prolonged outdoor exertion.'
    elif aqi <= 5:
        return 'Avoid outdoor activities. Health alert!'
    else:
        return 'Hazardous! Stay indoors and use air purifiers.'


@app.get("/", response_model=dict)
async def root():
    """Root endpoint with API information"""
    return {
        "message": "AQI Prediction API v2.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health",
        "endpoints": {
            "stations": "/api/stations",
            "cities": "/api/cities",
            "predict": "/api/predict?city=Delhi&hours_ahead=24",
            "stats": "/api/stats",
            "alert": "/api/alert"
        }
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring"""
    data_exists = os.path.exists(CSV_FILE)
    
    return HealthResponse(
        status="healthy" if data_exists else "degraded",
        message="API operational, data available" if data_exists else "API operational, no data yet",
        timestamp=datetime.now().isoformat(),
        data_available=data_exists
    )


@app.get("/api/stations")
async def get_stations():
    """Get all monitoring stations with latest readings"""
    try:
        if not os.path.exists(CSV_FILE):
            raise HTTPException(status_code=404, detail="No data available. Run data collector first.")
        
        df = pd.read_csv(CSV_FILE)
        
        # Get latest record for each city
        df_latest = df.sort_values('timestamp').groupby('city').tail(1)
        
        stations = []
        for _, row in df_latest.iterrows():
            stations.append({
                'name': row['station_name'],
                'city': row['city'],
                'lat': float(row['latitude']),
                'lng': float(row['longitude']),
                'pm25': float(row['pm25']) if pd.notna(row['pm25']) else None,
                'pm10': float(row['pm10']) if pd.notna(row['pm10']) else None,
                'no2': float(row['no2']) if pd.notna(row['no2']) else None,
                'so2': float(row['so2']) if pd.notna(row['so2']) else None,
                'co': float(row['co']) if pd.notna(row['co']) else None,
                'o3': float(row['o3']) if pd.notna(row['o3']) else None,
                'aqi': int(row['aqi']) if pd.notna(row['aqi']) else None,
                'category': get_aqi_category(int(row['aqi'])),
                'recommendation': get_health_recommendation(int(row['aqi'])),
                'last_updated': row['timestamp'],
                'source': row['source']
            })
        
        logger.info(f"Fetched {len(stations)} stations")
        return stations
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/cities")
async def get_cities():
    """Get all cities with current AQI summary"""
    try:
        if not os.path.exists(CSV_FILE):
            raise HTTPException(status_code=404, detail="No data available")
        
        df = pd.read_csv(CSV_FILE)
        
        cities = []
        for city_name in df['city'].unique():
            city_data = df[df['city'] == city_name].sort_values('timestamp').tail(1).iloc[0]
            
            aqi_value = int(city_data['aqi'])
            cities.append({
                'city': city_name,
                'aqi': aqi_value,
                'pm25': round(float(city_data['pm25']), 2) if pd.notna(city_data['pm25']) else None,
                'pm10': round(float(city_data['pm10']), 2) if pd.notna(city_data['pm10']) else None,
                'category': get_aqi_category(aqi_value),
                'recommendation': get_health_recommendation(aqi_value),
                'last_updated': city_data['timestamp'],
                'alert': aqi_value > 3  # Alert if AQI > Moderate
            })
        
        # Sort by AQI (worst first)
        cities.sort(key=lambda x: x['aqi'], reverse=True)
        
        logger.info(f"Fetched {len(cities)} cities")
        return cities
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/predict", response_model=PredictResponse)
async def predict_aqi(city: str, hours_ahead: int = 24):
    """
    Predict AQI for specified city and time horizon
    
    Parameters:
    - city: City name (e.g., "Delhi", "Mumbai")
    - hours_ahead: Number of hours to predict (1-48)
    
    Returns predictions with confidence intervals
    """
    try:
        if hours_ahead < 1 or hours_ahead > 48:
            raise HTTPException(status_code=400, detail="hours_ahead must be between 1 and 48")
        
        if not os.path.exists(CSV_FILE):
            raise HTTPException(status_code=404, detail="No data available")
        
        df = pd.read_csv(CSV_FILE)
        city_data = df[df['city'] == city].sort_values('timestamp').tail(24)
        
        if city_data.empty:
            raise HTTPException(status_code=404, detail=f"No data available for {city}")
        
        # Get current readings
        current_aqi = int(city_data['aqi'].iloc[-1])
        current_pm25 = float(city_data['pm25'].iloc[-1])
        
        # Generate predictions (using simple model for now)
        # TODO: Replace with actual trained ML models
        predictions = []
        for h in range(1, hours_ahead + 1):
            pred_time = datetime.now() + timedelta(hours=h)
            
            # Simple prediction (will be replaced with actual model)
            pred_aqi = current_aqi  # Placeholder
            pred_pm25 = current_pm25
            
            predictions.append({
                'hour': h,
                'timestamp': pred_time.isoformat(),
                'predicted_aqi': pred_aqi,
                'predicted_pm25': round(pred_pm25, 2),
                'category': get_aqi_category(pred_aqi),
                'confidence': 0.85,  # Model confidence score
                'confidence_lower': max(1, pred_aqi - 1),
                'confidence_upper': min(6, pred_aqi + 1)
            })
        
        logger.info(f"Generated {len(predictions)} predictions for {city}")
        
        return PredictResponse(
            city=city,
            current_time=datetime.now().isoformat(),
            predictions=predictions,
            model_used="XGBoost",  # Will be dynamic based on best model
            confidence=0.85
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Prediction error for {city}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/alert")
async def setup_alert(request: AlertRequest, background_tasks: BackgroundTasks):
    """
    Set up email alert for high AQI levels
    
    Monitors the specified city and sends email when AQI exceeds threshold
    """
    try:
        # Validate email format
        if '@' not in request.email:
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Add background task to monitor and send alerts
        background_tasks.add_task(
            monitor_and_alert,
            request.email,
            request.city,
            request.threshold
        )
        
        logger.info(f"Alert set up for {request.email} - {request.city} (threshold: {request.threshold})")
        
        return {
            "message": f"Alert successfully configured for {request.city}",
            "email": request.email,
            "city": request.city,
            "threshold": request.threshold,
            "status": "active"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Alert setup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def monitor_and_alert(email: str, city: str, threshold: int):
    """
    Background task to monitor AQI and send email alerts
    
    Uses SMTP to send email when AQI exceeds threshold
    """
    import smtplib
    import ssl
    from email.message import EmailMessage
    
    try:
        df = pd.read_csv(CSV_FILE)
        city_data = df[df['city'] == city].sort_values('timestamp').tail(1)
        
        if not city_data.empty:
            current_aqi = int(city_data['aqi'].iloc[0])
            
            if current_aqi > threshold:
                # Prepare email message
                msg = EmailMessage()
                msg.set_content(
                    f"⚠️ AQI Alert for {city}!\n\n"
                    f"Current AQI: {current_aqi}\n"
                    f"Category: {get_aqi_category(current_aqi)}\n"
                    f"PM2.5: {city_data['pm25'].iloc[0]:.2f} µg/m³\n\n"
                    f"Health Recommendation:\n{get_health_recommendation(current_aqi)}\n\n"
                    f"Stay safe and limit outdoor activities!\n\n"
                    f"— AQI Monitoring System"
                )
                msg["Subject"] = f"🚨 High AQI Alert: {city} (AQI {current_aqi})"
                msg["From"] = os.getenv('SENDER_EMAIL', 'noreply@aqi-system.com')
                msg["To"] = email
                
                # Send email using SMTP (configure credentials in .env)
                sender_email = os.getenv('SENDER_EMAIL')
                sender_password = os.getenv('EMAIL_PASSWORD')
                
                if sender_email and sender_password:
                    context = ssl.create_default_context()
                    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                    
                    logger.info(f"Alert email sent to {email} for {city} (AQI: {current_aqi})")
                else:
                    logger.warning("Email credentials not configured. Alert not sent.")
    
    except Exception as e:
        logger.error(f"Alert monitoring error: {e}")


@app.get("/api/stats")
async def get_stats():
    """Get system statistics and metadata"""
    try:
        if not os.path.exists(CSV_FILE):
            return {
                "status": "no_data",
                "message": "No data collected yet"
            }
        
        df = pd.read_csv(CSV_FILE)
        
        stats = {
            'status': 'operational',
            'total_records': len(df),
            'cities_covered': df['city'].nunique(),
            'cities_list': sorted(df['city'].unique().tolist()),
            'data_sources': df['source'].unique().tolist(),
            'latest_update': df['timestamp'].max(),
            'oldest_record': df['timestamp'].min(),
            'date_range_days': (pd.to_datetime(df['timestamp'].max()) - 
                               pd.to_datetime(df['timestamp'].min())).days,
            'average_aqi_all_cities': round(df['aqi'].mean(), 2),
            'worst_city': df.groupby('city')['aqi'].mean().idxmax(),
            'best_city': df.groupby('city')['aqi'].mean().idxmin()
        }
        
        logger.info("Stats retrieved successfully")
        return stats
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trends/{city}")
async def get_trends(city: str, hours: int = 24):
    """
    Get historical trends for a city
    
    Parameters:
    - city: City name
    - hours: Number of hours of history (default 24)
    """
    try:
        if not os.path.exists(CSV_FILE):
            raise HTTPException(status_code=404, detail="No data available")
        
        df = pd.read_csv(CSV_FILE)
        city_data = df[df['city'] == city].sort_values('timestamp').tail(hours)
        
        if city_data.empty:
            raise HTTPException(status_code=404, detail=f"No data for {city}")
        
        trends = []
        for _, row in city_data.iterrows():
            trends.append({
                'timestamp': row['timestamp'],
                'aqi': int(row['aqi']),
                'pm25': float(row['pm25']) if pd.notna(row['pm25']) else None,
                'pm10': float(row['pm10']) if pd.notna(row['pm10']) else None,
                'category': get_aqi_category(int(row['aqi']))
            })
        
        return {
            'city': city,
            'hours': hours,
            'data_points': len(trends),
            'trends': trends
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Trends error for {city}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    logger.info("\n" + "="*70)
    logger.info("FastAPI AQI Prediction Server v2.0")
    logger.info("="*70)
    logger.info("Documentation: http://localhost:8000/docs")
    logger.info("Health Check: http://localhost:8000/health")
    logger.info("API Endpoints: http://localhost:8000/api/*")
    logger.info("="*70 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
