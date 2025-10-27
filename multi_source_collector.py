"""
Multi-Source Air Quality Data Collector
Collects data from CPCB, OpenWeather, and IQAir APIs
Stores in unified SQLite database
"""

import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import time

load_dotenv()

class MultiSourceAirQualityCollector:
    def __init__(self, db_path='air_quality_multi.db'):
        self.cpcb_api_key = os.getenv('CPCB_API_KEY')
        self.openweather_api_key = os.getenv('OPENWEATHER_API_KEY')
        self.iqair_api_key = os.getenv('IQAIR_API_KEY')
        self.db_path = db_path
        self.db_conn = None
        self.setup_database()
    
    def setup_database(self):
        """Create SQLite database with unified schema for all sources"""
        self.db_conn = sqlite3.connect(self.db_path)
        cursor = self.db_conn.cursor()
        
        # Create stations table with source tracking
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                station_id TEXT PRIMARY KEY,
                station_name TEXT NOT NULL,
                city TEXT,
                state TEXT,
                country TEXT,
                latitude REAL,
                longitude REAL,
                data_source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create unified air quality data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS air_quality_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT,
                recorded_at TIMESTAMP NOT NULL,
                data_source TEXT,
                pollutant_id TEXT,
                pollutant_avg REAL,
                pollutant_min REAL,
                pollutant_max REAL,
                aqi REAL,
                aqi_category TEXT,
                temperature REAL,
                humidity REAL,
                pressure REAL,
                wind_speed REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_id) REFERENCES stations(station_id),
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
        
        self.db_conn.commit()
        print(f"✓ Database initialized: {self.db_path}")
    
    # ==================== CPCB DATA COLLECTION ====================
    
    def fetch_cpcb_data(self, limit=1000):
        """Fetch data from CPCB API"""
        endpoint = "https://api.data.gov.in/resource/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
        params = {
            'api-key': self.cpcb_api_key,
            'format': 'json',
            'limit': limit,
            'offset': 0
        }
        
        try:
            print("📡 Fetching CPCB data...")
            response = requests.get(endpoint, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ CPCB: Fetched {len(data.get('records', []))} records")
                return data
            else:
                print(f"✗ CPCB API error: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ CPCB fetch error: {e}")
            return None
    
    def parse_cpcb_data(self, api_data):
        """Parse and store CPCB data"""
        if not api_data or 'records' not in api_data:
            return 0, 0
        
        cursor = self.db_conn.cursor()
        stations_added = 0
        data_points_added = 0
        stations_seen = set()
        
        for record in api_data['records']:
            try:
                station_name = record.get('station', 'Unknown')
                city = record.get('city', '')
                state = record.get('state', '')
                country = record.get('country', 'India')
                latitude = record.get('latitude', '')
                longitude = record.get('longitude', '')
                
                station_id = f"CPCB_{city}_{station_name}".replace(' ', '_').replace(',', '').replace('-', '_')
                
                if station_id not in stations_seen:
                    cursor.execute("""
                        INSERT OR REPLACE INTO stations 
                        (station_id, station_name, city, state, country, latitude, longitude, data_source)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (station_id, station_name, city, state, country, latitude, longitude, 'CPCB'))
                    stations_added += 1
                    stations_seen.add(station_id)
                
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
                    try:
                        cursor.execute("""
                            INSERT OR REPLACE INTO air_quality_data 
                            (station_id, recorded_at, data_source, pollutant_id, pollutant_avg, 
                             pollutant_min, pollutant_max, aqi, aqi_category)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (station_id, recorded_at, 'CPCB', pollutant_id, 
                              float(pollutant_avg), 
                              float(pollutant_min) if pollutant_min else None,
                              float(pollutant_max) if pollutant_max else None,
                              aqi, aqi_category))
                        data_points_added += 1
                    except:
                        continue
            except Exception as e:
                continue
        
        self.db_conn.commit()
        return stations_added, data_points_added
    
    # ==================== OPENWEATHER DATA COLLECTION ====================
    
    def fetch_openweather_data(self, cities):
        """Fetch air quality data from OpenWeather API for multiple cities"""
        stations_added = 0
        data_points_added = 0
        
        print("📡 Fetching OpenWeather data...")
        
        for city_info in cities:
            try:
                lat, lon, city_name = city_info
                
                # Get air pollution data
                aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution"
                params = {
                    'lat': lat,
                    'lon': lon,
                    'appid': self.openweather_api_key
                }
                
                response = requests.get(aqi_url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Get weather data for additional parameters
                    weather_url = f"http://api.openweathermap.org/data/2.5/weather"
                    weather_response = requests.get(weather_url, params=params, timeout=10)
                    weather_data = weather_response.json() if weather_response.status_code == 200 else {}
                    
                    s, d = self.parse_openweather_data(data, weather_data, city_name, lat, lon)
                    stations_added += s
                    data_points_added += d
                    
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ Error fetching {city_name}: {e}")
                continue
        
        print(f"✓ OpenWeather: {stations_added} stations, {data_points_added} data points")
        return stations_added, data_points_added
    
    def parse_openweather_data(self, aqi_data, weather_data, city_name, lat, lon):
        """Parse and store OpenWeather data"""
        if not aqi_data or 'list' not in aqi_data:
            return 0, 0
        
        cursor = self.db_conn.cursor()
        station_id = f"OW_{city_name}".replace(' ', '_')
        
        # Insert station
        cursor.execute("""
            INSERT OR REPLACE INTO stations 
            (station_id, station_name, city, country, latitude, longitude, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (station_id, f"OpenWeather_{city_name}", city_name, 'India', lat, lon, 'OpenWeather'))
        
        data_points = 0
        
        for item in aqi_data['list']:
            try:
                recorded_at = datetime.fromtimestamp(item['dt'])
                aqi = item['main']['aqi']
                components = item['components']
                
                # Extract weather parameters
                temp = weather_data.get('main', {}).get('temp')
                humidity = weather_data.get('main', {}).get('humidity')
                pressure = weather_data.get('main', {}).get('pressure')
                wind_speed = weather_data.get('wind', {}).get('speed')
                
                # Map OpenWeather pollutants
                pollutants = {
                    'PM2.5': components.get('pm2_5'),
                    'PM10': components.get('pm10'),
                    'NO2': components.get('no2'),
                    'SO2': components.get('so2'),
                    'CO': components.get('co'),
                    'O3': components.get('o3'),
                    'NH3': components.get('nh3')
                }
                
                aqi_category = self.get_aqi_category(aqi * 50)  # OpenWeather AQI is 1-5
                
                for pollutant_id, value in pollutants.items():
                    if value is not None:
                        cursor.execute("""
                            INSERT OR REPLACE INTO air_quality_data 
                            (station_id, recorded_at, data_source, pollutant_id, pollutant_avg, 
                             aqi, aqi_category, temperature, humidity, pressure, wind_speed)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (station_id, recorded_at, 'OpenWeather', pollutant_id, value,
                              aqi * 50, aqi_category, temp, humidity, pressure, wind_speed))
                        data_points += 1
            except Exception as e:
                continue
        
        self.db_conn.commit()
        return 1, data_points
    
    # ==================== IQAIR DATA COLLECTION ====================
    
    def fetch_iqair_data(self, cities):
        """Fetch air quality data from IQAir API"""
        stations_added = 0
        data_points_added = 0
        
        print("📡 Fetching IQAir data...")
        
        for city_name in cities:
            try:
                url = f"http://api.airvisual.com/v2/city"
                params = {
                    'city': city_name,
                    'state': '',
                    'country': 'India',
                    'key': self.iqair_api_key
                }
                
                response = requests.get(url, params=params, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('status') == 'success':
                        s, d = self.parse_iqair_data(data, city_name)
                        stations_added += s
                        data_points_added += d
                else:
                    print(f"  ✗ IQAir {city_name}: Status {response.status_code}")
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"  ✗ Error fetching {city_name}: {e}")
                continue
        
        print(f"✓ IQAir: {stations_added} stations, {data_points_added} data points")
        return stations_added, data_points_added
    
    def parse_iqair_data(self, data, city_name):
        """Parse and store IQAir data"""
        if data.get('status') != 'success':
            return 0, 0
        
        cursor = self.db_conn.cursor()
        
        try:
            city_data = data['data']['city']
            location = data['data']['location']
            current = data['data']['current']
            
            station_id = f"IQAIR_{city_name}".replace(' ', '_')
            
            # Insert station
            cursor.execute("""
                INSERT OR REPLACE INTO stations 
                (station_id, station_name, city, country, latitude, longitude, data_source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (station_id, f"IQAir_{city_name}", city_name, 
                  location['coordinates'][1], location['coordinates'][0], 
                  location['coordinates'][1], 'IQAir'))
            
            # Parse timestamp
            recorded_at = datetime.fromisoformat(current['pollution']['ts'].replace('Z', '+00:00'))
            
            # Extract pollution data
            pollution = current['pollution']
            aqi = pollution.get('aqius')  # US AQI
            main_pollutant = pollution.get('mainus')
            
            # Extract weather data
            weather = current.get('weather', {})
            temp = weather.get('tp')
            humidity = weather.get('hu')
            pressure = weather.get('pr')
            wind_speed = weather.get('ws')
            
            aqi_category = self.get_aqi_category(aqi)
            
            # Store main pollutant data
            if main_pollutant:
                cursor.execute("""
                    INSERT OR REPLACE INTO air_quality_data 
                    (station_id, recorded_at, data_source, pollutant_id, pollutant_avg, 
                     aqi, aqi_category, temperature, humidity, pressure, wind_speed)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (station_id, recorded_at, 'IQAir', main_pollutant, aqi,
                      aqi, aqi_category, temp, humidity, pressure, wind_speed))
                
                self.db_conn.commit()
                return 1, 1
        except Exception as e:
            print(f"  ✗ Parse error for {city_name}: {e}")
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
    
    def get_statistics(self):
        """Get database statistics"""
        cursor = self.db_conn.cursor()
        
        cursor.execute("""
            SELECT data_source, COUNT(DISTINCT station_id) as stations, COUNT(*) as data_points
            FROM air_quality_data
            GROUP BY data_source
        """)
        source_stats = cursor.fetchall()
        
        cursor.execute("SELECT COUNT(*) FROM stations")
        total_stations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM air_quality_data")
        total_data = cursor.fetchone()[0]
        
        return {
            'total_stations': total_stations,
            'total_data_points': total_data,
            'by_source': source_stats
        }
    
    def collect_all_data(self):
        """Collect data from all sources"""
        print("="*70)
        print("Multi-Source Air Quality Data Collection")
        print("="*70)
        print()
        
        total_stations = 0
        total_data = 0
        
        # Collect CPCB data
        cpcb_data = self.fetch_cpcb_data(1000)
        if cpcb_data:
            s, d = self.parse_cpcb_data(cpcb_data)
            print(f"  ✓ CPCB: {s} stations, {d} data points")
            total_stations += s
            total_data += d
        
        print()
        
        # Major Indian cities for OpenWeather (lat, lon, name)
        cities_openweather = [
            (28.6139, 77.2090, 'Delhi'),
            (19.0760, 72.8777, 'Mumbai'),
            (12.9716, 77.5946, 'Bangalore'),
            (13.0827, 80.2707, 'Chennai'),
            (22.5726, 88.3639, 'Kolkata'),
            (17.3850, 78.4867, 'Hyderabad'),
            (23.0225, 72.5714, 'Ahmedabad'),
            (18.5204, 73.8567, 'Pune'),
            (26.9124, 75.7873, 'Jaipur'),
            (28.4595, 77.0266, 'Gurgaon')
        ]
        
        s, d = self.fetch_openweather_data(cities_openweather)
        total_stations += s
        total_data += d
        
        print()
        
        # Major Indian cities for IQAir
        cities_iqair = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 
                        'Hyderabad', 'Ahmedabad', 'Pune', 'Jaipur', 'Lucknow']
        
        s, d = self.fetch_iqair_data(cities_iqair)
        total_stations += s
        total_data += d
        
        return total_stations, total_data
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()

if __name__ == "__main__":
    collector = MultiSourceAirQualityCollector()
    
    try:
        total_s, total_d = collector.collect_all_data()
        
        print("\n" + "="*70)
        print("Collection Summary")
        print("="*70)
        
        stats = collector.get_statistics()
        print(f"Total Stations: {stats['total_stations']}")
        print(f"Total Data Points: {stats['total_data_points']}")
        print(f"\nBy Data Source:")
        for source, stations, data_points in stats['by_source']:
            print(f"  {source}: {stations} stations, {data_points} data points")
        
        print("="*70)
        print(f"\n✓ Data saved to: {collector.db_path}")
        
    except KeyboardInterrupt:
        print("\n\nProcess interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        collector.close()
