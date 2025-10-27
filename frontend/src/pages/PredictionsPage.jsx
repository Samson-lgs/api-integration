/**
 * Predictions Page
 * ML-powered AQI predictions
 */

import { useState, useEffect } from 'react';
import { TrendingUp, AlertCircle, Brain, Send } from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../services/api';
import '../App.css';

function PredictionsPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [predictions, setPredictions] = useState([]);
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState('');
  const [predicting, setPredicting] = useState(false);
  const [predictionResult, setPredictionResult] = useState(null);

  // Sample features for prediction (in real app, fetch from latest data)
  const [features, setFeatures] = useState({
    pm25: 45,
    pm10: 85,
    no2: 35,
    temperature: 28,
    humidity: 65,
  });

  useEffect(() => {
    loadInitialData();
  }, []);

  const loadInitialData = async () => {
    try {
      setLoading(true);
      const [predictionsResponse, stationsResponse] = await Promise.all([
        apiService.getPredictions(24),
        apiService.getStations(true)
      ]);
      setPredictions(predictionsResponse.data || []);
      setStations(stationsResponse.data || []);
      if (stationsResponse.data?.length > 0) {
        setSelectedStation(stationsResponse.data[0].station_id);
      }
    } catch (err) {
      console.error('Failed to load predictions:', err);
      setError('Failed to load predictions data');
    } finally {
      setLoading(false);
    }
  };

  const handlePredict = async () => {
    if (!selectedStation) {
      alert('Please select a station');
      return;
    }

    try {
      setPredicting(true);
      setError(null);
      
      const response = await apiService.predict({
        station_id: selectedStation,
        model: 'linear_regression',
        features: {
          pm25: parseFloat(features.pm25),
          pm10: parseFloat(features.pm10),
          no2: parseFloat(features.no2),
          temperature: parseFloat(features.temperature),
          humidity: parseFloat(features.humidity),
        }
      });

      setPredictionResult(response);
      
      // Reload predictions
      const predictionsResponse = await apiService.getPredictions(24);
      setPredictions(predictionsResponse.data || []);
    } catch (err) {
      console.error('Prediction failed:', err);
      setError(err.response?.data?.message || 'Prediction failed. Please try again.');
    } finally {
      setPredicting(false);
    }
  };

  const getAqiBadgeClass = (category) => {
    if (!category) return 'aqi-badge';
    const categoryLower = category.toLowerCase();
    if (categoryLower === 'good') return 'aqi-badge aqi-good';
    if (categoryLower === 'satisfactory') return 'aqi-badge aqi-satisfactory';
    if (categoryLower === 'moderate') return 'aqi-badge aqi-moderate';
    if (categoryLower === 'poor') return 'aqi-badge aqi-poor';
    if (categoryLower === 'very poor') return 'aqi-badge aqi-very-poor';
    if (categoryLower === 'severe') return 'aqi-badge aqi-severe';
    return 'aqi-badge';
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="predictions-page">
      <div className="page-header">
        <h1 className="page-title">AQI Predictions</h1>
        <p className="page-description">
          Machine learning powered air quality predictions
        </p>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      <div className="grid grid-cols-2 gap-lg">
        {/* Prediction Form */}
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">
              <Brain size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Generate Prediction
            </h3>
          </div>

          <div>
            <div className="mb-md">
              <label htmlFor="station">Select Station</label>
              <select
                id="station"
                value={selectedStation}
                onChange={(e) => setSelectedStation(e.target.value)}
              >
                <option value="">Choose a station...</option>
                {stations.map((station) => (
                  <option key={station.station_id} value={station.station_id}>
                    {station.station_name} - {station.city}
                  </option>
                ))}
              </select>
            </div>

            <h4 className="mb-md">Input Features</h4>
            
            <div className="grid grid-cols-2 gap-md mb-md">
              <div>
                <label htmlFor="pm25">PM2.5 (µg/m³)</label>
                <input
                  id="pm25"
                  type="number"
                  value={features.pm25}
                  onChange={(e) => setFeatures({ ...features, pm25: e.target.value })}
                  placeholder="45"
                />
              </div>
              <div>
                <label htmlFor="pm10">PM10 (µg/m³)</label>
                <input
                  id="pm10"
                  type="number"
                  value={features.pm10}
                  onChange={(e) => setFeatures({ ...features, pm10: e.target.value })}
                  placeholder="85"
                />
              </div>
              <div>
                <label htmlFor="no2">NO2 (µg/m³)</label>
                <input
                  id="no2"
                  type="number"
                  value={features.no2}
                  onChange={(e) => setFeatures({ ...features, no2: e.target.value })}
                  placeholder="35"
                />
              </div>
              <div>
                <label htmlFor="temperature">Temperature (°C)</label>
                <input
                  id="temperature"
                  type="number"
                  value={features.temperature}
                  onChange={(e) => setFeatures({ ...features, temperature: e.target.value })}
                  placeholder="28"
                />
              </div>
              <div>
                <label htmlFor="humidity">Humidity (%)</label>
                <input
                  id="humidity"
                  type="number"
                  value={features.humidity}
                  onChange={(e) => setFeatures({ ...features, humidity: e.target.value })}
                  placeholder="65"
                />
              </div>
            </div>

            <button
              className="btn-primary"
              onClick={handlePredict}
              disabled={predicting || !selectedStation}
              style={{ width: '100%' }}
            >
              {predicting ? (
                <>
                  <div className="spinner" style={{ width: '16px', height: '16px' }}></div>
                  Predicting...
                </>
              ) : (
                <>
                  <Send size={18} />
                  Generate Prediction
                </>
              )}
            </button>

            {predictionResult && (
              <div className="mt-lg" style={{ 
                padding: '1rem', 
                backgroundColor: '#f0fdf4', 
                border: '1px solid #86efac',
                borderRadius: '0.5rem'
              }}>
                <h4 className="mb-md">Prediction Result</h4>
                <div className="grid grid-cols-2 gap-md">
                  <div>
                    <p className="text-sm text-muted mb-0">Predicted AQI</p>
                    <p className="text-xl font-bold mb-0">{predictionResult.predicted_aqi}</p>
                  </div>
                  <div>
                    <p className="text-sm text-muted mb-0">Category</p>
                    <span className={getAqiBadgeClass(predictionResult.aqi_category)}>
                      {predictionResult.aqi_category}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-muted mb-0">Confidence Interval</p>
                    <p className="text-sm mb-0">
                      {predictionResult.confidence_interval?.lower} - {predictionResult.confidence_interval?.upper}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-muted mb-0">Model Used</p>
                    <p className="text-sm mb-0">{predictionResult.model_used}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Predictions */}
        <div className="data-table-container">
          <div className="table-header">
            <h3 className="mb-0">Recent Predictions</h3>
            <span className="text-sm text-muted">{predictions.length} predictions</span>
          </div>
          <div className="table-wrapper" style={{ maxHeight: '600px', overflowY: 'auto' }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Station</th>
                  <th>City</th>
                  <th>Predicted AQI</th>
                  <th>Category</th>
                  <th>Model</th>
                  <th>Predicted For</th>
                </tr>
              </thead>
              <tbody>
                {predictions.length > 0 ? (
                  predictions.map((pred, index) => (
                    <tr key={index}>
                      <td className="font-medium">{pred.station_name}</td>
                      <td>{pred.city}</td>
                      <td className="font-semibold">{pred.predicted_aqi?.toFixed(0)}</td>
                      <td>
                        <span className={getAqiBadgeClass(pred.predicted_category)}>
                          {pred.predicted_category || 'Unknown'}
                        </span>
                      </td>
                      <td className="text-sm">{pred.model_name}</td>
                      <td className="text-sm text-muted">
                        {pred.predicted_for ? format(new Date(pred.predicted_for), 'MMM dd, HH:mm') : 'N/A'}
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" className="text-center text-muted">
                      No predictions available
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PredictionsPage;
