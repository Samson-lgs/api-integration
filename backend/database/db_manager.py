"""
Database Manager
Handles PostgreSQL connection, initialization, and management
"""

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values
from contextlib import contextmanager
import os
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages all database operations"""
    
    def __init__(self, connection_string=None):
        """Initialize database manager"""
        self.connection_string = connection_string or os.getenv('DATABASE_URL')
        if not self.connection_string:
            raise ValueError("DATABASE_URL environment variable not set")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(self.connection_string)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def get_cursor(self, dict_cursor=True):
        """Context manager for database cursors"""
        with self.get_connection() as conn:
            cursor_factory = RealDictCursor if dict_cursor else None
            cursor = conn.cursor(cursor_factory=cursor_factory)
            try:
                yield cursor
            finally:
                cursor.close()
    
    def initialize_schema(self, schema_file='schema.sql'):
        """Initialize database schema from SQL file"""
        try:
            schema_path = os.path.join(os.path.dirname(__file__), schema_file)
            
            with open(schema_path, 'r') as f:
                schema_sql = f.read()
            
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(schema_sql)
                cursor.close()
            
            logger.info("Database schema initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            return False
    
    def check_connection(self):
        """Check if database connection is working"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Connection check failed: {e}")
            return False
    
    def get_statistics(self):
        """Get database statistics"""
        with self.get_cursor() as cursor:
            cursor.execute("SELECT * FROM get_db_statistics()")
            return cursor.fetchone()
    
    def refresh_materialized_views(self):
        """Refresh materialized views for better performance"""
        try:
            with self.get_cursor(dict_cursor=False) as cursor:
                cursor.execute("SELECT refresh_materialized_views()")
            logger.info("Materialized views refreshed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to refresh materialized views: {e}")
            return False
    
    # ========================================================================
    # STATIONS OPERATIONS
    # ========================================================================
    
    def upsert_station(self, station_data):
        """Insert or update station information"""
        with self.get_cursor(dict_cursor=False) as cursor:
            cursor.execute("""
                INSERT INTO stations (
                    station_id, station_name, city, state, country,
                    latitude, longitude, data_source, is_active, last_updated
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (station_id) 
                DO UPDATE SET
                    station_name = EXCLUDED.station_name,
                    city = EXCLUDED.city,
                    state = EXCLUDED.state,
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    last_updated = EXCLUDED.last_updated,
                    is_active = EXCLUDED.is_active
            """, (
                station_data['station_id'],
                station_data['station_name'],
                station_data['city'],
                station_data.get('state'),
                station_data.get('country', 'India'),
                station_data.get('latitude'),
                station_data.get('longitude'),
                station_data['data_source'],
                station_data.get('is_active', True),
                datetime.now()
            ))
    
    def get_all_stations(self, active_only=True):
        """Get all monitoring stations"""
        with self.get_cursor() as cursor:
            query = "SELECT * FROM stations"
            if active_only:
                query += " WHERE is_active = TRUE"
            query += " ORDER BY city, station_name"
            
            cursor.execute(query)
            return cursor.fetchall()
    
    def get_stations_by_city(self, city):
        """Get stations in a specific city"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT * FROM stations 
                WHERE LOWER(city) = LOWER(%s) AND is_active = TRUE
                ORDER BY station_name
            """, (city,))
            return cursor.fetchall()
    
    # ========================================================================
    # AIR QUALITY DATA OPERATIONS
    # ========================================================================
    
    def insert_air_quality_data(self, data):
        """Insert air quality reading"""
        with self.get_cursor(dict_cursor=False) as cursor:
            # Get AQI category ID
            aqi_category_id = None
            if data.get('aqi'):
                cursor.execute("""
                    SELECT category_id FROM aqi_categories
                    WHERE %s BETWEEN min_aqi AND max_aqi
                    LIMIT 1
                """, (data['aqi'],))
                result = cursor.fetchone()
                if result:
                    aqi_category_id = result[0]
            
            cursor.execute("""
                INSERT INTO air_quality_data (
                    station_id, recorded_at, pollutant_id,
                    pollutant_avg, pollutant_min, pollutant_max,
                    aqi, aqi_category_id,
                    temperature, humidity, wind_speed, wind_direction, pressure,
                    data_source, data_quality_flag
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data['station_id'],
                data['recorded_at'],
                data['pollutant_id'],
                data.get('pollutant_avg'),
                data.get('pollutant_min'),
                data.get('pollutant_max'),
                data.get('aqi'),
                aqi_category_id,
                data.get('temperature'),
                data.get('humidity'),
                data.get('wind_speed'),
                data.get('wind_direction'),
                data.get('pressure'),
                data.get('data_source'),
                data.get('data_quality_flag', 'GOOD')
            ))
    
    def bulk_insert_air_quality_data(self, data_list):
        """Bulk insert air quality readings for better performance"""
        with self.get_cursor(dict_cursor=False) as cursor:
            # Prepare data tuples
            values = []
            for data in data_list:
                # Get AQI category ID
                aqi_category_id = None
                if data.get('aqi'):
                    cursor.execute("""
                        SELECT category_id FROM aqi_categories
                        WHERE %s BETWEEN min_aqi AND max_aqi
                        LIMIT 1
                    """, (data['aqi'],))
                    result = cursor.fetchone()
                    if result:
                        aqi_category_id = result[0]
                
                values.append((
                    data['station_id'],
                    data['recorded_at'],
                    data['pollutant_id'],
                    data.get('pollutant_avg'),
                    data.get('pollutant_min'),
                    data.get('pollutant_max'),
                    data.get('aqi'),
                    aqi_category_id,
                    data.get('temperature'),
                    data.get('humidity'),
                    data.get('wind_speed'),
                    data.get('wind_direction'),
                    data.get('pressure'),
                    data.get('data_source'),
                    data.get('data_quality_flag', 'GOOD')
                ))
            
            # Bulk insert
            execute_values(cursor, """
                INSERT INTO air_quality_data (
                    station_id, recorded_at, pollutant_id,
                    pollutant_avg, pollutant_min, pollutant_max,
                    aqi, aqi_category_id,
                    temperature, humidity, wind_speed, wind_direction, pressure,
                    data_source, data_quality_flag
                ) VALUES %s
            """, values)
            
            logger.info(f"Bulk inserted {len(values)} air quality readings")
    
    def get_latest_readings(self, limit=50, city=None):
        """Get latest air quality readings"""
        with self.get_cursor() as cursor:
            query = """
                SELECT 
                    aq.id,
                    s.station_id,
                    s.station_name,
                    s.city,
                    s.state,
                    aq.recorded_at,
                    aq.pollutant_id,
                    p.pollutant_name,
                    aq.pollutant_avg,
                    aq.aqi,
                    ac.category_name AS aqi_category,
                    ac.color_code,
                    aq.temperature,
                    aq.humidity,
                    aq.data_source
                FROM air_quality_data aq
                JOIN stations s ON aq.station_id = s.station_id
                JOIN pollutants p ON aq.pollutant_id = p.pollutant_id
                LEFT JOIN aqi_categories ac ON aq.aqi_category_id = ac.category_id
            """
            
            if city:
                query += " WHERE LOWER(s.city) = LOWER(%s)"
                query += " ORDER BY aq.recorded_at DESC LIMIT %s"
                cursor.execute(query, (city, limit))
            else:
                query += " ORDER BY aq.recorded_at DESC LIMIT %s"
                cursor.execute(query, (limit,))
            
            return cursor.fetchall()
    
    def get_station_readings(self, station_id, hours=24):
        """Get readings for a specific station"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    aq.recorded_at,
                    aq.pollutant_id,
                    p.pollutant_name,
                    aq.pollutant_avg,
                    aq.aqi,
                    ac.category_name AS aqi_category,
                    aq.temperature,
                    aq.humidity
                FROM air_quality_data aq
                JOIN pollutants p ON aq.pollutant_id = p.pollutant_id
                LEFT JOIN aqi_categories ac ON aq.aqi_category_id = ac.category_id
                WHERE aq.station_id = %s
                    AND aq.recorded_at >= NOW() - INTERVAL '%s hours'
                ORDER BY aq.recorded_at DESC
            """, (station_id, hours))
            return cursor.fetchall()
    
    def get_time_series_data(self, station_id, pollutant_id, days=7):
        """Get time-series data for ML training"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    recorded_at,
                    pollutant_avg,
                    aqi,
                    temperature,
                    humidity,
                    wind_speed,
                    pressure
                FROM air_quality_data
                WHERE station_id = %s
                    AND pollutant_id = %s
                    AND recorded_at >= NOW() - INTERVAL '%s days'
                ORDER BY recorded_at ASC
            """, (station_id, pollutant_id, days))
            return cursor.fetchall()
    
    # ========================================================================
    # PREDICTIONS OPERATIONS
    # ========================================================================
    
    def insert_prediction(self, prediction_data):
        """Insert AQI prediction"""
        with self.get_cursor(dict_cursor=False) as cursor:
            # Get predicted category ID
            predicted_category_id = None
            if prediction_data.get('predicted_aqi'):
                cursor.execute("""
                    SELECT category_id FROM aqi_categories
                    WHERE %s BETWEEN min_aqi AND max_aqi
                    LIMIT 1
                """, (prediction_data['predicted_aqi'],))
                result = cursor.fetchone()
                if result:
                    predicted_category_id = result[0]
            
            cursor.execute("""
                INSERT INTO predictions (
                    station_id, prediction_time, predicted_for,
                    model_name, predicted_aqi, predicted_category_id,
                    confidence_lower, confidence_upper,
                    model_version, features_used
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                prediction_data['station_id'],
                prediction_data.get('prediction_time', datetime.now()),
                prediction_data['predicted_for'],
                prediction_data['model_name'],
                prediction_data['predicted_aqi'],
                predicted_category_id,
                prediction_data.get('confidence_lower'),
                prediction_data.get('confidence_upper'),
                prediction_data.get('model_version', '1.0'),
                prediction_data.get('features_used')
            ))
            
            return cursor.fetchone()[0]
    
    def get_predictions(self, station_id=None, hours_ahead=24):
        """Get predictions"""
        with self.get_cursor() as cursor:
            query = """
                SELECT 
                    p.id,
                    s.station_name,
                    s.city,
                    p.predicted_for,
                    p.predicted_aqi,
                    ac.category_name AS predicted_category,
                    ac.color_code,
                    p.confidence_lower,
                    p.confidence_upper,
                    p.model_name,
                    p.prediction_time
                FROM predictions p
                JOIN stations s ON p.station_id = s.station_id
                LEFT JOIN aqi_categories ac ON p.predicted_category_id = ac.category_id
                WHERE p.predicted_for >= NOW()
                    AND p.predicted_for <= NOW() + INTERVAL '%s hours'
            """
            
            if station_id:
                query += " AND p.station_id = %s"
                query += " ORDER BY p.predicted_for ASC"
                cursor.execute(query, (hours_ahead, station_id))
            else:
                query += " ORDER BY p.predicted_for ASC"
                cursor.execute(query, (hours_ahead,))
            
            return cursor.fetchall()
    
    # ========================================================================
    # ANALYTICS
    # ========================================================================
    
    def get_city_summary(self, city):
        """Get summary statistics for a city"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                WITH latest_readings AS (
                    SELECT DISTINCT ON (s.station_id, aq.pollutant_id)
                        s.station_id,
                        s.station_name,
                        aq.pollutant_id,
                        aq.pollutant_avg,
                        aq.aqi,
                        ac.category_name,
                        aq.recorded_at
                    FROM air_quality_data aq
                    JOIN stations s ON aq.station_id = s.station_id
                    LEFT JOIN aqi_categories ac ON aq.aqi_category_id = ac.category_id
                    WHERE LOWER(s.city) = LOWER(%s)
                    ORDER BY s.station_id, aq.pollutant_id, aq.recorded_at DESC
                )
                SELECT 
                    COUNT(DISTINCT station_id) AS total_stations,
                    AVG(aqi) AS avg_aqi,
                    MAX(aqi) AS max_aqi,
                    MIN(aqi) AS min_aqi,
                    MAX(recorded_at) AS last_updated
                FROM latest_readings
            """, (city,))
            return cursor.fetchone()
    
    def get_pollutant_trends(self, pollutant_id, days=7):
        """Get pollutant trends across all stations"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    DATE(recorded_at) AS date,
                    AVG(pollutant_avg) AS avg_concentration,
                    MIN(pollutant_avg) AS min_concentration,
                    MAX(pollutant_avg) AS max_concentration,
                    COUNT(*) AS reading_count
                FROM air_quality_data
                WHERE pollutant_id = %s
                    AND recorded_at >= NOW() - INTERVAL '%s days'
                GROUP BY DATE(recorded_at)
                ORDER BY date DESC
            """, (pollutant_id, days))
            return cursor.fetchall()
    
    def get_cities_list(self):
        """Get list of all cities with data"""
        with self.get_cursor() as cursor:
            cursor.execute("""
                SELECT DISTINCT city, COUNT(*) AS station_count
                FROM stations
                WHERE is_active = TRUE
                GROUP BY city
                ORDER BY city
            """)
            return cursor.fetchall()


# Singleton instance
_db_manager = None

def get_db_manager():
    """Get singleton database manager instance"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager


if __name__ == "__main__":
    # Test database connection
    db = DatabaseManager()
    
    if db.check_connection():
        print("✅ Database connection successful!")
        
        # Initialize schema
        if db.initialize_schema():
            print("✅ Database schema initialized!")
        
        # Get statistics
        stats = db.get_statistics()
        print(f"\n📊 Database Statistics:")
        print(f"   Total Stations: {stats['total_stations']}")
        print(f"   Total Readings: {stats['total_readings']}")
        print(f"   Latest Reading: {stats['latest_reading']}")
        print(f"   Cities Covered: {stats['cities_covered']}")
    else:
        print("❌ Database connection failed!")
