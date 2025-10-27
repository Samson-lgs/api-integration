"""
Cloud-based Multi-Source Air Quality Data Collector for Render
Automatically fetches data from CPCB, OpenWeather, and IQAir APIs
Stores in PostgreSQL database
"""

import requests
import psycopg2
from psycopg2.extras import execute_values
import os
from datetime import datetime
import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CloudAirQualityCollector:
    def __init__(self):
        # Get credentials from environment variables
        self.cpcb_api_key = os.getenv('CPCB_API_KEY')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.iqair_api_key = os.getenv('IQAIR_API_KEY')
        
        # PostgreSQL connection from Render environment variable
        self.database_url = os.getenv('DATABASE_URL')
        
        self.db_conn = None
        self.setup_database()
    
    def get_db_connection(self):
        """Create PostgreSQL connection"""
        try:
            self.db_conn = psycopg2.connect(self.database_url)
            logger.info("✓ Connected to PostgreSQL")
            return self.db_conn
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            return None
    
    def setup_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = self.get_db_connection()
            if not conn:
                return False
            
            cursor = conn.cursor()
            
            # Create stations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stations (
                    station_id VARCHAR(255) PRIMARY KEY,
                    station_name VARCHAR(500) NOT NULL,
                    city VARCHAR(200),
                    state VARCHAR(200),
                    country VARCHAR(100),
                    latitude DECIMAL(10, 8),
                    longitude DECIMAL(11, 8),
                    data_source VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create air quality data table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS air_quality_data (
                    id SERIAL PRIMARY KEY,
                    station_id VARCHAR(255) REFERENCES stations(station_id),
                    recorded_at TIMESTAMP NOT NULL,
                    data_source VARCHAR(50),
                    pollutant_id VARCHAR(50),
                    pollutant_avg DECIMAL(10, 4),
                    pollutant_min DECIMAL(10, 4),
                    pollutant_max DECIMAL(10, 4),
                    aqi DECIMAL(10, 2),
                    aqi_category VARCHAR(50),
                    temperature DECIMAL(10, 2),
                    humidity DECIMAL(10, 2),
                    pressure DECIMAL(10, 2),
                    wind_speed DECIMAL(10, 2),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(station_id, recorded_at, pollutant_id, data_source)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_station_recorded 
                ON air_quality_data(station_id, recorded_at)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_data_source 
                ON air_quality_data(data_source)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_city 
                ON stations(city)
            """)
            
            conn.commit()
            cursor.close()
            logger.info("✓ Database tables created/verified")
            return True
            
        except Exception as e:
            logger.error(f"Database setup error: {e}")
            return False
    
    # ==================== CPCB DATA COLLECTION ====================
    
    def fetch_cpcb_data(self, limit=1000):
        """Fetch data from CPCB API"""
        try:
            endpoint = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
            params = {
                'api-key': self.cpcb_api_key,
                'format': 'json',
                'limit': limit,
                'offset': 0
            }
            
            logger.info("📡 Fetching CPCB data...")
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✓ CPCB: Fetched {len(data.get('records', []))} records")
                return data
            else:
                logger.error(f"CPCB API error: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"CPCB fetch error: {e}")
            return None
    
    def store_cpcb_data(self, api_data):
        """Parse and store CPCB data in PostgreSQL"""
        if not api_data or 'records' not in api_data:
            return 0, 0
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            stations_added = 0
            data_points_added = 0
            
            for record in api_data['records']:
                try:
                    station_name = record.get('station', 'Unknown')
                    city = record.get('city', '')
                    state = record.get('state', '')
                    country = record.get('country', 'India')
                    latitude = record.get('latitude', 0)
                    longitude = record.get('longitude', 0)
                    
                    station_id = f"CPCB_{city}_{station_name}".replace(' ', '_').replace(',', '').replace('-', '_')[:255]
                    
                    # Insert or update station
                    cursor.execute("""
                        INSERT INTO stations 
                        (station_id, station_name, city, state, country, latitude, longitude, data_source)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (station_id) DO UPDATE
                        SET station_name = EXCLUDED.station_name,
                            updated_at = CURRENT_TIMESTAMP
                    """, (station_id, station_name, city, state, country, latitude, longitude, 'CPCB'))
                    stations_added += 1
                    
                    # Parse timestamp
                    last_update = record.get('last_update', '')
                    try:
                        recorded_at = datetime.strptime(last_update, "%d-%m-%Y %H:%M:%S")
                    except:
                        recorded_at = datetime.now()
                    
                    pollutant_id = record.get('pollutant_id', '')
                    pollutant_avg = record.get('avg_value', '')
                    pollutant_min = record.get('min_value', '')
                    pollutant_max = record.get('max_value', '')
                    
                    aqi = self.calculate_aqi(pollutant_id, pollutant_avg)
                    aqi_category = self.get_aqi_category(aqi)
                    
                    if pollutant_id and pollutant_avg:
                        cursor.execute("""
                            INSERT INTO air_quality_data 
                            (station_id, recorded_at, data_source, pollutant_id, pollutant_avg, 
                             pollutant_min, pollutant_max, aqi, aqi_category)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (station_id, recorded_at, pollutant_id, data_source) DO NOTHING
                        """, (station_id, recorded_at, 'CPCB', pollutant_id, 
                              float(pollutant_avg), 
                              float(pollutant_min) if pollutant_min else None,
                              float(pollutant_max) if pollutant_max else None,
                              aqi, aqi_category))
                        data_points_added += 1
                        
                except Exception as e:
                    logger.warning(f"Error processing CPCB record: {e}")
                    continue
            
            conn.commit()
            cursor.close()
            logger.info(f"✓ CPCB: {stations_added} stations, {data_points_added} data points")
            return stations_added, data_points_added
            
        except Exception as e:
            logger.error(f"CPCB storage error: {e}")
            return 0, 0
    
    # ==================== OPENWEATHER DATA COLLECTION ====================
    
    def fetch_openweather_data(self):
        """Fetch air quality data from OpenWeather API"""
        cities = [
            (28.6139, 77.2090, 'Delhi'),
            (19.0760, 72.8777, 'Mumbai'),
            (12.9716, 77.5946, 'Bangalore'),
            (13.0827, 80.2707, 'Chennai'),
            (22.5726, 88.3639, 'Kolkata'),
            (17.3850, 78.4867, 'Hyderabad'),
            (23.0225, 72.5714, 'Ahmedabad'),
            (18.5204, 73.8567, 'Pune'),
            (26.9124, 75.7873, 'Jaipur'),
            (28.4595, 77.0266, 'Gurgaon'),
            (26.8467, 80.9462, 'Lucknow'),
            (21.1702, 72.8311, 'Surat'),
            (11.0168, 76.9558, 'Coimbatore'),
            (30.7333, 76.7794, 'Chandigarh'),
            (25.5941, 85.1376, 'Patna')
        ]
        
        stations_added = 0
        data_points_added = 0
        
        logger.info("📡 Fetching OpenWeather data...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            for lat, lon, city_name in cities:
                try:
                    # Get air pollution data
                    aqi_url = "http://api.openweathermap.org/data/2.5/air_pollution"
                    params = {'lat': lat, 'lon': lon, 'appid': self.openweather_api_key}
                    
                    response = requests.get(aqi_url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Get weather data
                        weather_url = "http://api.openweathermap.org/data/2.5/weather"
                        weather_response = requests.get(weather_url, params=params, timeout=10)
                        weather_data = weather_response.json() if weather_response.status_code == 200 else {}
                        
                        s, d = self.store_openweather_data(cursor, data, weather_data, city_name, lat, lon)
                        stations_added += s
                        data_points_added += d
                    
                    time.sleep(0.5)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching OpenWeather for {city_name}: {e}")
                    continue
            
            conn.commit()
            cursor.close()
            logger.info(f"✓ OpenWeather: {stations_added} stations, {data_points_added} data points")
            return stations_added, data_points_added
            
        except Exception as e:
            logger.error(f"OpenWeather error: {e}")
            return 0, 0
    
    def store_openweather_data(self, cursor, aqi_data, weather_data, city_name, lat, lon):
        """Store OpenWeather data in PostgreSQL"""
        if not aqi_data or 'list' not in aqi_data:
            return 0, 0
        
        station_id = f"OW_{city_name}".replace(' ', '_')
        
        # Insert station
        cursor.execute("""
            INSERT INTO stations 
            (station_id, station_name, city, country, latitude, longitude, data_source)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (station_id) DO UPDATE
            SET updated_at = CURRENT_TIMESTAMP
        """, (station_id, f"OpenWeather_{city_name}", city_name, 'India', lat, lon, 'OpenWeather'))
        
        data_points = 0
        
        for item in aqi_data['list']:
            try:
                recorded_at = datetime.fromtimestamp(item['dt'])
                aqi = item['main']['aqi']
                components = item['components']
                
                temp = weather_data.get('main', {}).get('temp')
                humidity = weather_data.get('main', {}).get('humidity')
                pressure = weather_data.get('main', {}).get('pressure')
                wind_speed = weather_data.get('wind', {}).get('speed')
                
                pollutants = {
                    'PM2.5': components.get('pm2_5'),
                    'PM10': components.get('pm10'),
                    'NO2': components.get('no2'),
                    'SO2': components.get('so2'),
                    'CO': components.get('co'),
                    'O3': components.get('o3'),
                    'NH3': components.get('nh3')
                }
                
                aqi_category = self.get_aqi_category(aqi * 50)
                
                for pollutant_id, value in pollutants.items():
                    if value is not None:
                        cursor.execute("""
                            INSERT INTO air_quality_data 
                            (station_id, recorded_at, data_source, pollutant_id, pollutant_avg, 
                             aqi, aqi_category, temperature, humidity, pressure, wind_speed)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (station_id, recorded_at, pollutant_id, data_source) DO NOTHING
                        """, (station_id, recorded_at, 'OpenWeather', pollutant_id, value,
                              aqi * 50, aqi_category, temp, humidity, pressure, wind_speed))
                        data_points += 1
            except Exception as e:
                continue
        
        return 1, data_points
    
    # ==================== IQAIR DATA COLLECTION ====================
    
    def fetch_iqair_data(self):
        """Fetch air quality data from IQAir API"""
        cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 
                  'Hyderabad', 'Ahmedabad', 'Pune', 'Jaipur', 'Lucknow']
        
        stations_added = 0
        data_points_added = 0
        
        logger.info("📡 Fetching IQAir data...")
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            for city_name in cities:
                try:
                    url = "http://api.airvisual.com/v2/city"
                    params = {
                        'city': city_name,
                        'country': 'India',
                        'key': self.iqair_api_key
                    }
                    
                    response = requests.get(url, params=params, timeout=10)
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('status') == 'success':
                            s, d = self.store_iqair_data(cursor, data, city_name)
                            stations_added += s
                            data_points_added += d
                    
                    time.sleep(1)  # Rate limiting
                    
                except Exception as e:
                    logger.warning(f"Error fetching IQAir for {city_name}: {e}")
                    continue
            
            conn.commit()
            cursor.close()
            logger.info(f"✓ IQAir: {stations_added} stations, {data_points_added} data points")
            return stations_added, data_points_added
            
        except Exception as e:
            logger.error(f"IQAir error: {e}")
            return 0, 0
    
    def store_iqair_data(self, cursor, data, city_name):
        """Store IQAir data in PostgreSQL"""
        if data.get('status') != 'success':
            return 0, 0
        
        try:
            location = data['data']['location']
            current = data['data']['current']
            
            station_id = f"IQAIR_{city_name}".replace(' ', '_')
            
            cursor.execute("""
                INSERT INTO stations 
                (station_id, station_name, city, country, latitude, longitude, data_source)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (station_id) DO UPDATE
                SET updated_at = CURRENT_TIMESTAMP
            """, (station_id, f"IQAir_{city_name}", city_name, 'India',
                  location['coordinates'][1], location['coordinates'][0], 'IQAir'))
            
            recorded_at = datetime.fromisoformat(current['pollution']['ts'].replace('Z', '+00:00'))
            
            pollution = current['pollution']
            aqi = pollution.get('aqius')
            main_pollutant = pollution.get('mainus')
            
            weather = current.get('weather', {})
            temp = weather.get('tp')
            humidity = weather.get('hu')
            pressure = weather.get('pr')
            wind_speed = weather.get('ws')
            
            aqi_category = self.get_aqi_category(aqi)
            
            if main_pollutant:
                cursor.execute("""
                    INSERT INTO air_quality_data 
                    (station_id, recorded_at, data_source, pollutant_id, pollutant_avg, 
                     aqi, aqi_category, temperature, humidity, pressure, wind_speed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (station_id, recorded_at, pollutant_id, data_source) DO NOTHING
                """, (station_id, recorded_at, 'IQAir', main_pollutant, aqi,
                      aqi, aqi_category, temp, humidity, pressure, wind_speed))
                
                return 1, 1
        except Exception as e:
            logger.warning(f"Error storing IQAir data for {city_name}: {e}")
            return 0, 0
        
        return 0, 0
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def calculate_aqi(self, pollutant_id, value):
        """Calculate AQI based on pollutant concentration"""
        if not value:
            return None
        
        try:
            val = float(value)
            
            if pollutant_id == 'PM2.5':
                if val <= 30:
                    return val * 50 / 30
                elif val <= 60:
                    return 50 + (val - 30) * 50 / 30
                elif val <= 90:
                    return 100 + (val - 60) * 100 / 30
                elif val <= 120:
                    return 200 + (val - 90) * 100 / 30
                elif val <= 250:
                    return 300 + (val - 120) * 100 / 130
                else:
                    return 400 + (val - 250) * 100 / 130
            
            elif pollutant_id == 'PM10':
                if val <= 50:
                    return val
                elif val <= 100:
                    return 50 + (val - 50)
                elif val <= 250:
                    return 100 + (val - 100) * 100 / 150
                elif val <= 350:
                    return 200 + (val - 250)
                elif val <= 430:
                    return 300 + (val - 350) * 100 / 80
                else:
                    return 400 + (val - 430) * 100 / 80
            else:
                return min(500, val * 2)
        except:
            return None
    
    def get_aqi_category(self, aqi):
        """Determine AQI category based on value"""
        if aqi is None:
            return 'Unknown'
        
        try:
            aqi_value = float(aqi)
            if aqi_value <= 50:
                return 'Good'
            elif aqi_value <= 100:
                return 'Satisfactory'
            elif aqi_value <= 200:
                return 'Moderate'
            elif aqi_value <= 300:
                return 'Poor'
            elif aqi_value <= 400:
                return 'Very Poor'
            else:
                return 'Severe'
        except:
            return 'Unknown'
    
    def collect_all_data(self):
        """Collect data from all sources"""
        logger.info("="*70)
        logger.info("Starting Multi-Source Data Collection")
        logger.info("="*70)
        
        total_stations = 0
        total_data = 0
        
        # Collect CPCB data
        cpcb_data = self.fetch_cpcb_data(1000)
        if cpcb_data:
            s, d = self.store_cpcb_data(cpcb_data)
            total_stations += s
            total_data += d
        
        # Collect OpenWeather data
        s, d = self.fetch_openweather_data()
        total_stations += s
        total_data += d
        
        # Collect IQAir data
        s, d = self.fetch_iqair_data()
        total_stations += s
        total_data += d
        
        logger.info("="*70)
        logger.info(f"Collection Complete: {total_stations} stations, {total_data} data points")
        logger.info("="*70)
        
        return total_stations, total_data
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            logger.info("Database connection closed")

def main():
    """Main function for scheduled execution"""
    collector = CloudAirQualityCollector()
    
    try:
        collector.collect_all_data()
    except Exception as e:
        logger.error(f"Collection error: {e}")
    finally:
        collector.close()

if __name__ == "__main__":
    main()
