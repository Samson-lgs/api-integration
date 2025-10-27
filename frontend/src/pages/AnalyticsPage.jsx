/**
 * Analytics Page
 * Advanced analytics and trends visualization
 */

import { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, AlertCircle, Calendar } from 'lucide-react';
import { format } from 'date-fns';
import apiService from '../services/api';
import '../App.css';

const COLORS = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [trends, setTrends] = useState([]);
  const [cities, setCities] = useState([]);
  const [selectedCity, setSelectedCity] = useState('');
  const [cityAnalytics, setCityAnalytics] = useState(null);
  const [pollutant, setPollutant] = useState('PM2.5');
  const [days, setDays] = useState(7);

  useEffect(() => {
    loadAnalytics();
  }, [pollutant, days]);

  useEffect(() => {
    if (selectedCity) {
      loadCityAnalytics();
    }
  }, [selectedCity]);

  const loadAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const [trendsResponse, citiesResponse] = await Promise.all([
        apiService.getTrends(pollutant, days),
        apiService.getCities()
      ]);

      setTrends(trendsResponse.data || []);
      setCities(citiesResponse.data || []);
    } catch (err) {
      console.error('Failed to load analytics:', err);
      setError('Failed to load analytics data');
    } finally {
      setLoading(false);
    }
  };

  const loadCityAnalytics = async () => {
    try {
      const response = await apiService.getCityAnalytics(selectedCity);
      setCityAnalytics(response.analytics);
    } catch (err) {
      console.error('Failed to load city analytics:', err);
      setCityAnalytics(null);
    }
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
    <div className="analytics-page">
      <div className="page-header">
        <h1 className="page-title">Analytics & Trends</h1>
        <p className="page-description">
          Comprehensive air quality analytics and insights
        </p>
      </div>

      {/* Filters */}
      <div className="filters mb-lg">
        <div className="filter-group">
          <label htmlFor="pollutant">Pollutant</label>
          <select
            id="pollutant"
            value={pollutant}
            onChange={(e) => setPollutant(e.target.value)}
          >
            <option value="PM2.5">PM2.5</option>
            <option value="PM10">PM10</option>
            <option value="NO2">NO2</option>
            <option value="SO2">SO2</option>
            <option value="CO">CO</option>
            <option value="O3">O3</option>
          </select>
        </div>
        <div className="filter-group">
          <label htmlFor="days">Time Period</label>
          <select
            id="days"
            value={days}
            onChange={(e) => setDays(parseInt(e.target.value))}
          >
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>
        <div className="filter-group">
          <label htmlFor="city">Analyze City</label>
          <select
            id="city"
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
          >
            <option value="">Select a city...</option>
            {cities.map((city) => (
              <option key={city.city} value={city.city}>
                {city.city}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* City Analytics Card */}
      {cityAnalytics && (
        <div className="card mb-lg">
          <div className="card-header">
            <h3 className="card-title">{selectedCity} - Summary Statistics</h3>
          </div>
          <div className="grid grid-cols-4 gap-md">
            <div>
              <p className="text-sm text-muted mb-sm">Total Stations</p>
              <p className="text-xl font-bold">{cityAnalytics.total_stations || 0}</p>
            </div>
            <div>
              <p className="text-sm text-muted mb-sm">Average AQI</p>
              <p className="text-xl font-bold">{cityAnalytics.avg_aqi?.toFixed(1) || 'N/A'}</p>
            </div>
            <div>
              <p className="text-sm text-muted mb-sm">Max AQI</p>
              <p className="text-xl font-bold" style={{ color: '#ef4444' }}>
                {cityAnalytics.max_aqi?.toFixed(0) || 'N/A'}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted mb-sm">Last Updated</p>
              <p className="text-sm">
                {cityAnalytics.last_updated ? format(new Date(cityAnalytics.last_updated), 'MMM dd, HH:mm') : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Trends Charts */}
      <div className="grid grid-cols-2 gap-lg">
        {/* Average Concentration Trend */}
        <div className="chart-container">
          <div className="chart-header">
            <h3 className="chart-title">
              <TrendingUp size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              {pollutant} Concentration Trends
            </h3>
            <p className="text-sm text-muted">Average daily concentrations</p>
          </div>
          {trends.length > 0 ? (
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
                  name={`Avg ${pollutant} (µg/m³)`}
                  dot={{ fill: '#2563eb' }}
                />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-muted" style={{ padding: '3rem' }}>
              No trend data available
            </div>
          )}
        </div>

        {/* Min/Max Concentration */}
        <div className="chart-container">
          <div className="chart-header">
            <h3 className="chart-title">
              <Calendar size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Daily Range
            </h3>
            <p className="text-sm text-muted">Minimum and maximum concentrations</p>
          </div>
          {trends.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={trends}>
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
                <Bar dataKey="min_concentration" fill="#10b981" name="Min" />
                <Bar dataKey="max_concentration" fill="#ef4444" name="Max" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-muted" style={{ padding: '3rem' }}>
              No range data available
            </div>
          )}
        </div>
      </div>

      {/* Cities Distribution */}
      <div className="chart-container mt-lg">
        <div className="chart-header">
          <h3 className="chart-title">Cities Overview</h3>
          <p className="text-sm text-muted">Monitoring stations distribution</p>
        </div>
        {cities.length > 0 ? (
          <div className="grid grid-cols-2 gap-lg">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={cities.slice(0, 6)}
                  dataKey="station_count"
                  nameKey="city"
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  label={(entry) => `${entry.city}: ${entry.station_count}`}
                >
                  {cities.slice(0, 6).map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            
            <div>
              <h4 className="mb-md">All Cities</h4>
              <div style={{ maxHeight: '250px', overflowY: 'auto' }}>
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>City</th>
                      <th>Stations</th>
                    </tr>
                  </thead>
                  <tbody>
                    {cities.map((city, index) => (
                      <tr key={index}>
                        <td className="font-medium">{city.city}</td>
                        <td>{city.station_count}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="text-center text-muted" style={{ padding: '3rem' }}>
            No city data available
          </div>
        )}
      </div>
    </div>
  );
}

export default AnalyticsPage;
