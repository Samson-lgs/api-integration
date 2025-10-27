"""
Query and View CPCB Air Quality Data from SQLite
"""

import sqlite3
import pandas as pd
from datetime import datetime

class AirQualityQuerySQLite:
    def __init__(self, db_path='air_quality.db'):
        self.conn = sqlite3.connect(db_path)
        print(f"✓ Connected to database: {db_path}\n")
    
    def get_summary(self):
        """Get overall summary of collected data"""
        cursor = self.conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM stations")
        station_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM air_quality_data")
        data_count = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT pollutant_id, COUNT(*) as count 
            FROM air_quality_data 
            GROUP BY pollutant_id
            ORDER BY count DESC
        """)
        pollutant_counts = cursor.fetchall()
        
        print("="*70)
        print("DATABASE SUMMARY")
        print("="*70)
        print(f"Total Monitoring Stations: {station_count}")
        print(f"Total Data Points Collected: {data_count}")
        print(f"\nPollutant Distribution:")
        for pollutant, count in pollutant_counts:
            print(f"  {pollutant}: {count} readings")
        print("="*70 + "\n")
    
    def get_latest_readings(self, limit=20):
        """Get latest air quality readings"""
        query = """
            SELECT 
                s.station_name,
                s.city,
                s.state,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            ORDER BY aq.recorded_at DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        return df
    
    def get_stations_by_city(self, city):
        """Get all stations in a specific city"""
        query = """
            SELECT station_name, city, state, latitude, longitude
            FROM stations
            WHERE city LIKE ?
            ORDER BY station_name
        """
        df = pd.read_sql_query(query, self.conn, params=(f'%{city}%',))
        return df
    
    def get_pollutant_data(self, pollutant_id, limit=50):
        """Get data for a specific pollutant"""
        query = """
            SELECT 
                s.station_name,
                s.city,
                aq.recorded_at,
                aq.pollutant_avg,
                aq.pollutant_min,
                aq.pollutant_max,
                aq.aqi,
                aq.aqi_category
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE aq.pollutant_id = ?
            ORDER BY aq.pollutant_avg DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, self.conn, params=(pollutant_id, limit))
        return df
    
    def get_worst_aqi_stations(self, limit=10):
        """Get stations with worst air quality"""
        query = """
            SELECT 
                s.station_name,
                s.city,
                s.state,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category,
                aq.recorded_at
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE aq.aqi IS NOT NULL
            ORDER BY aq.aqi DESC
            LIMIT ?
        """
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        return df
    
    def get_city_statistics(self):
        """Get statistics by city"""
        query = """
            SELECT 
                s.city,
                s.state,
                COUNT(DISTINCT s.station_id) as station_count,
                AVG(aq.aqi) as avg_aqi,
                MAX(aq.aqi) as max_aqi,
                MIN(aq.aqi) as min_aqi
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE aq.aqi IS NOT NULL
            GROUP BY s.city, s.state
            ORDER BY avg_aqi DESC
            LIMIT 20
        """
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def export_to_csv(self, filename='air_quality_export.csv'):
        """Export all data to CSV for ML training"""
        query = """
            SELECT 
                s.station_id,
                s.station_name,
                s.city,
                s.state,
                s.latitude,
                s.longitude,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.pollutant_min,
                aq.pollutant_max,
                aq.aqi,
                aq.aqi_category
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            ORDER BY aq.recorded_at DESC
        """
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(filename, index=False)
        print(f"✓ Data exported to {filename}")
        print(f"  Total records: {len(df)}")
        return df
    
    def close(self):
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    print("="*70)
    print("CPCB Air Quality Data - Query Tool")
    print("="*70)
    print()
    
    query = AirQualityQuerySQLite()
    
    try:
        # Show summary
        query.get_summary()
        
        # Show latest readings
        print("\n📊 LATEST 10 AIR QUALITY READINGS")
        print("="*70)
        latest = query.get_latest_readings(10)
        print(latest.to_string(index=False))
        
        # Show worst AQI stations
        print("\n\n⚠️  WORST AIR QUALITY STATIONS")
        print("="*70)
        worst = query.get_worst_aqi_stations(10)
        print(worst.to_string(index=False))
        
        # Show city statistics
        print("\n\n🏙️  CITY-WISE AIR QUALITY STATISTICS")
        print("="*70)
        cities = query.get_city_statistics()
        print(cities.to_string(index=False))
        
        # Show PM2.5 data
        print("\n\n💨 PM2.5 READINGS (TOP 10 HIGHEST)")
        print("="*70)
        pm25 = query.get_pollutant_data('PM2.5', 10)
        if not pm25.empty:
            print(pm25.to_string(index=False))
        else:
            print("No PM2.5 data available")
        
        # Export data
        print("\n\n💾 EXPORTING DATA FOR ML TRAINING")
        print("="*70)
        query.export_to_csv('cpcb_air_quality_data.csv')
        
        print("\n" + "="*70)
        print("✓ Query completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        query.close()
