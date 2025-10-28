"""
Air Quality Monitoring System - Flask REST API
Production-ready backend with ML predictions, data retrieval, and analytics
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import os
import logging
import pickle
import numpy as np
import pandas as pd
from functools import wraps
import traceback

# Import database manager
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'database'))
from db_manager import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for React frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000", "http://localhost:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max request size

# Get database manager
db = get_db_manager()

# Load ML models globally
ML_MODELS = {}
SCALER = None

def load_ml_models():
    """Load trained ML models"""
    global ML_MODELS, SCALER
    try:
        models_dir = os.path.join(os.path.dirname(__file__), '..', 'models')
        
        # Load scaler
        scaler_path = os.path.join(models_dir, 'scaler.pkl')
        if os.path.exists(scaler_path):
            with open(scaler_path, 'rb') as f:
                SCALER = pickle.load(f)
            logger.info("✅ Scaler loaded successfully")
        
        # Load models
        model_files = {
            'linear_regression': 'linear_regression_model.pkl',
            'random_forest': 'random_forest_model.pkl',
            'xgboost': 'xgboost_model.pkl',
            'ensemble': 'ensemble_model.pkl'
        }
        
        for model_name, filename in model_files.items():
            model_path = os.path.join(models_dir, filename)
            if os.path.exists(model_path):
                with open(model_path, 'rb') as f:
                    ML_MODELS[model_name] = pickle.load(f)
                logger.info(f"✅ {model_name} model loaded successfully")
        
        logger.info(f"Total models loaded: {len(ML_MODELS)}")
    except Exception as e:
        logger.error(f"Failed to load ML models: {e}")

# Load models on startup
load_ml_models()

# ============================================================================
# DECORATORS & UTILITIES
# ============================================================================

def handle_errors(f):
    """Error handling decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}")
            logger.error(traceback.format_exc())
            return jsonify({
                'status': 'error',
                'message': str(e),
                'endpoint': request.endpoint
            }), 500
    return decorated_function

def validate_pagination():
    """Get and validate pagination parameters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    page = max(1, page)
    per_page = min(max(1, per_page), 100)  # Max 100 per page
    
    offset = (page - 1) * per_page
    
    return page, per_page, offset

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.route('/')
def root():
    """Root endpoint with API documentation"""
    return jsonify({
        'name': 'Air Quality Monitoring API',
        'version': '2.0.0',
        'description': 'RESTful API for air quality data and ML predictions',
        'endpoints': {
            'health': {
                'GET /api/health': 'Health check and system status'
            },
            'stations': {
                'GET /api/stations': 'Get all monitoring stations',
                'GET /api/stations/<station_id>': 'Get specific station',
                'GET /api/cities': 'Get list of all cities'
            },
            'data': {
                'GET /api/data/latest': 'Get latest air quality readings',
                'GET /api/data/station/<station_id>': 'Get station readings',
                'GET /api/data/city/<city>': 'Get city readings',
                'GET /api/data/timeseries': 'Get time-series data for ML'
            },
            'predictions': {
                'POST /api/predict': 'Generate AQI prediction',
                'GET /api/predictions': 'Get saved predictions',
                'GET /api/predictions/<station_id>': 'Get station predictions'
            },
            'analytics': {
                'GET /api/analytics/summary': 'Get overall summary',
                'GET /api/analytics/city/<city>': 'Get city analytics',
                'GET /api/analytics/trends': 'Get pollutant trends'
            }
        },
        'documentation': 'https://github.com/your-repo/api-docs',
        'status': 'operational'
    })

@app.route('/api/health')
@handle_errors
def health_check():
    """Health check endpoint"""
    # Check database connection
    db_status = 'healthy' if db.check_connection() else 'unhealthy'
    
    # Get database stats
    stats = db.get_statistics() if db_status == 'healthy' else {}
    
    # Check models
    models_loaded = len(ML_MODELS)
    
    return jsonify({
        'status': 'healthy' if db_status == 'healthy' else 'degraded',
        'timestamp': datetime.now().isoformat(),
        'services': {
            'database': db_status,
            'ml_models': f'{models_loaded} models loaded',
            'api': 'operational'
        },
        'statistics': {
            'total_stations': stats.get('total_stations', 0),
            'total_readings': stats.get('total_readings', 0),
            'latest_reading': stats.get('latest_reading').isoformat() if stats.get('latest_reading') else None,
            'cities_covered': stats.get('cities_covered', 0)
        }
    })

# ============================================================================
# STATIONS ENDPOINTS
# ============================================================================

@app.route('/api/stations')
@handle_errors
def get_stations():
    """Get all monitoring stations"""
    active_only = request.args.get('active_only', 'true').lower() == 'true'
    
    stations = db.get_all_stations(active_only=active_only)
    
    return jsonify({
        'status': 'success',
        'count': len(stations),
        'data': stations
    })

@app.route('/api/stations/<station_id>')
@handle_errors
def get_station(station_id):
    """Get specific station details"""
    stations = db.get_all_stations(active_only=False)
    station = next((s for s in stations if s['station_id'] == station_id), None)
    
    if not station:
        return jsonify({
            'status': 'error',
            'message': f'Station {station_id} not found'
        }), 404
    
    # Get recent readings
    recent_readings = db.get_station_readings(station_id, hours=24)
    
    return jsonify({
        'status': 'success',
        'station': station,
        'recent_readings': recent_readings[:10]
    })

@app.route('/api/cities')
@handle_errors
def get_cities():
    """Get list of all cities with monitoring stations"""
    cities = db.get_cities_list()
    
    return jsonify({
        'status': 'success',
        'count': len(cities),
        'data': cities
    })

# ============================================================================
# DATA ENDPOINTS
# ============================================================================

@app.route('/api/data/latest')
@handle_errors
def get_latest_data():
    """Get latest air quality readings"""
    limit = request.args.get('limit', 50, type=int)
    limit = min(limit, 200)  # Max 200 records
    
    city = request.args.get('city')
    
    readings = db.get_latest_readings(limit=limit, city=city)
    
    return jsonify({
        'status': 'success',
        'count': len(readings),
        'data': readings
    })

@app.route('/api/data/station/<station_id>')
@handle_errors
def get_station_data(station_id):
    """Get readings for a specific station"""
    hours = request.args.get('hours', 24, type=int)
    hours = min(hours, 168)  # Max 7 days
    
    readings = db.get_station_readings(station_id, hours=hours)
    
    if not readings:
        return jsonify({
            'status': 'error',
            'message': f'No data found for station {station_id}'
        }), 404
    
    return jsonify({
        'status': 'success',
        'station_id': station_id,
        'count': len(readings),
        'data': readings
    })

@app.route('/api/data/city/<city>')
@handle_errors
def get_city_data(city):
    """Get air quality data for a city"""
    limit = request.args.get('limit', 100, type=int)
    
    readings = db.get_latest_readings(limit=limit, city=city)
    
    if not readings:
        return jsonify({
            'status': 'error',
            'message': f'No data found for city {city}'
        }), 404
    
    return jsonify({
        'status': 'success',
        'city': city,
        'count': len(readings),
        'data': readings
    })

@app.route('/api/data/timeseries')
@handle_errors
def get_timeseries_data():
    """Get time-series data for ML training/analysis"""
    station_id = request.args.get('station_id', required=True)
    pollutant_id = request.args.get('pollutant_id', 'PM2.5')
    days = request.args.get('days', 7, type=int)
    
    if not station_id:
        return jsonify({
            'status': 'error',
            'message': 'station_id parameter is required'
        }), 400
    
    data = db.get_time_series_data(station_id, pollutant_id, days=days)
    
    return jsonify({
        'status': 'success',
        'station_id': station_id,
        'pollutant_id': pollutant_id,
        'days': days,
        'count': len(data),
        'data': data
    })

# ============================================================================
# PREDICTION ENDPOINTS
# ============================================================================

@app.route('/api/predict', methods=['POST'])
@handle_errors
def predict_aqi():
    """Generate AQI prediction using ML models"""
    if not ML_MODELS:
        return jsonify({
            'status': 'error',
            'message': 'ML models not loaded'
        }), 503
    
    # Get request data
    data = request.get_json()
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Request body is required'
        }), 400
    
    # Required fields
    station_id = data.get('station_id')
    features = data.get('features')  # Dictionary of feature values
    model_name = data.get('model', 'linear_regression')
    
    if not station_id or not features:
        return jsonify({
            'status': 'error',
            'message': 'station_id and features are required'
        }), 400
    
    # Get model
    model = ML_MODELS.get(model_name)
    if not model:
        return jsonify({
            'status': 'error',
            'message': f'Model {model_name} not found. Available: {list(ML_MODELS.keys())}'
        }), 400
    
    try:
        # Convert features to DataFrame
        features_df = pd.DataFrame([features])
        
        # Scale features if scaler available
        if SCALER:
            features_scaled = SCALER.transform(features_df)
        else:
            features_scaled = features_df.values
        
        # Make prediction
        predicted_aqi = model.predict(features_scaled)[0]
        
        # Calculate confidence interval (simplified)
        confidence_lower = max(0, predicted_aqi - 10)
        confidence_upper = min(500, predicted_aqi + 10)
        
        # Determine AQI category
        if predicted_aqi <= 50:
            category = 'Good'
        elif predicted_aqi <= 100:
            category = 'Satisfactory'
        elif predicted_aqi <= 200:
            category = 'Moderate'
        elif predicted_aqi <= 300:
            category = 'Poor'
        elif predicted_aqi <= 400:
            category = 'Very Poor'
        else:
            category = 'Severe'
        
        # Save prediction to database
        prediction_data = {
            'station_id': station_id,
            'predicted_for': datetime.now() + timedelta(hours=1),
            'model_name': model_name,
            'predicted_aqi': float(predicted_aqi),
            'confidence_lower': float(confidence_lower),
            'confidence_upper': float(confidence_upper),
            'features_used': features
        }
        
        prediction_id = db.insert_prediction(prediction_data)
        
        return jsonify({
            'status': 'success',
            'prediction_id': prediction_id,
            'station_id': station_id,
            'predicted_aqi': round(float(predicted_aqi), 2),
            'aqi_category': category,
            'confidence_interval': {
                'lower': round(float(confidence_lower), 2),
                'upper': round(float(confidence_upper), 2)
            },
            'model_used': model_name,
            'predicted_for': prediction_data['predicted_for'].isoformat(),
            'prediction_time': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Prediction failed: {str(e)}'
        }), 500

@app.route('/api/predictions')
@handle_errors
def get_predictions():
    """Get saved predictions"""
    hours_ahead = request.args.get('hours_ahead', 24, type=int)
    
    predictions = db.get_predictions(hours_ahead=hours_ahead)
    
    return jsonify({
        'status': 'success',
        'count': len(predictions),
        'data': predictions
    })

@app.route('/api/predictions/<station_id>')
@handle_errors
def get_station_predictions(station_id):
    """Get predictions for a specific station"""
    hours_ahead = request.args.get('hours_ahead', 24, type=int)
    
    predictions = db.get_predictions(station_id=station_id, hours_ahead=hours_ahead)
    
    return jsonify({
        'status': 'success',
        'station_id': station_id,
        'count': len(predictions),
        'data': predictions
    })

# ============================================================================
# ANALYTICS ENDPOINTS
# ============================================================================

@app.route('/api/analytics/summary')
@handle_errors
def get_summary():
    """Get overall system summary"""
    stats = db.get_statistics()
    
    return jsonify({
        'status': 'success',
        'summary': stats
    })

@app.route('/api/analytics/city/<city>')
@handle_errors
def get_city_analytics(city):
    """Get analytics for a specific city"""
    summary = db.get_city_summary(city)
    
    if not summary or summary['total_stations'] == 0:
        return jsonify({
            'status': 'error',
            'message': f'No data found for city {city}'
        }), 404
    
    return jsonify({
        'status': 'success',
        'city': city,
        'analytics': summary
    })

@app.route('/api/analytics/trends')
@handle_errors
def get_trends():
    """Get pollutant trends"""
    pollutant_id = request.args.get('pollutant_id', 'PM2.5')
    days = request.args.get('days', 7, type=int)
    
    trends = db.get_pollutant_trends(pollutant_id, days=days)
    
    return jsonify({
        'status': 'success',
        'pollutant_id': pollutant_id,
        'days': days,
        'count': len(trends),
        'data': trends
    })

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/refresh-views', methods=['POST'])
@handle_errors
def refresh_views():
    """Refresh materialized views"""
    success = db.refresh_materialized_views()
    
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Materialized views refreshed successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to refresh materialized views'
        }), 500

@app.route('/api/admin/models')
@handle_errors
def get_models_info():
    """Get information about loaded ML models"""
    # Load metrics if available
    metrics = {}
    metrics_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'metrics.json')
    if os.path.exists(metrics_path):
        import json
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
    
    return jsonify({
        'status': 'success',
        'models_loaded': list(ML_MODELS.keys()),
        'scaler_loaded': SCALER is not None,
        'total_models': len(ML_MODELS),
        'metrics': metrics
    })

@app.route('/api/admin/models/reload', methods=['POST'])
@handle_errors
def reload_models():
    """Reload ML models from disk"""
    load_ml_models()
    return jsonify({
        'status': 'success',
        'message': 'Models reloaded successfully',
        'models_loaded': list(ML_MODELS.keys())
    })

@app.route('/api/admin/stats')
@handle_errors
def get_system_stats():
    """Get system statistics and metrics"""
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            # Database stats
            cursor.execute("""
                SELECT 
                    (SELECT COUNT(*) FROM stations) as total_stations,
                    (SELECT COUNT(*) FROM air_quality_data) as total_readings,
                    (SELECT COUNT(*) FROM predictions) as total_predictions,
                    (SELECT COUNT(DISTINCT city) FROM stations) as total_cities,
                    (SELECT MIN(timestamp) FROM air_quality_data) as earliest_reading,
                    (SELECT MAX(timestamp) FROM air_quality_data) as latest_reading
            """)
            stats = cursor.fetchone()
            
            # Recent activity
            cursor.execute("""
                SELECT 
                    DATE(timestamp) as date,
                    COUNT(*) as readings_count
                FROM air_quality_data
                WHERE timestamp >= NOW() - INTERVAL '7 days'
                GROUP BY DATE(timestamp)
                ORDER BY date DESC
            """)
            recent_activity = cursor.fetchall()
    
    return jsonify({
        'status': 'success',
        'database': {
            'total_stations': stats[0],
            'total_readings': stats[1],
            'total_predictions': stats[2],
            'total_cities': stats[3],
            'earliest_reading': stats[4].isoformat() if stats[4] else None,
            'latest_reading': stats[5].isoformat() if stats[5] else None
        },
        'recent_activity': [
            {'date': str(row[0]), 'count': row[1]} 
            for row in recent_activity
        ],
        'models': {
            'loaded': len(ML_MODELS),
            'available': list(ML_MODELS.keys())
        }
    })

@app.route('/api/admin/data/cleanup', methods=['POST'])
@handle_errors
def cleanup_old_data():
    """Clean up old data (older than retention period)"""
    days = request.json.get('retention_days', 90)
    
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                DELETE FROM air_quality_data
                WHERE timestamp < NOW() - INTERVAL '%s days'
                RETURNING COUNT(*)
            """, (days,))
            deleted_count = cursor.fetchone()[0]
            conn.commit()
    
    return jsonify({
        'status': 'success',
        'message': f'Deleted {deleted_count} old records',
        'retention_days': days
    })

@app.route('/api/monitoring/metrics')
@handle_errors
def get_monitoring_metrics():
    """Get monitoring metrics for observability (Prometheus format compatible)"""
    with db.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_readings,
                    COUNT(*) FILTER (WHERE timestamp >= NOW() - INTERVAL '1 hour') as readings_last_hour,
                    COUNT(*) FILTER (WHERE timestamp >= NOW() - INTERVAL '24 hours') as readings_last_day,
                    AVG(pm25) FILTER (WHERE timestamp >= NOW() - INTERVAL '1 hour') as avg_pm25_last_hour,
                    MAX(aqi) FILTER (WHERE timestamp >= NOW() - INTERVAL '1 hour') as max_aqi_last_hour
                FROM air_quality_data
            """)
            metrics = cursor.fetchone()
    
    return jsonify({
        'status': 'success',
        'timestamp': datetime.utcnow().isoformat(),
        'metrics': {
            'total_readings': metrics[0],
            'readings_last_hour': metrics[1],
            'readings_last_day': metrics[2],
            'avg_pm25_last_hour': float(metrics[3]) if metrics[3] else 0,
            'max_aqi_last_hour': metrics[4] if metrics[4] else 0,
            'models_loaded': len(ML_MODELS)
        }
    })

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'requested_url': request.url
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error': str(error)
    }), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting Air Quality API on port {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Models loaded: {len(ML_MODELS)}")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
