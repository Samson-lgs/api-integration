/**
 * Dashboard Page
 * Main dashboard with real-time data, stats, and charts
 */

import { useState, useEffect } from 'react';
import { AlertCircle, MapPin, Activity, TrendingUp, Droplets } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import apiService from '../services/api';
// import AQIMap from '../components/AQIMap'; // DISABLED - causing crashes
import HealthImpact from '../components/HealthImpact';
import '../App.css';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [latestData, setLatestData] = useState([]);
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [cities, setCities] = useState([]);

  useEffect(() => {
    loadDashboardData();
  }, [selectedCity]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      console.log('Loading dashboard data...');

      // Load all data in parallel
      const [latestResponse, summaryResponse, trendsResponse, citiesResponse] = await Promise.all([
        apiService.getLatestData({ limit: 20, city: selectedCity || undefined }),
        apiService.getSummary(),
        apiService.getTrends('PM2.5', 7),
        apiService.getCities()
      ]);

      console.log('API Responses:', {
        latest: latestResponse,
        summary: summaryResponse,
        trends: trendsResponse,
        cities: citiesResponse
      });

      setLatestData(latestResponse.data || []);
      setSummary(summaryResponse.summary || {});
      setTrends(trendsResponse.data || []);
      setCities(citiesResponse.data || []);
      
      console.log('Data loaded successfully');
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
      console.error('Error details:', err.response || err.message);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
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
        <p style={{ marginTop: '1rem', color: '#6b7280' }}>Loading dashboard data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <AlertCircle size={20} />
        <div>
          <p>{error}</p>
          <button 
            onClick={loadDashboardData}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  // Safety check for data
  if (!summary || !Array.isArray(latestData) || !Array.isArray(trends) || !Array.isArray(cities)) {
    console.error('Invalid data structure:', { summary, latestData, trends, cities });
    return (
      <div className="error-message">
        <AlertCircle size={20} />
        <div>
          <p>Invalid data received from server</p>
          <button 
            onClick={loadDashboardData}
            style={{
              marginTop: '1rem',
              padding: '0.5rem 1rem',
              backgroundColor: '#2563eb',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Dashboard</h1>
        <p className="page-description">Real-time air quality monitoring and analytics</p>
      </div>

      {/* Stats Grid */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Total Stations</span>
            <div className="stat-card-icon" style={{ backgroundColor: '#dbeafe', color: '#2563eb' }}>
              <MapPin size={20} />
            </div>
          </div>
          <div className="stat-card-value">{summary?.total_stations || 0}</div>
          <div className="stat-card-label">Monitoring locations</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Total Readings</span>
            <div className="stat-card-icon" style={{ backgroundColor: '#dcfce7', color: '#10b981' }}>
              <Activity size={20} />
            </div>
          </div>
          <div className="stat-card-value">{summary?.total_readings?.toLocaleString() || 0}</div>
          <div className="stat-card-label">Data points collected</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Cities Covered</span>
            <div className="stat-card-icon" style={{ backgroundColor: '#fef3c7', color: '#f59e0b' }}>
              <TrendingUp size={20} />
            </div>
          </div>
          <div className="stat-card-value">{summary?.cities_covered || 0}</div>
          <div className="stat-card-label">Across India</div>
        </div>

        <div className="stat-card">
          <div className="stat-card-header">
            <span className="stat-card-title">Last Updated</span>
            <div className="stat-card-icon" style={{ backgroundColor: '#e0e7ff', color: '#6366f1' }}>
              <Droplets size={20} />
            </div>
          </div>
          <div className="stat-card-value" style={{ fontSize: '1.25rem' }}>
            {summary?.latest_reading ? format(new Date(summary.latest_reading), 'HH:mm') : 'N/A'}
          </div>
          <div className="stat-card-label">
            {summary?.latest_reading ? format(new Date(summary.latest_reading), 'MMM dd, yyyy') : 'No data'}
          </div>
        </div>
      </div>

      {/* Real-time AQI Map - Placeholder */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3 className="chart-title">Station Locations</h3>
          <p className="text-sm text-muted">Monitoring stations across India</p>
        </div>
        <div style={{ padding: '16px' }}>
          <div style={{ 
            height: '400px', 
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))',
            gap: '12px',
            overflowY: 'auto',
            padding: '8px',
            backgroundColor: '#f9fafb',
            borderRadius: '8px'
          }}>
            {latestData && latestData.length > 0 ? (
              latestData.map((station) => {
                const aqiColor = 
                  station.aqi <= 50 ? '#10b981' :
                  station.aqi <= 100 ? '#fbbf24' :
                  station.aqi <= 200 ? '#f97316' :
                  station.aqi <= 300 ? '#ef4444' :
                  station.aqi <= 400 ? '#8b5cf6' : '#991b1b';
                
                return (
                  <div 
                    key={station.id} 
                    style={{
                      padding: '12px',
                      backgroundColor: 'white',
                      borderRadius: '6px',
                      borderLeft: `4px solid ${aqiColor}`,
                      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
                    }}
                  >
                    <div style={{ fontWeight: '600', fontSize: '0.9rem', marginBottom: '4px' }}>
                      {station.name}
                    </div>
                    <div style={{ fontSize: '0.8rem', color: '#6b7280', marginBottom: '8px' }}>
                      {station.city}
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <div style={{
                        fontSize: '1.2rem',
                        fontWeight: 'bold',
                        color: aqiColor
                      }}>
                        {station.aqi}
                      </div>
                      <div style={{ fontSize: '0.75rem', color: '#9ca3af' }}>
                        PM2.5: {station.pm25?.toFixed(1)}
                      </div>
                    </div>
                  </div>
                );
              })
            ) : (
              <p style={{ color: '#6b7280', gridColumn: '1 / -1', textAlign: 'center' }}>
                No station data available
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Health Impact for Worst City */}
      {latestData.length > 0 && (
        <div style={{ marginTop: '24px' }}>
          {(() => {
            const worstStation = latestData.reduce((max, station) => 
              (station.aqi || 0) > (max.aqi || 0) ? station : max
            , latestData[0]);
            
            return (
              <div className="card">
                <div className="card-header">
                  <h3 className="chart-title">Health Advisory - {worstStation.city}</h3>
                  <p className="text-sm text-muted">Current air quality health implications</p>
                </div>
                <div style={{ padding: '16px' }}>
                  <HealthImpact aqi={worstStation.aqi || 0} city={worstStation.city} />
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* PM2.5 Trends Chart */}
      {trends.length > 0 && (
        <div className="chart-container">
          <div className="chart-header">
            <h3 className="chart-title">PM2.5 Trends (7 Days)</h3>
            <p className="text-sm text-muted">Average concentrations across all stations</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={trends}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis 
                dataKey="date" 
                tickFormatter={(date) => format(new Date(date), 'MMM dd')}
                stroke="#64748b"
              />
              <YAxis stroke="#64748b" />
              <Tooltip 
                labelFormatter={(date) => format(new Date(date), 'MMM dd, yyyy')}
                contentStyle={{ backgroundColor: 'white', border: '1px solid #e2e8f0', borderRadius: '0.5rem' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="avg_concentration" 
                stroke="#2563eb" 
                strokeWidth={2}
                name="Avg PM2.5 (µg/m³)"
                dot={{ fill: '#2563eb' }}
              />
              <Line 
                type="monotone" 
                dataKey="max_concentration" 
                stroke="#ef4444" 
                strokeWidth={2}
                name="Max PM2.5 (µg/m³)"
                dot={{ fill: '#ef4444' }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Filters */}
      <div className="filters">
        <div className="filter-group">
          <label htmlFor="city-filter">Filter by City</label>
          <select
            id="city-filter"
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
          >
            <option value="">All Cities</option>
            {cities.map((city) => (
              <option key={city.city} value={city.city}>
                {city.city} ({city.station_count} stations)
              </option>
            ))}
          </select>
        </div>
        <div className="filter-group">
          <label>&nbsp;</label>
          <button className="btn-primary" onClick={loadDashboardData}>
            Refresh Data
          </button>
        </div>
      </div>

      {/* Latest Readings Table */}
      <div className="data-table-container">
        <div className="table-header">
          <h3 className="mb-0">Latest Air Quality Readings</h3>
          <span className="text-sm text-muted">{latestData.length} stations</span>
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Station</th>
                <th>City</th>
                <th>AQI</th>
                <th>PM2.5</th>
                <th>PM10</th>
                <th>NO₂</th>
                <th>SO₂</th>
                <th>CO</th>
                <th>Last Updated</th>
              </tr>
            </thead>
            <tbody>
              {latestData.length > 0 ? (
                latestData.map((station, index) => {
                  const aqiCategory = 
                    station.aqi <= 50 ? 'Good' :
                    station.aqi <= 100 ? 'Satisfactory' :
                    station.aqi <= 200 ? 'Moderate' :
                    station.aqi <= 300 ? 'Poor' :
                    station.aqi <= 400 ? 'Very Poor' : 'Severe';
                  
                  return (
                    <tr key={station.id || index}>
                      <td className="font-medium">{station.name || 'N/A'}</td>
                      <td>{station.city || 'N/A'}</td>
                      <td className="font-semibold">{station.aqi || 'N/A'}</td>
                      <td>{station.pm25?.toFixed(2) || 'N/A'}</td>
                      <td>{station.pm10?.toFixed(2) || 'N/A'}</td>
                      <td>{station.no2?.toFixed(2) || 'N/A'}</td>
                      <td>{station.so2?.toFixed(2) || 'N/A'}</td>
                      <td>{station.co?.toFixed(2) || 'N/A'}</td>
                      <td className="text-sm text-muted">
                        {station.last_updated ? format(new Date(station.last_updated), 'MMM dd, HH:mm') : 'N/A'}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan="9" className="text-center text-muted">
                    No data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
