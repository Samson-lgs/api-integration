"""
Flask Web Service for Render
Provides API endpoints and scheduled data collection
"""

from flask import Flask, jsonify, request
from cloud_collector import CloudAirQualityCollector
from apscheduler.schedulers.background import BackgroundScheduler
import psycopg2
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize scheduler for automatic data collection
scheduler = BackgroundScheduler()

def scheduled_collection():
    """Function to run on schedule"""
    try:
        logger.info("Starting scheduled data collection...")
        collector = CloudAirQualityCollector()
        collector.collect_all_data()
        collector.close()
        logger.info("Scheduled collection completed")
    except Exception as e:
        logger.error(f"Scheduled collection error: {e}")

# Schedule data collection every hour
scheduler.add_job(func=scheduled_collection, trigger="interval", hours=1)
scheduler.start()

@app.route('/')
def home():
    """Home endpoint with API documentation"""
    return jsonify({
        "message": "Air Quality Data Collection API",
        "version": "1.0",
        "endpoints": {
            "/": "API documentation",
            "/health": "Health check",
            "/collect": "Trigger manual data collection",
            "/stats": "Get database statistics",
            "/latest": "Get latest air quality data",
            "/city/<city_name>": "Get data for specific city"
        },
        "status": "running",
        "auto_collection": "Every 1 hour"
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    try:
        # Check database connection
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM stations")
        station_count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "stations": station_count
        })
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/collect', methods=['POST'])
def trigger_collection():
    """Manually trigger data collection"""
    try:
        collector = CloudAirQualityCollector()
        stations, data_points = collector.collect_all_data()
        collector.close()
        
        return jsonify({
            "status": "success",
            "message": "Data collection completed",
            "stations": stations,
            "data_points": data_points
        })
    except Exception as e:
        logger.error(f"Collection error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/stats')
def get_stats():
    """Get database statistics"""
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Get total counts
        cursor.execute("SELECT COUNT(*) FROM stations")
        total_stations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM air_quality_data")
        total_data = cursor.fetchone()[0]
        
        # Get counts by source
        cursor.execute("""
            SELECT data_source, COUNT(DISTINCT station_id) as stations, COUNT(*) as data_points
            FROM air_quality_data
            GROUP BY data_source
        """)
        source_stats = cursor.fetchall()
        
        # Get pollutant counts
        cursor.execute("""
            SELECT pollutant_id, COUNT(*) as count
            FROM air_quality_data
            GROUP BY pollutant_id
            ORDER BY count DESC
        """)
        pollutant_stats = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "total_stations": total_stations,
            "total_data_points": total_data,
            "by_source": [
                {"source": row[0], "stations": row[1], "data_points": row[2]}
                for row in source_stats
            ],
            "pollutants": [
                {"pollutant": row[0], "count": row[1]}
                for row in pollutant_stats
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/latest')
def get_latest():
    """Get latest air quality readings"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                s.station_id,
                s.station_name,
                s.city,
                s.data_source,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category,
                aq.temperature,
                aq.humidity
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            ORDER BY aq.recorded_at DESC
            LIMIT %s
        """, (limit,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "station_id": row[0],
                "station_name": row[1],
                "city": row[2],
                "data_source": row[3],
                "recorded_at": row[4].isoformat() if row[4] else None,
                "pollutant_id": row[5],
                "pollutant_avg": float(row[6]) if row[6] else None,
                "aqi": float(row[7]) if row[7] else None,
                "aqi_category": row[8],
                "temperature": float(row[9]) if row[9] else None,
                "humidity": float(row[10]) if row[10] else None
            })
        
        return jsonify({
            "count": len(results),
            "data": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/city/<city_name>')
def get_city_data(city_name):
    """Get air quality data for a specific city"""
    try:
        database_url = os.getenv('DATABASE_URL')
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                s.station_id,
                s.station_name,
                s.data_source,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category,
                aq.temperature,
                aq.humidity
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE LOWER(s.city) = LOWER(%s)
            ORDER BY aq.recorded_at DESC
            LIMIT 100
        """, (city_name,))
        
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        if not rows:
            return jsonify({
                "message": f"No data found for city: {city_name}"
            }), 404
        
        results = []
        for row in rows:
            results.append({
                "station_id": row[0],
                "station_name": row[1],
                "data_source": row[2],
                "recorded_at": row[3].isoformat() if row[3] else None,
                "pollutant_id": row[4],
                "pollutant_avg": float(row[5]) if row[5] else None,
                "aqi": float(row[6]) if row[6] else None,
                "aqi_category": row[7],
                "temperature": float(row[8]) if row[8] else None,
                "humidity": float(row[9]) if row[9] else None
            })
        
        return jsonify({
            "city": city_name,
            "count": len(results),
            "data": results
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
