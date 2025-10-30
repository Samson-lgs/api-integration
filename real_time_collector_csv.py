"""
Real-Time Air Quality Data Collector (CSV Version)
Collects data from OpenWeather, IQAir, and CPCB APIs
Saves to CSV file instead of database
"""

import os
import requests
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MultiSourceDataCollector:
    """Collects air quality data from multiple sources and saves to CSV"""
    
    def __init__(self):
        self.openweather_key = os.getenv('OPENWEATHER_API_KEY')
        self.iqair_key = os.getenv('IQAIR_API_KEY')
        self.cpcb_key = os.getenv('CPCB_API_KEY')
        
        self.cities = [
            {'name': 'Delhi', 'lat': 28.7041, 'lon': 77.1025},
            {'name': 'Mumbai', 'lat': 19.0760, 'lon': 72.8777},
            {'name': 'Bangalore', 'lat': 12.9716, 'lon': 77.5946},
            {'name': 'Chennai', 'lat': 13.0827, 'lon': 80.2707},
            {'name': 'Kolkata', 'lat': 22.5726, 'lon': 88.3639},
            {'name': 'Hyderabad', 'lat': 17.3850, 'lon': 78.4867},
            {'name': 'Pune', 'lat': 18.5204, 'lon': 73.8567},
            {'name': 'Ahmedabad', 'lat': 23.0225, 'lon': 72.5714},
            {'name': 'Jaipur', 'lat': 26.9124, 'lon': 75.7873},
            {'name': 'Lucknow', 'lat': 26.8467, 'lon': 80.9462}
        ]
    
    def fetch_openweather_data(self, city, lat, lon):
        """Fetch data from OpenWeather Air Pollution API"""
        try:
            url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={self.openweather_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pollution = data['list'][0]
            
            record = {
                'source': 'openweather',
                'city': city,
                'station_name': f'{city} (OpenWeather)',
                'latitude': lat,
                'longitude': lon,
                'pm25': pollution['components'].get('pm2_5'),
                'pm10': pollution['components'].get('pm10'),
                'no2': pollution['components'].get('no2'),
                'so2': pollution['components'].get('so2'),
                'co': pollution['components'].get('co'),
                'o3': pollution['components'].get('o3'),
                'nh3': pollution['components'].get('nh3'),
                'aqi': pollution['main']['aqi'],
                'timestamp': datetime.now()
            }
            
            logger.info(f"  ✓ OpenWeather: AQI={record['aqi']}, PM2.5={record['pm25']}")
            return record
            
        except Exception as e:
            logger.error(f"OpenWeather API error for {city}: {e}")
            return None
    
    def fetch_iqair_data(self, city, lat, lon):
        """Fetch data from IQAir API"""
        try:
            url = f"http://api.airvisual.com/v2/nearest_city?lat={lat}&lon={lon}&key={self.iqair_key}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pollution = data['data']['current']['pollution']
            
            record = {
                'source': 'iqair',
                'city': city,
                'station_name': f'{city} (IQAir)',
                'latitude': lat,
                'longitude': lon,
                'pm25': pollution.get('p2', {}).get('conc') if isinstance(pollution.get('p2'), dict) else None,
                'pm10': pollution.get('p1', {}).get('conc') if isinstance(pollution.get('p1'), dict) else None,
                'no2': None,
                'so2': None,
                'co': None,
                'o3': None,
                'nh3': None,
                'aqi': pollution.get('aqius'),
                'timestamp': datetime.now()
            }
            
            logger.info(f"  ✓ IQAir: AQI={record['aqi']}, PM2.5={record['pm25']}")
            return record
            
        except Exception as e:
            logger.error(f"IQAir API error for {city}: {e}")
            return None
    
    def collect_all_sources(self):
        """Collect data from all sources for all cities"""
        all_records = []
        
        for city_info in self.cities:
            city = city_info['name']
            lat = city_info['lat']
            lon = city_info['lon']
            
            logger.info(f"Collecting data for {city}...")
            
            # OpenWeather
            record = self.fetch_openweather_data(city, lat, lon)
            if record:
                all_records.append(record)
            
            # IQAir
            record = self.fetch_iqair_data(city, lat, lon)
            if record:
                all_records.append(record)
        
        return all_records
    
    def save_to_csv(self, records, filename='air_quality_data.csv'):
        """Save records to CSV file"""
        if not records:
            logger.warning("No records to save")
            return
        
        df = pd.DataFrame(records)
        
        # Append to existing file or create new
        if os.path.exists(filename):
            existing_df = pd.read_csv(filename)
            df = pd.concat([existing_df, df], ignore_index=True)
        
        df.to_csv(filename, index=False)
        logger.info(f"✓ Saved {len(records)} records to {filename}")


if __name__ == "__main__":
    collector = MultiSourceDataCollector()
    
    logger.info("\n" + "="*70)
    logger.info("REAL-TIME AIR QUALITY DATA COLLECTOR (CSV MODE)")
    logger.info("="*70)
    logger.info("Collecting data from OpenWeather and IQAir APIs...")
    logger.info("="*70 + "\n")
    
    # Collect data
    data = collector.collect_all_sources()
    
    # Save to CSV
    collector.save_to_csv(data)
    
    logger.info(f"\n✓ Successfully collected {len(data)} records from all sources!")
    logger.info("✓ Data saved to: air_quality_data.csv")
    logger.info("\nTo view the data:")
    logger.info("  python -c \"import pandas as pd; print(pd.read_csv('air_quality_data.csv'))\"")
    logger.info("\n" + "="*70 + "\n")
