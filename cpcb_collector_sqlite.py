"""
CPCB Air Quality Data Collector - SQLite Version
Fetches air quality data from CPCB API and stores in SQLite (no PostgreSQL needed)
"""

import requests
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
import json

load_dotenv()

class CPCBDataCollectorSQLite:
    def __init__(self, db_path='air_quality.db'):
        self.api_key = os.getenv('CPCB_API_KEY')
        self.base_url = "https://api.data.gov.in/resource"
        self.db_path = db_path
        self.db_conn = None
        self.setup_database()
    
    def setup_database(self):
        """Create SQLite database and tables"""
        self.db_conn = sqlite3.connect(self.db_path)
        cursor = self.db_conn.cursor()
        
        # Create stations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                station_id TEXT PRIMARY KEY,
                station_name TEXT NOT NULL,
                city TEXT,
                state TEXT,
                latitude REAL,
                longitude REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create air quality data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS air_quality_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                station_id TEXT,
                recorded_at TIMESTAMP NOT NULL,
                pollutant_id TEXT,
                pollutant_avg REAL,
                pollutant_max REAL,
                pollutant_min REAL,
                aqi REAL,
                aqi_category TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (station_id) REFERENCES stations(station_id),
                UNIQUE(station_id, recorded_at, pollutant_id)
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_station_recorded 
            ON air_quality_data(station_id, recorded_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recorded_at 
            ON air_quality_data(recorded_at)
        """)
        
        self.db_conn.commit()
        print(f"✓ SQLite database initialized: {self.db_path}")
    
    def fetch_realtime_data(self, limit=1000):
        """Fetch real-time air quality data from CPCB API"""
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
                print(f"✓ Successfully fetched data from API")
                return data
            else:
                print(f"✗ API returned status code {response.status_code}")
                print(f"Response: {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error fetching data from API: {e}")
            return None
    
    def parse_and_store_data(self, api_data):
        """Parse API response and store in SQLite"""
        if not api_data or 'records' not in api_data:
            print("No records found in API response")
            return
        
        records = api_data['records']
        print(f"Processing {len(records)} records...")
        
        cursor = self.db_conn.cursor()
        stations_added = 0
        data_points_added = 0
        stations_seen = set()
        
        for record in records:
            try:
                # Extract station information
                station_name = record.get('station', 'Unknown')
                city = record.get('city', '')
                state = record.get('state', '')
                latitude = record.get('latitude', '')
                longitude = record.get('longitude', '')
                
                # Create unique station_id from station name and city
                station_id = f"{city}_{station_name}".replace(' ', '_').replace(',', '')
                
                # Insert or update station (only once per unique station)
                if station_id not in stations_seen:
                    cursor.execute("""
                        INSERT OR REPLACE INTO stations (station_id, station_name, city, state, latitude, longitude)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (station_id, station_name, city, state, latitude, longitude))
                    stations_added += 1
                    stations_seen.add(station_id)
                
                # Parse timestamp - format: "26-10-2025 21:00:00"
                last_update = record.get('last_update', '')
                try:
                    recorded_at = datetime.strptime(last_update, "%d-%m-%Y %H:%M:%S")
                except:
                    recorded_at = datetime.now()
                
                # Extract pollutant data from the record
                pollutant_id = record.get('pollutant_id', '')
                pollutant_min = record.get('min_value', '')
                pollutant_max = record.get('max_value', '')
                pollutant_avg = record.get('avg_value', '')
                
                # Calculate AQI based on pollutant values (simplified)
                aqi = self.calculate_aqi(pollutant_id, pollutant_avg)
                aqi_category = self.get_aqi_category(aqi)
                
                # Insert pollutant data
                if pollutant_id and pollutant_avg:
                    try:
                        avg_value = float(pollutant_avg)
                        min_value = float(pollutant_min) if pollutant_min else None
                        max_value = float(pollutant_max) if pollutant_max else None
                        
                        cursor.execute("""
                            INSERT OR REPLACE INTO air_quality_data 
                            (station_id, recorded_at, pollutant_id, pollutant_avg, pollutant_min, pollutant_max, aqi, aqi_category)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (station_id, recorded_at, pollutant_id, avg_value, min_value, max_value, aqi, aqi_category))
                        data_points_added += 1
                    except (ValueError, TypeError) as e:
                        continue
                
            except Exception as e:
                print(f"Error processing record: {e}")
                continue
        
        self.db_conn.commit()
        
        print(f"\n✓ Data stored successfully!")
        print(f"  Stations processed: {stations_added}")
        print(f"  Data points added: {data_points_added}")
    
    def calculate_aqi(self, pollutant_id, value):
        """Calculate AQI based on pollutant concentration"""
        if not value:
            return None
        
        try:
            val = float(value)
            
            # Simplified AQI calculation for PM2.5 and PM10
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
            
            # For other pollutants, return a simplified estimate
            else:
                return min(500, val * 2)  # Simplified mapping
                
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
        
        cursor.execute("SELECT COUNT(*) FROM stations")
        station_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM air_quality_data")
        data_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT pollutant_id, COUNT(*) as count 
            FROM air_quality_data 
            GROUP BY pollutant_id
        """)
        pollutant_counts = cursor.fetchall()
        
        return {
            'stations': station_count,
            'data_points': data_count,
            'pollutants': pollutant_counts
        }
    
    def fetch_and_store(self):
        """Main method to fetch and store data"""
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
    print("="*70)
    print("CPCB Air Quality Data Collector (SQLite - No PostgreSQL Required)")
    print("="*70)
    print()
    
    collector = CPCBDataCollectorSQLite()
    
    try:
        if collector.fetch_and_store():
            print("\n" + "="*70)
            print("Data Collection Summary")
            print("="*70)
            stats = collector.get_statistics()
            print(f"Total Stations: {stats['stations']}")
            print(f"Total Data Points: {stats['data_points']}")
            print(f"\nPollutant Distribution:")
            for pollutant, count in stats['pollutants']:
                print(f"  {pollutant}: {count} readings")
            print("="*70)
            print("\n✓ Collection completed successfully!")
            print(f"✓ Data saved to: {collector.db_path}")
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"\n✗ Error: {e}")
    finally:
        collector.close()
