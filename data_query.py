"""
Query and analyze air quality data from PostgreSQL
Utility script for data retrieval and analysis
"""

import psycopg2
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

class AirQualityQuery:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def get_latest_data(self, limit=10):
        """Get the latest air quality readings"""
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
            LIMIT %s
        """
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        return df
    
    def get_station_data(self, city=None, state=None):
        """Get all stations, optionally filtered by city or state"""
        query = "SELECT * FROM stations WHERE 1=1"
        params = []
        
        if city:
            query += " AND city = %s"
            params.append(city)
        if state:
            query += " AND state = %s"
            params.append(state)
        
        df = pd.read_sql_query(query, self.conn, params=params if params else None)
        return df
    
    def get_data_by_date_range(self, start_date, end_date, station_id=None):
        """Get air quality data for a specific date range"""
        query = """
            SELECT 
                s.station_name,
                s.city,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE aq.recorded_at BETWEEN %s AND %s
        """
        params = [start_date, end_date]
        
        if station_id:
            query += " AND aq.station_id = %s"
            params.append(station_id)
        
        query += " ORDER BY aq.recorded_at DESC"
        
        df = pd.read_sql_query(query, self.conn, params=params)
        return df
    
    def get_aqi_statistics(self, city=None):
        """Get AQI statistics by city"""
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
        """
        
        if city:
            query += " AND s.city = %s"
            params = (city,)
        else:
            params = None
        
        query += " GROUP BY s.city, s.state ORDER BY avg_aqi DESC"
        
        df = pd.read_sql_query(query, self.conn, params=params)
        return df
    
    def get_pollutant_trends(self, pollutant_id, days=7):
        """Get pollutant trends for the last N days"""
        start_date = datetime.now() - timedelta(days=days)
        
        query = """
            SELECT 
                DATE(aq.recorded_at) as date,
                s.city,
                AVG(aq.pollutant_avg) as avg_value,
                MAX(aq.pollutant_avg) as max_value,
                MIN(aq.pollutant_avg) as min_value
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE aq.pollutant_id = %s
            AND aq.recorded_at >= %s
            GROUP BY DATE(aq.recorded_at), s.city
            ORDER BY date DESC, s.city
        """
        
        df = pd.read_sql_query(query, self.conn, params=(pollutant_id, start_date))
        return df
    
    def export_to_csv(self, dataframe, filename):
        """Export dataframe to CSV file"""
        dataframe.to_csv(filename, index=False)
        print(f"Data exported to {filename}")
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Example usage
if __name__ == "__main__":
    query = AirQualityQuery()
    
    try:
        print("=== Latest Air Quality Data ===")
        latest_data = query.get_latest_data(20)
        print(latest_data)
        
        print("\n=== All Stations ===")
        stations = query.get_station_data()
        print(f"Total stations: {len(stations)}")
        print(stations)
        
        print("\n=== AQI Statistics by City ===")
        aqi_stats = query.get_aqi_statistics()
        print(aqi_stats)
        
        # Export data
        # query.export_to_csv(latest_data, 'latest_aqi_data.csv')
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        query.close()
