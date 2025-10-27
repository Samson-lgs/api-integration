"""
CPCB Air Quality Data Collector
Fetches air quality data from CPCB API and stores in PostgreSQL
"""

import requests
import psycopg2
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import json
import time

load_dotenv()

class CPCBDataCollector:
    def __init__(self):
        self.api_key = os.getenv('CPCB_API_KEY')
        self.base_url = "https://api.data.gov.in/resource"
        self.db_conn = None
        self.connect_database()
    
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.db_conn = psycopg2.connect(
                host=os.getenv('DB_HOST'),
                port=os.getenv('DB_PORT'),
                database=os.getenv('DB_NAME'),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD')
            )
            print("Connected to PostgreSQL database")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.db_conn = None
    
    def fetch_realtime_data(self, limit=1000):
        """
        Fetch real-time air quality data from CPCB API
        API endpoint for real-time AQI data
        """
        # CPCB real-time data endpoint
        endpoint = f"{self.base_url}/3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
        
        params = {
            'api-key': self.api_key,
            'format': 'json',
            'limit': limit,
            'offset': 0
        }
        
        try:
            print(f"Fetching data from CPCB API...")
            response = requests.get(endpoint, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Successfully fetched data from API")
                return data
            else:
                print(f"Error: API returned status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"Error fetching data from API: {e}")
            return None
    
    def parse_and_store_data(self, api_data):
        """Parse API response and store in PostgreSQL"""
        if not api_data or 'records' not in api_data:
            print("No records found in API response")
            return
        
        records = api_data['records']
        print(f"Processing {len(records)} records...")
        
        cursor = self.db_conn.cursor()
        stations_added = 0
        data_points_added = 0
        
        for record in records:
            try:
                # Extract station information
                station_id = record.get('id', record.get('station_id', 'unknown'))
                station_name = record.get('station', record.get('station_name', 'Unknown'))
                city = record.get('city', record.get('area', ''))
                state = record.get('state', '')
                
                # Insert or update station
                cursor.execute("""
                    INSERT INTO stations (station_id, station_name, city, state)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (station_id) DO UPDATE
                    SET station_name = EXCLUDED.station_name,
                        city = EXCLUDED.city,
                        state = EXCLUDED.state
                    RETURNING station_id
                """, (station_id, station_name, city, state))
                
                result = cursor.fetchone()
                if result:
                    stations_added += 1
                
                # Parse timestamp
                last_update = record.get('last_update', record.get('lastupdate', datetime.now().isoformat()))
                try:
                    recorded_at = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
                except:
                    recorded_at = datetime.now()
                
                # Extract pollutant data
                pollutants = {
                    'PM2.5': record.get('pm2_5', record.get('pm25')),
                    'PM10': record.get('pm10'),
                    'NO2': record.get('no2'),
                    'SO2': record.get('so2'),
                    'CO': record.get('co'),
                    'O3': record.get('ozone', record.get('o3')),
                    'NH3': record.get('nh3')
                }
                
                # Get AQI values
                aqi = record.get('aqi', record.get('aqivalue'))
                aqi_category = record.get('aqicategory', self.get_aqi_category(aqi))
                
                # Insert pollutant data
                for pollutant_id, value in pollutants.items():
                    if value is not None and value != '':
                        try:
                            pollutant_value = float(value)
                            cursor.execute("""
                                INSERT INTO air_quality_data 
                                (station_id, recorded_at, pollutant_id, pollutant_avg, aqi, aqi_category)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON CONFLICT (station_id, recorded_at, pollutant_id) DO UPDATE
                                SET pollutant_avg = EXCLUDED.pollutant_avg,
                                    aqi = EXCLUDED.aqi,
                                    aqi_category = EXCLUDED.aqi_category
                            """, (station_id, recorded_at, pollutant_id, pollutant_value, aqi, aqi_category))
                            data_points_added += 1
                        except (ValueError, TypeError):
                            continue
                
            except Exception as e:
                print(f"Error processing record: {e}")
                continue
        
        self.db_conn.commit()
        cursor.close()
        
        print(f"\nData stored successfully!")
        print(f"Stations processed: {stations_added}")
        print(f"Data points added: {data_points_added}")
    
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
    
    def fetch_and_store(self):
        """Main method to fetch and store data"""
        if not self.db_conn:
            print("Database connection not available")
            return False
        
        data = self.fetch_realtime_data()
        if data:
            self.parse_and_store_data(data)
            return True
        return False
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            print("Database connection closed")

if __name__ == "__main__":
    print("=== CPCB Air Quality Data Collector ===\n")
    collector = CPCBDataCollector()
    
    try:
        collector.fetch_and_store()
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    finally:
        collector.close()
