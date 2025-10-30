/**
 * Multi-City Comparison Component
 * Compare air quality across multiple cities
 */

import { useState, useEffect } from 'react';
import { BarChart, Bar, RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, TrendingDown, AlertCircle } from 'lucide-react';
import apiService from '../services/api';

function CityComparison() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cities, setCities] = useState([]);
  const [selectedCities, setSelectedCities] = useState([]);
  const [comparisonData, setComparisonData] = useState([]);
  const [viewMode, setViewMode] = useState('bar'); // 'bar', 'radar', 'table'

  useEffect(() => {
    loadCities();
  }, []);

  useEffect(() => {
    if (selectedCities.length > 0) {
      loadComparisonData();
    }
  }, [selectedCities]);

  const loadCities = async () => {
    try {
      const response = await apiService.getCities();
      setCities(response.data || []);
      
      // Auto-select top 5 cities by default
      const topCities = (response.data || []).slice(0, 5).map(c => c.city);
      setSelectedCities(topCities);
    } catch (err) {
      console.error('Failed to load cities:', err);
      setError('Failed to load cities');
    }
  };

  const loadComparisonData = async () => {
    try {
      setLoading(true);
      setError(null);

      const dataPromises = selectedCities.map(city =>
        apiService.getCityData(city, 7)
      );

      const responses = await Promise.all(dataPromises);
      
      const comparison = responses.map((response, index) => {
        const cityData = response.data || [];
        const cityName = selectedCities[index];
        
        // Calculate averages
        const avgPM25 = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.pm25 || 0), 0) / cityData.length 
          : 0;
        const avgPM10 = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.pm10 || 0), 0) / cityData.length 
          : 0;
        const avgNO2 = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.no2 || 0), 0) / cityData.length 
          : 0;
        const avgSO2 = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.so2 || 0), 0) / cityData.length 
          : 0;
        const avgCO = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.co || 0), 0) / cityData.length 
          : 0;
        const avgO3 = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.o3 || 0), 0) / cityData.length 
          : 0;
        const avgAQI = cityData.length > 0 
          ? cityData.reduce((sum, d) => sum + (d.aqi || 0), 0) / cityData.length 
          : 0;

        return {
          city: cityName,
          pm25: parseFloat(avgPM25.toFixed(1)),
          pm10: parseFloat(avgPM10.toFixed(1)),
          no2: parseFloat(avgNO2.toFixed(1)),
          so2: parseFloat(avgSO2.toFixed(1)),
          co: parseFloat(avgCO.toFixed(1)),
          o3: parseFloat(avgO3.toFixed(1)),
          aqi: parseFloat(avgAQI.toFixed(0)),
        };
      });

      setComparisonData(comparison);
    } catch (err) {
      console.error('Failed to load comparison data:', err);
      setError('Failed to load comparison data');
    } finally {
      setLoading(false);
    }
  };

  const handleCityToggle = (city) => {
    setSelectedCities(prev => {
      if (prev.includes(city)) {
        return prev.filter(c => c !== city);
      } else if (prev.length < 10) {
        return [...prev, city];
      }
      return prev;
    });
  };

  const getAQIColor = (aqi) => {
    if (aqi <= 50) return '#10b981';
    if (aqi <= 100) return '#fbbf24';
    if (aqi <= 200) return '#f97316';
    if (aqi <= 300) return '#ef4444';
    if (aqi <= 400) return '#8b5cf6';
    return '#991b1b';
  };

  const getAQICategory = (aqi) => {
    if (aqi <= 50) return 'Good';
    if (aqi <= 100) return 'Satisfactory';
    if (aqi <= 200) return 'Moderate';
    if (aqi <= 300) return 'Poor';
    if (aqi <= 400) return 'Very Poor';
    return 'Severe';
  };

  if (loading && comparisonData.length === 0) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="city-comparison">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Multi-City Comparison</h1>
        <p className="page-description">Compare air quality across different cities (Last 7 days average)</p>
      </div>

      {/* City Selector */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h3>Select Cities (Max 10)</h3>
          <span style={{ fontSize: '14px', color: '#6b7280' }}>
            {selectedCities.length} selected
          </span>
        </div>
        <div style={{ 
          display: 'flex', 
          flexWrap: 'wrap', 
          gap: '8px',
          padding: '16px' 
        }}>
          {cities.map(cityObj => (
            <button
              key={cityObj.city}
              onClick={() => handleCityToggle(cityObj.city)}
              style={{
                padding: '8px 16px',
                borderRadius: '20px',
                border: selectedCities.includes(cityObj.city) ? '2px solid #3b82f6' : '2px solid #e5e7eb',
                backgroundColor: selectedCities.includes(cityObj.city) ? '#eff6ff' : '#fff',
                color: selectedCities.includes(cityObj.city) ? '#3b82f6' : '#6b7280',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: 500,
                transition: 'all 0.2s'
              }}
            >
              {cityObj.city}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="error-message">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* View Mode Selector */}
      <div style={{ 
        display: 'flex', 
        gap: '12px', 
        marginBottom: '24px',
        justifyContent: 'center'
      }}>
        {['bar', 'radar', 'table'].map(mode => (
          <button
            key={mode}
            onClick={() => setViewMode(mode)}
            style={{
              padding: '8px 24px',
              borderRadius: '8px',
              border: viewMode === mode ? 'none' : '1px solid #e5e7eb',
              backgroundColor: viewMode === mode ? '#3b82f6' : '#fff',
              color: viewMode === mode ? '#fff' : '#6b7280',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: 500,
              textTransform: 'capitalize'
            }}
          >
            {mode} View
          </button>
        ))}
      </div>

      {comparisonData.length === 0 ? (
        <div className="card">
          <p style={{ textAlign: 'center', color: '#6b7280', padding: '40px' }}>
            Select at least one city to compare
          </p>
        </div>
      ) : (
        <>
          {/* Bar Chart View */}
          {viewMode === 'bar' && (
            <div className="card">
              <div className="card-header">
                <h3>Pollutant Comparison</h3>
              </div>
              <div style={{ padding: '16px' }}>
                <ResponsiveContainer width="100%" height={400}>
                  <BarChart data={comparisonData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="city" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="pm25" fill="#3b82f6" name="PM2.5" />
                    <Bar dataKey="pm10" fill="#8b5cf6" name="PM10" />
                    <Bar dataKey="no2" fill="#f97316" name="NO2" />
                    <Bar dataKey="aqi" fill="#ef4444" name="AQI" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Radar Chart View */}
          {viewMode === 'radar' && (
            <div className="card">
              <div className="card-header">
                <h3>Multi-Pollutant Radar</h3>
              </div>
              <div style={{ padding: '16px' }}>
                <ResponsiveContainer width="100%" height={500}>
                  <RadarChart data={comparisonData}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="city" />
                    <PolarRadiusAxis />
                    <Radar name="PM2.5" dataKey="pm25" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                    <Radar name="PM10" dataKey="pm10" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} />
                    <Radar name="NO2" dataKey="no2" stroke="#f97316" fill="#f97316" fillOpacity={0.3} />
                    <Legend />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* Table View */}
          {viewMode === 'table' && (
            <div className="card">
              <div className="card-header">
                <h3>Detailed Comparison</h3>
              </div>
              <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>City</th>
                      <th>AQI</th>
                      <th>Category</th>
                      <th>PM2.5</th>
                      <th>PM10</th>
                      <th>NO2</th>
                      <th>SO2</th>
                      <th>CO</th>
                      <th>O3</th>
                    </tr>
                  </thead>
                  <tbody>
                    {comparisonData
                      .sort((a, b) => b.aqi - a.aqi)
                      .map(city => (
                        <tr key={city.city}>
                          <td style={{ fontWeight: 600 }}>{city.city}</td>
                          <td>
                            <span style={{
                              display: 'inline-block',
                              padding: '4px 12px',
                              borderRadius: '12px',
                              backgroundColor: getAQIColor(city.aqi),
                              color: '#fff',
                              fontWeight: 600,
                              fontSize: '14px'
                            }}>
                              {city.aqi}
                            </span>
                          </td>
                          <td>{getAQICategory(city.aqi)}</td>
                          <td>{city.pm25}</td>
                          <td>{city.pm10}</td>
                          <td>{city.no2}</td>
                          <td>{city.so2}</td>
                          <td>{city.co}</td>
                          <td>{city.o3}</td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Rankings */}
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', 
            gap: '16px',
            marginTop: '24px'
          }}>
            <div className="card">
              <div className="card-header">
                <h3>Best Air Quality</h3>
              </div>
              <div style={{ padding: '16px' }}>
                {comparisonData
                  .sort((a, b) => a.aqi - b.aqi)
                  .slice(0, 3)
                  .map((city, index) => (
                    <div key={city.city} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px',
                      marginBottom: '8px',
                      backgroundColor: '#f9fafb',
                      borderRadius: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{
                          fontSize: '20px',
                          fontWeight: 700,
                          color: '#10b981'
                        }}>
                          #{index + 1}
                        </span>
                        <span style={{ fontWeight: 600 }}>{city.city}</span>
                      </div>
                      <div style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        backgroundColor: getAQIColor(city.aqi),
                        color: '#fff',
                        fontWeight: 600,
                        fontSize: '14px'
                      }}>
                        {city.aqi}
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h3>Worst Air Quality</h3>
              </div>
              <div style={{ padding: '16px' }}>
                {comparisonData
                  .sort((a, b) => b.aqi - a.aqi)
                  .slice(0, 3)
                  .map((city, index) => (
                    <div key={city.city} style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      padding: '12px',
                      marginBottom: '8px',
                      backgroundColor: '#f9fafb',
                      borderRadius: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{
                          fontSize: '20px',
                          fontWeight: 700,
                          color: '#ef4444'
                        }}>
                          #{index + 1}
                        </span>
                        <span style={{ fontWeight: 600 }}>{city.city}</span>
                      </div>
                      <div style={{
                        padding: '4px 12px',
                        borderRadius: '12px',
                        backgroundColor: getAQIColor(city.aqi),
                        color: '#fff',
                        fontWeight: 600,
                        fontSize: '14px'
                      }}>
                        {city.aqi}
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}

export default CityComparison;
