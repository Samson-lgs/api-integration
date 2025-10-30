"""
Quick Test Server with Mock Data
Use this to test the UI without database setup
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import datetime, timedelta
import random

app = Flask(__name__)
CORS(app)

# Mock data storage for alerts
ALERT_SETTINGS = {
    'email': None,
    'alerts': []
}
ALERT_COUNTER = 0

# Mock cities
CITIES = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata', 'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow']

# Generate mock station data
def generate_mock_stations():
    stations = []
    coords = {
        'Delhi': [(28.7041, 77.1025), (28.6139, 77.2090), (28.5355, 77.3910)],
        'Mumbai': [(19.0760, 72.8777), (19.1136, 72.8697), (18.9388, 72.8354)],
        'Bangalore': [(12.9716, 77.5946), (12.9352, 77.6245), (13.0358, 77.5970)],
        'Chennai': [(13.0827, 80.2707), (13.0524, 80.2511), (13.1189, 80.2981)],
        'Kolkata': [(22.5726, 88.3639), (22.5431, 88.3424), (22.6208, 88.4098)],
        'Hyderabad': [(17.3850, 78.4867), (17.4239, 78.4738), (17.4486, 78.3908)],
        'Pune': [(18.5204, 73.8567), (18.5642, 73.7769), (18.4574, 73.8677)],
        'Ahmedabad': [(23.0225, 72.5714), (23.0368, 72.5661), (23.0522, 72.6187)],
        'Jaipur': [(26.9124, 75.7873), (26.9260, 75.8235), (26.8851, 75.8143)],
        'Lucknow': [(26.8467, 80.9462), (26.8389, 80.9149), (26.8734, 80.9813)]
    }
    
    station_id = 1
    for city, locations in coords.items():
        for i, (lat, lon) in enumerate(locations):
            aqi = random.randint(50, 400)
            pm25 = aqi * 0.6 + random.uniform(-10, 10)
            pm10 = aqi * 0.8 + random.uniform(-15, 15)
            no2 = random.uniform(20, 120)
            so2 = random.uniform(5, 50)
            co = random.uniform(0.5, 5.0)
            o3 = random.uniform(10, 100)
            
            stations.append({
                'id': station_id,
                'name': f'{city} Station {i+1}',
                'city': city,
                'latitude': lat,
                'longitude': lon,
                'aqi': round(aqi),
                'pm25': round(pm25, 2),
                'pm10': round(pm10, 2),
                'no2': round(no2, 2),
                'so2': round(so2, 2),
                'co': round(co, 2),
                'o3': round(o3, 2),
                'last_updated': (datetime.now() - timedelta(minutes=random.randint(1, 30))).isoformat()
            })
            station_id += 1
    
    return stations

# Generate historical data
def generate_historical_data(days=7):
    data = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        pm25 = random.uniform(60, 150)
        data.append({
            'date': date,
            'pm25': round(pm25, 2),
            'pm10': round(pm25 * 1.3, 2),
            'no2': round(random.uniform(30, 80), 2),
            'aqi': round(pm25 * 1.8)
        })
    return data

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'Test server running',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/stations', methods=['GET'])
def get_stations():
    stations = generate_mock_stations()
    city_filter = request.args.get('city')
    
    if city_filter:
        stations = [s for s in stations if s['city'].lower() == city_filter.lower()]
    
    return jsonify({
        'status': 'success',
        'data': stations,
        'count': len(stations)
    })

@app.route('/api/cities', methods=['GET'])
def get_cities():
    stations = generate_mock_stations()
    city_data = {}
    
    for station in stations:
        city = station['city']
        if city not in city_data:
            city_data[city] = {
                'name': city,
                'station_count': 0,
                'total_aqi': 0,
                'total_pm25': 0,
                'total_pm10': 0,
                'total_no2': 0,
                'total_so2': 0,
                'total_co': 0,
                'total_o3': 0
            }
        
        city_data[city]['station_count'] += 1
        city_data[city]['total_aqi'] += station['aqi']
        city_data[city]['total_pm25'] += station['pm25']
        city_data[city]['total_pm10'] += station['pm10']
        city_data[city]['total_no2'] += station['no2']
        city_data[city]['total_so2'] += station['so2']
        city_data[city]['total_co'] += station['co']
        city_data[city]['total_o3'] += station['o3']
    
    cities = []
    for city, data in city_data.items():
        count = data['station_count']
        cities.append({
            'name': city,
            'avg_aqi': round(data['total_aqi'] / count),
            'avg_pm25': round(data['total_pm25'] / count, 2),
            'avg_pm10': round(data['total_pm10'] / count, 2),
            'avg_no2': round(data['total_no2'] / count, 2),
            'avg_so2': round(data['total_so2'] / count, 2),
            'avg_co': round(data['total_co'] / count, 2),
            'avg_o3': round(data['total_o3'] / count, 2)
        })
    
    return jsonify({
        'status': 'success',
        'data': cities
    })

@app.route('/api/trends', methods=['GET'])
def get_trends():
    city = request.args.get('city', 'Delhi')
    days = int(request.args.get('days', 7))
    
    data = generate_historical_data(days)
    
    return jsonify({
        'status': 'success',
        'data': data,
        'city': city
    })

@app.route('/api/predictions/<city>', methods=['GET'])
def get_predictions(city):
    predictions = []
    for i in range(1, 8):
        date = (datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d')
        base_pm25 = random.uniform(70, 130)
        predictions.append({
            'date': date,
            'pm25': round(base_pm25, 2),
            'pm10': round(base_pm25 * 1.3, 2),
            'no2': round(random.uniform(35, 75), 2),
            'aqi': round(base_pm25 * 1.8)
        })
    
    return jsonify({
        'status': 'success',
        'data': predictions,
        'city': city
    })

@app.route('/api/data/latest', methods=['GET'])
def get_latest_data():
    stations = generate_mock_stations()
    city_filter = request.args.get('city')
    limit = int(request.args.get('limit', 20))
    
    if city_filter:
        stations = [s for s in stations if s['city'].lower() == city_filter.lower()]
    
    return jsonify({
        'status': 'success',
        'data': stations[:limit]
    })

@app.route('/api/analytics/summary', methods=['GET'])
def get_summary():
    stations = generate_mock_stations()
    
    total_stations = len(stations)
    avg_aqi = sum(s['aqi'] for s in stations) / total_stations if total_stations else 0
    avg_pm25 = sum(s['pm25'] for s in stations) / total_stations if total_stations else 0
    avg_pm10 = sum(s['pm10'] for s in stations) / total_stations if total_stations else 0
    
    # Count stations by category
    good = sum(1 for s in stations if s['aqi'] <= 50)
    satisfactory = sum(1 for s in stations if 51 <= s['aqi'] <= 100)
    moderate = sum(1 for s in stations if 101 <= s['aqi'] <= 200)
    poor = sum(1 for s in stations if 201 <= s['aqi'] <= 300)
    very_poor = sum(1 for s in stations if 301 <= s['aqi'] <= 400)
    severe = sum(1 for s in stations if s['aqi'] > 400)
    
    return jsonify({
        'status': 'success',
        'summary': {
            'total_stations': total_stations,
            'active_stations': total_stations,
            'avg_aqi': round(avg_aqi, 2),
            'avg_pm25': round(avg_pm25, 2),
            'avg_pm10': round(avg_pm10, 2),
            'good': good,
            'satisfactory': satisfactory,
            'moderate': moderate,
            'poor': poor,
            'very_poor': very_poor,
            'severe': severe,
            'worst_city': max(CITIES, key=lambda c: random.random()),
            'best_city': min(CITIES, key=lambda c: random.random())
        }
    })

@app.route('/api/analytics/trends', methods=['GET'])
def get_analytics_trends():
    pollutant = request.args.get('pollutant_id', 'PM2.5')
    days = int(request.args.get('days', 7))
    
    data = []
    for i in range(days):
        date = (datetime.now() - timedelta(days=days-i-1)).strftime('%Y-%m-%d')
        if pollutant.upper() == 'PM2.5':
            value = random.uniform(60, 150)
        elif pollutant.upper() == 'PM10':
            value = random.uniform(80, 200)
        elif pollutant.upper() == 'NO2':
            value = random.uniform(30, 80)
        else:
            value = random.uniform(50, 150)
        
        data.append({
            'date': date,
            'value': round(value, 2),
            'pollutant': pollutant
        })
    
    return jsonify({
        'status': 'success',
        'data': data
    })

# Alert endpoints
@app.route('/api/alerts/settings', methods=['GET'])
def get_alert_settings():
    return jsonify({
        'status': 'success',
        'data': ALERT_SETTINGS
    })

@app.route('/api/alerts/email', methods=['POST'])
def update_email():
    data = request.json
    ALERT_SETTINGS['email'] = data.get('email')
    return jsonify({
        'status': 'success',
        'message': 'Email updated successfully',
        'data': {'email': ALERT_SETTINGS['email']}
    })

@app.route('/api/alerts', methods=['POST'])
def create_alert():
    global ALERT_COUNTER
    data = request.json
    
    ALERT_COUNTER += 1
    alert = {
        'id': ALERT_COUNTER,
        'city': data.get('city'),
        'threshold': data.get('threshold'),
        'frequency': data.get('frequency', 'daily'),
        'enabled': True,
        'created_at': datetime.now().isoformat()
    }
    
    ALERT_SETTINGS['alerts'].append(alert)
    
    return jsonify({
        'status': 'success',
        'message': 'Alert created successfully',
        'data': alert
    }), 201

@app.route('/api/alerts/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    data = request.json
    
    for alert in ALERT_SETTINGS['alerts']:
        if alert['id'] == alert_id:
            alert.update(data)
            return jsonify({
                'status': 'success',
                'message': 'Alert updated successfully',
                'data': alert
            })
    
    return jsonify({
        'status': 'error',
        'message': 'Alert not found'
    }), 404

@app.route('/api/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    global ALERT_SETTINGS
    
    ALERT_SETTINGS['alerts'] = [a for a in ALERT_SETTINGS['alerts'] if a['id'] != alert_id]
    
    return jsonify({
        'status': 'success',
        'message': 'Alert deleted successfully'
    })

@app.route('/api/alerts/<int:alert_id>/test', methods=['POST'])
def test_alert(alert_id):
    for alert in ALERT_SETTINGS['alerts']:
        if alert['id'] == alert_id:
            print(f"[TEST EMAIL] Alert test for {alert['city']} - Threshold: {alert['threshold']}")
            print(f"[TEST EMAIL] To: {ALERT_SETTINGS.get('email', 'No email set')}")
            return jsonify({
                'status': 'success',
                'message': f'Test email would be sent to {ALERT_SETTINGS.get("email", "No email set")}'
            })
    
    return jsonify({
        'status': 'error',
        'message': 'Alert not found'
    }), 404

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Test Server Starting...")
    print("=" * 60)
    print("📍 Server: http://localhost:5000")
    print("📍 Frontend: http://localhost:3000")
    print("=" * 60)
    print("✅ Mock data endpoints available:")
    print("   GET  /api/health")
    print("   GET  /api/stations")
    print("   GET  /api/cities")
    print("   GET  /api/trends")
    print("   GET  /api/predictions/<city>")
    print("   GET  /api/alerts/settings")
    print("   POST /api/alerts/email")
    print("   POST /api/alerts")
    print("   PUT  /api/alerts/<id>")
    print("   DELETE /api/alerts/<id>")
    print("   POST /api/alerts/<id>/test")
    print("=" * 60)
    
    app.run(debug=True, port=5000, host='0.0.0.0')
