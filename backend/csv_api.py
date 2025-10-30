"""
Simple Flask API serving data from CSV file
Use this until PostgreSQL is set up
"""

from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

CSV_FILE = 'air_quality_data.csv'


def get_aqi_category(aqi):
    """Get AQI category from numeric value"""
    if aqi <= 1:
        return 'Good'
    elif aqi <= 2:
        return 'Fair'
    elif aqi <= 3:
        return 'Moderate'
    elif aqi <= 4:
        return 'Poor'
    elif aqi <= 5:
        return 'Very Poor'
    else:
        return 'Extremely Poor'


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'CSV-based API operational',
        'timestamp': datetime.now().isoformat(),
        'data_file': CSV_FILE,
        'file_exists': os.path.exists(CSV_FILE)
    })


@app.route('/api/stations', methods=['GET'])
def get_stations():
    """Get all stations with latest readings"""
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.read_csv(CSV_FILE)
        
        # Get latest record for each city
        df_latest = df.sort_values('timestamp').groupby('city').tail(1)
        
        stations = []
        for _, row in df_latest.iterrows():
            stations.append({
                'name': row['station_name'],
                'city': row['city'],
                'lat': row['latitude'],
                'lng': row['longitude'],
                'pm25': float(row['pm25']) if pd.notna(row['pm25']) else None,
                'pm10': float(row['pm10']) if pd.notna(row['pm10']) else None,
                'no2': float(row['no2']) if pd.notna(row['no2']) else None,
                'so2': float(row['so2']) if pd.notna(row['so2']) else None,
                'co': float(row['co']) if pd.notna(row['co']) else None,
                'o3': float(row['o3']) if pd.notna(row['o3']) else None,
                'aqi': int(row['aqi']) if pd.notna(row['aqi']) else None,
                'category': get_aqi_category(row['aqi']),
                'last_updated': row['timestamp'],
                'source': row['source']
            })
        
        return jsonify(stations)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/cities', methods=['GET'])
def get_cities():
    """Get all cities with average AQI"""
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.read_csv(CSV_FILE)
        
        # Group by city and get latest/average
        cities = []
        for city_name in df['city'].unique():
            city_data = df[df['city'] == city_name].sort_values('timestamp').tail(1).iloc[0]
            
            cities.append({
                'city': city_name,
                'aqi': int(city_data['aqi']),
                'pm25': round(float(city_data['pm25']), 2) if pd.notna(city_data['pm25']) else None,
                'pm10': round(float(city_data['pm10']), 2) if pd.notna(city_data['pm10']) else None,
                'category': get_aqi_category(city_data['aqi']),
                'last_updated': city_data['timestamp']
            })
        
        # Sort by AQI descending
        cities.sort(key=lambda x: x['aqi'], reverse=True)
        
        return jsonify(cities)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    try:
        if not os.path.exists(CSV_FILE):
            return jsonify({'error': 'No data available'}), 404
        
        df = pd.read_csv(CSV_FILE)
        
        return jsonify({
            'total_records': len(df),
            'cities_covered': df['city'].nunique(),
            'latest_update': df['timestamp'].max(),
            'sources': df['source'].unique().tolist()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("CSV-Based API Server Starting...")
    print("="*70)
    print(f"Data file: {CSV_FILE}")
    print(f"File exists: {os.path.exists(CSV_FILE)}")
    print("\nEndpoints:")
    print("  http://localhost:5000/api/health")
    print("  http://localhost:5000/api/stations")
    print("  http://localhost:5000/api/cities")
    print("  http://localhost:5000/api/stats")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
