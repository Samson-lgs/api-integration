"""
Production API for AQI Prediction System
Serves real-time data, predictions, and analytics
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:5432/aqi_db')


def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        conn.close()
        return jsonify({
            'status': 'healthy',
            'message': 'API and database operational',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500


@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get latest readings from all stations"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT DISTINCT ON (city, station_name)
                city,
                station_name as name,
                latitude as lat,
                longitude as lng,
                pm25,
                pm10,
                no2,
                so2,
                co,
                o3,
                aqi,
                get_aqi_category(aqi) as category,
                timestamp as last_updated,
                source
            FROM raw_air_quality_data
            WHERE timestamp >= NOW() - INTERVAL '2 hours'
            ORDER BY city, station_name, timestamp DESC
        """
        
        cursor.execute(query)
        stations = cursor.fetchall()
        conn.close()
        
        return jsonify(stations)
        
    except Exception as e:
        logger.error(f"Error fetching stations: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all cities with latest AQI"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                city,
                ROUND(AVG(aqi)) as aqi,
                ROUND(AVG(pm25), 2) as pm25,
                ROUND(AVG(pm10), 2) as pm10,
                get_aqi_category(ROUND(AVG(aqi))) as category,
                MAX(timestamp) as last_updated,
                COUNT(*) as station_count
            FROM raw_air_quality_data
            WHERE timestamp >= NOW() - INTERVAL '2 hours'
            GROUP BY city
            ORDER BY aqi DESC
        """
        
        cursor.execute(query)
        cities = cursor.fetchall()
        conn.close()
        
        return jsonify(cities)
        
    except Exception as e:
        logger.error(f"Error fetching cities: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/trends/<city>', methods=['GET'])
def get_trends(city):
    """Get 24-hour historical trends for a city"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                DATE_TRUNC('hour', timestamp) as hour,
                ROUND(AVG(aqi)) as aqi,
                ROUND(AVG(pm25), 2) as pm25,
                ROUND(AVG(pm10), 2) as pm10,
                ROUND(AVG(no2), 2) as no2,
                ROUND(AVG(so2), 2) as so2,
                ROUND(AVG(co), 2) as co
            FROM raw_air_quality_data
            WHERE city = %s 
                AND timestamp >= NOW() - INTERVAL '%s hours'
            GROUP BY hour
            ORDER BY hour ASC
        """
        
        cursor.execute(query, (city, hours))
        trends = cursor.fetchall()
        conn.close()
        
        return jsonify(trends)
        
    except Exception as e:
        logger.error(f"Error fetching trends: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predictions/<city>', methods=['GET'])
def get_predictions(city):
    """Get predictions for a city"""
    try:
        hours = request.args.get('hours', 48, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                prediction_timestamp as timestamp,
                predicted_aqi as aqi,
                hours_ahead,
                model_type,
                get_aqi_category(ROUND(predicted_aqi)) as category,
                created_at
            FROM aqi_predictions
            WHERE city = %s 
                AND prediction_timestamp >= NOW()
                AND hours_ahead <= %s
            ORDER BY prediction_timestamp ASC
            LIMIT 48
        """
        
        cursor.execute(query, (city, hours))
        predictions = cursor.fetchall()
        conn.close()
        
        return jsonify(predictions)
        
    except Exception as e:
        logger.error(f"Error fetching predictions: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/predict', methods=['POST'])
def generate_prediction():
    """Generate new prediction for a location"""
    try:
        data = request.json
        city = data.get('city')
        hours_ahead = data.get('hours', 48)
        
        if not city:
            return jsonify({'error': 'City is required'}), 400
        
        # Import prediction engine
        from ml_prediction_engine import AQIPredictionEngine
        
        engine = AQIPredictionEngine(model_type='xgboost')
        engine.load_model()
        
        predictions = engine.predict_future(city, hours_ahead=hours_ahead)
        engine.store_predictions(predictions)
        
        return jsonify({
            'success': True,
            'city': city,
            'predictions': len(predictions),
            'data': predictions[:10]  # Return first 10
        })
        
    except Exception as e:
        logger.error(f"Error generating prediction: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Get active health alerts"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                city,
                alert_type,
                severity,
                message,
                aqi_value,
                created_at
            FROM health_alerts
            WHERE is_active = TRUE
            ORDER BY created_at DESC
            LIMIT 50
        """
        
        cursor.execute(query)
        alerts = cursor.fetchall()
        conn.close()
        
        return jsonify(alerts)
        
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health-impact/<city>', methods=['GET'])
def get_health_impact(city):
    """Get health impact summary for a city"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get latest AQI
        cursor.execute("""
            SELECT 
                ROUND(AVG(aqi)) as aqi,
                get_aqi_category(ROUND(AVG(aqi))) as category,
                get_health_recommendation(ROUND(AVG(aqi))) as recommendation
            FROM raw_air_quality_data
            WHERE city = %s 
                AND timestamp >= NOW() - INTERVAL '1 hour'
        """, (city,))
        
        current = cursor.fetchone()
        
        # Get 24h average
        cursor.execute("""
            SELECT ROUND(AVG(aqi)) as avg_aqi_24h
            FROM raw_air_quality_data
            WHERE city = %s 
                AND timestamp >= NOW() - INTERVAL '24 hours'
        """, (city,))
        
        avg_24h = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'city': city,
            'current_aqi': current['aqi'] if current else None,
            'category': current['category'] if current else 'Unknown',
            'recommendation': current['recommendation'] if current else 'No data',
            'avg_24h': avg_24h['avg_aqi_24h'] if avg_24h else None
        })
        
    except Exception as e:
        logger.error(f"Error fetching health impact: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/compare', methods=['POST'])
def compare_cities():
    """Compare AQI across multiple cities"""
    try:
        data = request.json
        cities = data.get('cities', [])
        
        if not cities:
            return jsonify({'error': 'Cities array is required'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join(['%s'] * len(cities))
        query = f"""
            SELECT 
                city,
                ROUND(AVG(aqi)) as aqi,
                ROUND(AVG(pm25), 2) as pm25,
                ROUND(AVG(pm10), 2) as pm10,
                get_aqi_category(ROUND(AVG(aqi))) as category,
                MAX(timestamp) as last_updated
            FROM raw_air_quality_data
            WHERE city IN ({placeholders})
                AND timestamp >= NOW() - INTERVAL '2 hours'
            GROUP BY city
            ORDER BY aqi DESC
        """
        
        cursor.execute(query, tuple(cities))
        comparison = cursor.fetchall()
        conn.close()
        
        return jsonify(comparison)
        
    except Exception as e:
        logger.error(f"Error comparing cities: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total records
        cursor.execute("SELECT COUNT(*) as total FROM raw_air_quality_data")
        total_records = cursor.fetchone()['total']
        
        # Cities covered
        cursor.execute("SELECT COUNT(DISTINCT city) as cities FROM raw_air_quality_data")
        cities_count = cursor.fetchone()['cities']
        
        # Active predictions
        cursor.execute("""
            SELECT COUNT(*) as predictions 
            FROM aqi_predictions 
            WHERE prediction_timestamp >= NOW()
        """)
        predictions_count = cursor.fetchone()['predictions']
        
        # Latest update
        cursor.execute("SELECT MAX(timestamp) as latest FROM raw_air_quality_data")
        latest_update = cursor.fetchone()['latest']
        
        conn.close()
        
        return jsonify({
            'total_records': total_records,
            'cities_covered': cities_count,
            'active_predictions': predictions_count,
            'latest_update': latest_update.isoformat() if latest_update else None
        })
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/model-info', methods=['GET'])
def get_model_info():
    """Get ML model information"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """
            SELECT 
                model_type,
                model_version,
                training_date,
                mae,
                rmse,
                r2_score,
                training_samples
            FROM model_metadata
            WHERE is_active = TRUE
            ORDER BY training_date DESC
        """
        
        cursor.execute(query)
        models = cursor.fetchall()
        conn.close()
        
        return jsonify(models)
        
    except Exception as e:
        logger.error(f"Error fetching model info: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    logger.info("Starting Production API Server...")
    logger.info("Database: " + DATABASE_URL)
    app.run(host='0.0.0.0', port=5000, debug=True)
