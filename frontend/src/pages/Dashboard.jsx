/**
 * Dashboard Page
 * Main dashboard with real-time data, stats, and charts
 */

import { useState, useEffect } from 'react';
import { AlertCircle, MapPin, Activity, TrendingUp, Droplets } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { format } from 'date-fns';
import apiService from '../services/api';
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

      // Load all data in parallel
      const [latestResponse, summaryResponse, trendsResponse, citiesResponse] = await Promise.all([
        apiService.getLatestData({ limit: 20, city: selectedCity || undefined }),
        apiService.getSummary(),
        apiService.getTrends('PM2.5', 7),
        apiService.getCities()
      ]);

      setLatestData(latestResponse.data || []);
      setSummary(summaryResponse.summary || {});
      setTrends(trendsResponse.data || []);
      setCities(citiesResponse.data || []);
    } catch (err) {
      console.error('Failed to load dashboard data:', err);
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
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-message">
        <AlertCircle size={20} />
        {error}
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
          <span className="text-sm text-muted">{latestData.length} readings</span>
        </div>
        <div className="table-wrapper">
          <table className="data-table">
            <thead>
              <tr>
                <th>Station</th>
                <th>City</th>
                <th>Pollutant</th>
                <th>Value</th>
                <th>AQI</th>
                <th>Category</th>
                <th>Temperature</th>
                <th>Humidity</th>
                <th>Time</th>
              </tr>
            </thead>
            <tbody>
              {latestData.length > 0 ? (
                latestData.map((reading, index) => (
                  <tr key={index}>
                    <td className="font-medium">{reading.station_name}</td>
                    <td>{reading.city}</td>
                    <td>{reading.pollutant_id}</td>
                    <td>{reading.pollutant_avg?.toFixed(2) || 'N/A'}</td>
                    <td className="font-semibold">{reading.aqi?.toFixed(0) || 'N/A'}</td>
                    <td>
                      <span className={getAqiBadgeClass(reading.aqi_category)}>
                        {reading.aqi_category || 'Unknown'}
                      </span>
                    </td>
                    <td>{reading.temperature ? `${reading.temperature.toFixed(1)}°C` : 'N/A'}</td>
                    <td>{reading.humidity ? `${reading.humidity.toFixed(0)}%` : 'N/A'}</td>
                    <td className="text-sm text-muted">
                      {reading.recorded_at ? format(new Date(reading.recorded_at), 'HH:mm:ss') : 'N/A'}
                    </td>
                  </tr>
                ))
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
