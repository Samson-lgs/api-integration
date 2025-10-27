"""
Export Multi-Source Air Quality Data to Unified CSV
Merges data from CPCB, OpenWeather, and IQAir with station IDs
"""

import sqlite3
import pandas as pd
from datetime import datetime

class MultiSourceExporter:
    def __init__(self, db_path='air_quality_multi.db'):
        self.conn = sqlite3.connect(db_path)
        print(f"✓ Connected to: {db_path}\n")
    
    def get_summary(self):
        """Get summary statistics"""
        cursor = self.conn.cursor()
        
        # Overall stats
        cursor.execute("SELECT COUNT(*) FROM stations")
        total_stations = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM air_quality_data")
        total_data = cursor.fetchone()[0]
        
        # By data source
        cursor.execute("""
            SELECT data_source, 
                   COUNT(DISTINCT station_id) as stations,
                   COUNT(*) as data_points
            FROM air_quality_data
            GROUP BY data_source
        """)
        source_stats = cursor.fetchall()
        
        # By pollutant
        cursor.execute("""
            SELECT pollutant_id, COUNT(*) as count
            FROM air_quality_data
            GROUP BY pollutant_id
            ORDER BY count DESC
        """)
        pollutant_stats = cursor.fetchall()
        
        print("="*70)
        print("MULTI-SOURCE AIR QUALITY DATA SUMMARY")
        print("="*70)
        print(f"Total Stations: {total_stations}")
        print(f"Total Data Points: {total_data}")
        print(f"\nBy Data Source:")
        for source, stations, points in source_stats:
            print(f"  {source}: {stations} stations, {points} data points")
        print(f"\nPollutant Distribution:")
        for pollutant, count in pollutant_stats:
            print(f"  {pollutant}: {count} readings")
        print("="*70 + "\n")
    
    def export_unified_csv(self, filename='unified_air_quality_data.csv'):
        """Export all data to unified CSV with all fields"""
        query = """
            SELECT 
                s.station_id,
                s.station_name,
                s.city,
                s.state,
                s.country,
                s.latitude,
                s.longitude,
                s.data_source,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.pollutant_min,
                aq.pollutant_max,
                aq.aqi,
                aq.aqi_category,
                aq.temperature,
                aq.humidity,
                aq.pressure,
                aq.wind_speed
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            ORDER BY s.data_source, aq.recorded_at DESC, s.city, s.station_name
        """
        
        print(f"📊 Exporting unified data to CSV...")
        df = pd.read_sql_query(query, self.conn)
        df.to_csv(filename, index=False)
        
        print(f"✓ Exported {len(df)} records to: {filename}")
        print(f"  Columns: {list(df.columns)}")
        print(f"  File size: {len(df) * len(df.columns)} cells")
        
        return df
    
    def export_by_source(self):
        """Export separate CSV files for each data source"""
        sources = ['CPCB', 'OpenWeather', 'IQAir']
        
        for source in sources:
            query = f"""
                SELECT 
                    s.station_id,
                    s.station_name,
                    s.city,
                    s.state,
                    s.country,
                    s.latitude,
                    s.longitude,
                    aq.recorded_at,
                    aq.pollutant_id,
                    aq.pollutant_avg,
                    aq.pollutant_min,
                    aq.pollutant_max,
                    aq.aqi,
                    aq.aqi_category,
                    aq.temperature,
                    aq.humidity,
                    aq.pressure,
                    aq.wind_speed
                FROM air_quality_data aq
                JOIN stations s ON aq.station_id = s.station_id
                WHERE aq.data_source = '{source}'
                ORDER BY aq.recorded_at DESC
            """
            
            df = pd.read_sql_query(query, self.conn)
            
            if not df.empty:
                filename = f'{source.lower()}_air_quality_data.csv'
                df.to_csv(filename, index=False)
                print(f"✓ Exported {len(df)} {source} records to: {filename}")
            else:
                print(f"  ⚠ No data for {source}")
    
    def get_station_list(self):
        """Get list of all stations with their details"""
        query = """
            SELECT 
                station_id,
                station_name,
                city,
                state,
                country,
                latitude,
                longitude,
                data_source,
                created_at
            FROM stations
            ORDER BY data_source, city, station_name
        """
        
        df = pd.read_sql_query(query, self.conn)
        return df
    
    def get_latest_readings(self, limit=20):
        """Get latest readings from all sources"""
        query = """
            SELECT 
                s.station_name,
                s.city,
                s.data_source,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category,
                aq.temperature,
                aq.humidity
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            ORDER BY aq.recorded_at DESC
            LIMIT ?
        """
        
        df = pd.read_sql_query(query, self.conn, params=(limit,))
        return df
    
    def get_comparison_data(self, city):
        """Get data from all sources for a specific city for comparison"""
        query = """
            SELECT 
                s.data_source,
                s.station_name,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.aqi_category,
                aq.temperature,
                aq.humidity
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
            WHERE s.city LIKE ?
            ORDER BY s.data_source, aq.recorded_at DESC, aq.pollutant_id
        """
        
        df = pd.read_sql_query(query, self.conn, params=(f'%{city}%',))
        return df
    
    def create_pivot_table(self):
        """Create pivot table with pollutants as columns"""
        query = """
            SELECT 
                s.station_id,
                s.station_name,
                s.city,
                s.state,
                s.data_source,
                aq.recorded_at,
                aq.pollutant_id,
                aq.pollutant_avg,
                aq.aqi,
                aq.temperature,
                aq.humidity,
                aq.pressure,
                aq.wind_speed
            FROM air_quality_data aq
            JOIN stations s ON aq.station_id = s.station_id
        """
        
        df = pd.read_sql_query(query, self.conn)
        
        # Pivot pollutants into columns
        pivot = df.pivot_table(
            index=['station_id', 'station_name', 'city', 'state', 'data_source', 
                   'recorded_at', 'aqi', 'temperature', 'humidity', 'pressure', 'wind_speed'],
            columns='pollutant_id',
            values='pollutant_avg',
            aggfunc='first'
        ).reset_index()
        
        return pivot
    
    def export_ml_ready_data(self, filename='ml_ready_air_quality.csv'):
        """Export data in ML-ready format with all features"""
        print(f"🤖 Creating ML-ready dataset...")
        
        pivot = self.create_pivot_table()
        
        # Add time-based features
        pivot['recorded_at'] = pd.to_datetime(pivot['recorded_at'])
        pivot['hour'] = pivot['recorded_at'].dt.hour
        pivot['day'] = pivot['recorded_at'].dt.day
        pivot['month'] = pivot['recorded_at'].dt.month
        pivot['day_of_week'] = pivot['recorded_at'].dt.dayofweek
        pivot['is_weekend'] = pivot['day_of_week'].isin([5, 6]).astype(int)
        
        # Save
        pivot.to_csv(filename, index=False)
        
        print(f"✓ ML-ready dataset exported to: {filename}")
        print(f"  Shape: {pivot.shape[0]} rows × {pivot.shape[1]} columns")
        print(f"  Features available: {list(pivot.columns)}")
        
        return pivot
    
    def close(self):
        if self.conn:
            self.conn.close()

if __name__ == "__main__":
    print("="*70)
    print("Multi-Source Air Quality Data Exporter")
    print("="*70)
    print()
    
    exporter = MultiSourceExporter()
    
    try:
        # Show summary
        exporter.get_summary()
        
        # Export unified CSV
        print("\n📦 EXPORTING DATA")
        print("="*70)
        df = exporter.export_unified_csv('unified_air_quality_data.csv')
        
        print()
        
        # Export by source
        exporter.export_by_source()
        
        print()
        
        # Export ML-ready data
        ml_df = exporter.export_ml_ready_data('ml_ready_air_quality.csv')
        
        print("\n\n📊 SAMPLE DATA (Latest 10 Readings)")
        print("="*70)
        latest = exporter.get_latest_readings(10)
        print(latest.to_string(index=False))
        
        print("\n\n🏙️ STATION LIST")
        print("="*70)
        stations = exporter.get_station_list()
        print(f"Total stations: {len(stations)}")
        print(f"\nStations by source:")
        print(stations.groupby('data_source').size())
        
        print("\n\n📍 COMPARISON: Delhi Data (All Sources)")
        print("="*70)
        delhi = exporter.get_comparison_data('Delhi')
        if not delhi.empty:
            print(f"Found {len(delhi)} readings for Delhi")
            print(delhi.head(15).to_string(index=False))
        
        print("\n" + "="*70)
        print("✓ Export completed successfully!")
        print("="*70)
        print("\nGenerated Files:")
        print("  1. unified_air_quality_data.csv - All data with station IDs")
        print("  2. ml_ready_air_quality.csv - ML-ready with time features")
        print("  3. cpcb_air_quality_data.csv - CPCB data only")
        print("  4. openweather_air_quality_data.csv - OpenWeather data only")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        exporter.close()
