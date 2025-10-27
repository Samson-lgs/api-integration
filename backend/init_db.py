"""
Initialize database with sample data
Run this script to populate the database with test data
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from database.db_manager import DatabaseManager
from datetime import datetime, timedelta
import random

def create_sample_data():
    """Create sample stations and air quality data"""
    db = DatabaseManager()
    
    print("🔄 Initializing database schema...")
    if not db.initialize_schema():
        print("❌ Schema initialization failed!")
        return
    
    print("✅ Schema initialized successfully!")
    
    # Sample stations
    stations = [
        {
            'station_id': 'DEL001',
            'station_name': 'Connaught Place',
            'city': 'Delhi',
            'state': 'Delhi',
            'latitude': 28.6315,
            'longitude': 77.2167,
            'data_source': 'CPCB'
        },
        {
            'station_id': 'MUM001',
            'station_name': 'Worli',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'latitude': 19.0176,
            'longitude': 72.8130,
            'data_source': 'CPCB'
        },
        {
            'station_id': 'BLR001',
            'station_name': 'Silk Board',
            'city': 'Bangalore',
            'state': 'Karnataka',
            'latitude': 12.9165,
            'longitude': 77.6230,
            'data_source': 'CPCB'
        },
        {
            'station_id': 'CHN001',
            'station_name': 'Anna Nagar',
            'city': 'Chennai',
            'state': 'Tamil Nadu',
            'latitude': 13.0850,
            'longitude': 80.2080,
            'data_source': 'CPCB'
        },
        {
            'station_id': 'KOL001',
            'station_name': 'Victoria Memorial',
            'city': 'Kolkata',
            'state': 'West Bengal',
            'latitude': 22.5448,
            'longitude': 88.3426,
            'data_source': 'CPCB'
        }
    ]
    
    print("\n🔄 Creating monitoring stations...")
    for station in stations:
        try:
            db.upsert_station(station)
            print(f"  ✅ {station['station_name']}, {station['city']}")
        except Exception as e:
            print(f"  ❌ Failed to create {station['station_name']}: {e}")
    
    # Generate sample air quality data
    print("\n🔄 Generating sample air quality data...")
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
    
    data_count = 0
    for station in stations:
        # Generate data for last 7 days, hourly
        for day in range(7):
            for hour in range(24):
                recorded_at = datetime.now() - timedelta(days=day, hours=hour)
                
                for pollutant in pollutants:
                    # Generate random but realistic values
                    if pollutant == 'PM2.5':
                        base_value = random.uniform(25, 150)
                        aqi = min(500, base_value * 2.5)
                    elif pollutant == 'PM10':
                        base_value = random.uniform(40, 250)
                        aqi = min(500, base_value * 1.8)
                    elif pollutant == 'NO2':
                        base_value = random.uniform(15, 80)
                        aqi = min(500, base_value * 2.0)
                    elif pollutant == 'SO2':
                        base_value = random.uniform(10, 60)
                        aqi = min(500, base_value * 2.2)
                    elif pollutant == 'CO':
                        base_value = random.uniform(0.5, 3.0)
                        aqi = min(500, base_value * 50)
                    else:  # O3
                        base_value = random.uniform(20, 120)
                        aqi = min(500, base_value * 1.5)
                    
                    data = {
                        'station_id': station['station_id'],
                        'recorded_at': recorded_at,
                        'pollutant_id': pollutant,
                        'pollutant_avg': base_value,
                        'pollutant_min': base_value * 0.8,
                        'pollutant_max': base_value * 1.2,
                        'aqi': aqi,
                        'temperature': random.uniform(20, 35),
                        'humidity': random.uniform(40, 80),
                        'wind_speed': random.uniform(2, 15),
                        'wind_direction': random.uniform(0, 360),
                        'pressure': random.uniform(1000, 1020),
                        'data_source': 'SAMPLE_DATA'
                    }
                    
                    try:
                        db.insert_air_quality_data(data)
                        data_count += 1
                    except Exception as e:
                        print(f"  ❌ Failed to insert data: {e}")
    
    print(f"  ✅ Generated {data_count} air quality readings")
    
    # Refresh materialized views
    print("\n🔄 Refreshing materialized views...")
    if db.refresh_materialized_views():
        print("  ✅ Materialized views refreshed")
    
    # Get statistics
    print("\n📊 Database Statistics:")
    stats = db.get_statistics()
    print(f"  Total Stations: {stats['total_stations']}")
    print(f"  Total Readings: {stats['total_readings']}")
    print(f"  Latest Reading: {stats['latest_reading']}")
    print(f"  Cities Covered: {stats['cities_covered']}")
    print(f"  Data Sources: {stats['data_sources']}")
    
    print("\n✅ Database initialization complete!")
    print("\n🚀 You can now start the Flask API:")
    print("   cd backend")
    print("   python api.py")


if __name__ == "__main__":
    create_sample_data()
