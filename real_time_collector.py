"""
Real-Time Multi-Source Data Collector
Fetches data from CPCB, OpenWeather, and IQAir APIs
Stores in PostgreSQL for ML training and predictions
"""

import os
import requests
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, timedelta
import logging
import time
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiSourceDataCollector:
    """Collects air quality data from multiple public APIs"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.iqair_api_key = os.getenv('IQAIR_API_KEY')
        self.cpcb_api_key = os.getenv('CPCB_API_KEY')
        
        # Indian cities with coordinates
        self.cities = {
            'Delhi': {'lat': 28.7041, 'lon': 77.1025},
            'Mumbai': {'lat': 19.0760, 'lon': 72.8777},
            'Bangalore': {'lat': 12.9716, 'lon': 77.5946},
            'Chennai': {'lat': 13.0827, 'lon': 80.2707},
            'Kolkata': {'lat': 22.5726, 'lon': 88.3639},
            'Hyderabad': {'lat': 17.3850, 'lon': 78.4867},
            'Pune': {'lat': 18.5204, 'lon': 73.8567},
            'Ahmedabad': {'lat': 23.0225, 'lon': 72.5714},
            'Jaipur': {'lat': 26.9124, 'lon': 75.7873},
            'Lucknow': {'lat': 26.8467, 'lon': 80.9462}
        }
    
    def get_db_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.db_url)
    
    def fetch_openweather_data(self, city, lat, lon):
        """Fetch air pollution data from OpenWeather API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.openweather_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if 'list' in data and len(data['list']) > 0:
                pollution = data['list'][0]
                components = pollution['components']
                
                return {
                    'source': 'openweather',
                    'city': city,
                    'latitude': lat,
                    'longitude': lon,
                    'aqi': pollution['main']['aqi'],
                    'pm25': components.get('pm2_5'),
                    'pm10': components.get('pm10'),
                    'no2': components.get('no2'),
                    'so2': components.get('so2'),
                    'co': components.get('co'),
                    'o3': components.get('o3'),
                    'nh3': components.get('nh3'),
                    'timestamp': datetime.utcfromtimestamp(pollution['dt'])
                }
            
            return None
            
        except Exception as e:
            logger.error(f"OpenWeather API error for {city}: {e}")
            return None
    
    def fetch_iqair_data(self, city, lat, lon):
        """Fetch air quality data from IQAir API"""
        try:
            url = "http://api.airvisual.com/v2/nearest_city"
            params = {
                'lat': lat,
                'lon': lon,
                'key': self.iqair_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] == 'success':
                current = data['data']['current']['pollution']
                
                return {
                    'source': 'iqair',
                    'city': city,
                    'latitude': lat,
                    'longitude': lon,
                    'aqi': current['aqius'],
                    'pm25': current.get('p2', {}).get('conc'),
                    'timestamp': datetime.strptime(current['ts'], '%Y-%m-%dT%H:%M:%S.%fZ')
                }
            
            return None
            
        except Exception as e:
            logger.error(f"IQAir API error for {city}: {e}")
            return None
    
    def fetch_cpcb_data(self, city):
        """Fetch data from CPCB (Central Pollution Control Board)"""
        try:
            # CPCB API endpoint (you'll need to register for actual API key)
            url = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
            params = {
                'api-key': self.cpcb_api_key,
                'format': 'json',
                'filters[city]': city,
                'limit': 1
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if 'records' in data and len(data['records']) > 0:
                record = data['records'][0]
                
                return {
                    'source': 'cpcb',
                    'city': city,
                    'station_name': record.get('station'),
                    'pm25': float(record.get('pm2_5', 0)) if record.get('pm2_5') else None,
                    'pm10': float(record.get('pm10', 0)) if record.get('pm10') else None,
                    'no2': float(record.get('no2', 0)) if record.get('no2') else None,
                    'so2': float(record.get('so2', 0)) if record.get('so2') else None,
                    'co': float(record.get('co', 0)) if record.get('co') else None,
                    'o3': float(record.get('o3', 0)) if record.get('o3') else None,
                    'timestamp': datetime.now()
                }
            
            return None
            
        except Exception as e:
            logger.error(f"CPCB API error for {city}: {e}")
            return None
    
    def calculate_aqi(self, pm25, pm10):
        """Calculate AQI from PM2.5 and PM10 values"""
        if pm25 is None:
            return None
        
        # Simplified AQI calculation based on PM2.5
        if pm25 <= 12:
            return int((50 / 12) * pm25)
        elif pm25 <= 35.4:
            return int(50 + ((100 - 50) / (35.4 - 12.1)) * (pm25 - 12.1))
        elif pm25 <= 55.4:
            return int(100 + ((150 - 100) / (55.4 - 35.5)) * (pm25 - 35.5))
        elif pm25 <= 150.4:
            return int(150 + ((200 - 150) / (150.4 - 55.5)) * (pm25 - 55.5))
        elif pm25 <= 250.4:
            return int(200 + ((300 - 200) / (250.4 - 150.5)) * (pm25 - 150.5))
        else:
            return int(300 + ((500 - 300) / (500 - 250.5)) * (pm25 - 250.5))
    
    def store_data(self, data_records):
        """Store collected data in PostgreSQL"""
        if not data_records:
            return
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO raw_air_quality_data 
                (source, city, station_name, latitude, longitude, 
                 pm25, pm10, no2, so2, co, o3, nh3, aqi, timestamp)
                VALUES %s
                ON CONFLICT DO NOTHING
            """
            
            values = [
                (
                    record.get('source'),
                    record.get('city'),
                    record.get('station_name'),
                    record.get('latitude'),
                    record.get('longitude'),
                    record.get('pm25'),
                    record.get('pm10'),
                    record.get('no2'),
                    record.get('so2'),
                    record.get('co'),
                    record.get('o3'),
                    record.get('nh3'),
                    record.get('aqi') or self.calculate_aqi(record.get('pm25'), record.get('pm10')),
                    record.get('timestamp')
                )
                for record in data_records
            ]
            
            execute_values(cursor, insert_query, values)
            conn.commit()
            
            logger.info(f"Stored {len(values)} records in database")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    def collect_all_sources(self):
        """Collect data from all sources for all cities"""
        all_data = []
        
        for city, coords in self.cities.items():
            logger.info(f"Collecting data for {city}...")
            
            # Fetch from OpenWeather
            if self.openweather_api_key:
                ow_data = self.fetch_openweather_data(city, coords['lat'], coords['lon'])
                if ow_data:
                    all_data.append(ow_data)
                    logger.info(f"  ✓ OpenWeather: AQI={ow_data.get('aqi')}, PM2.5={ow_data.get('pm25')}")
            
            # Fetch from IQAir
            if self.iqair_api_key:
                iq_data = self.fetch_iqair_data(city, coords['lat'], coords['lon'])
                if iq_data:
                    all_data.append(iq_data)
                    logger.info(f"  ✓ IQAir: AQI={iq_data.get('aqi')}, PM2.5={iq_data.get('pm25')}")
            
            # Fetch from CPCB
            if self.cpcb_api_key:
                cpcb_data = self.fetch_cpcb_data(city)
                if cpcb_data:
                    all_data.append(cpcb_data)
                    logger.info(f"  ✓ CPCB: PM2.5={cpcb_data.get('pm25')}, PM10={cpcb_data.get('pm10')}")
            
            # Rate limiting
            time.sleep(1)
        
        return all_data
    
    def run_hourly_collection(self):
        """Run data collection every hour"""
        logger.info("Starting hourly data collection...")
        
        while True:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Collection started at {datetime.now()}")
                logger.info(f"{'='*60}")
                
                # Collect from all sources
                data = self.collect_all_sources()
                
                # Store in database
                self.store_data(data)
                
                logger.info(f"\n{'='*60}")
                logger.info(f"Collection completed. Total records: {len(data)}")
                logger.info(f"Next collection in 1 hour...")
                logger.info(f"{'='*60}\n")
                
                # Wait 1 hour
                time.sleep(3600)
                
            except KeyboardInterrupt:
                logger.info("Collection stopped by user")
                break
            except Exception as e:
                logger.error(f"Collection error: {e}")
                logger.info("Retrying in 5 minutes...")
                time.sleep(300)


if __name__ == "__main__":
    collector = MultiSourceDataCollector()
    
    logger.info("\n" + "="*70)
    logger.info("REAL-TIME AIR QUALITY DATA COLLECTOR")
    logger.info("="*70)
    logger.info("Running single data collection cycle...")
    logger.info("="*70 + "\n")
    
    # Run once for testing
    data = collector.collect_all_sources()
    collector.store_data(data)
    
    logger.info(f"\n✓ Successfully collected {len(data)} records from all sources!")
    logger.info("\n" + "="*70)
    logger.info("To run continuous hourly collection, use:")
    logger.info("  python automated_scheduler.py")
    logger.info("="*70 + "\n")
