/**
 * API Service
 * Handles all HTTP requests to the Flask backend
 */

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const message = error.response?.data?.message || error.message || 'An error occurred';
    console.error('API Error:', message);
    return Promise.reject(error);
  }
);

// ============================================================================
// API ENDPOINTS
// ============================================================================

export const apiService = {
  // Health & System
  health: () => api.get('/health'),
  
  // Stations
  getStations: (activeOnly = true) => api.get('/stations', { params: { active_only: activeOnly } }),
  getStation: (stationId) => api.get(`/stations/${stationId}`),
  getCities: () => api.get('/cities'),
  
  // Data
  getLatestData: (params = {}) => api.get('/data/latest', { params }),
  getStationData: (stationId, hours = 24) => api.get(`/data/station/${stationId}`, { params: { hours } }),
  getCityData: (city, limit = 100) => api.get(`/data/city/${city}`, { params: { limit } }),
  getTimeSeriesData: (stationId, pollutantId = 'PM2.5', days = 7) => 
    api.get('/data/timeseries', { params: { station_id: stationId, pollutant_id: pollutantId, days } }),
  
  // Predictions
  predict: (data) => api.post('/predict', data),
  getPredictions: (hoursAhead = 24) => api.get('/predictions', { params: { hours_ahead: hoursAhead } }),
  getStationPredictions: (stationId, hoursAhead = 24) => 
    api.get(`/predictions/${stationId}`, { params: { hours_ahead: hoursAhead } }),
  
  // Analytics
  getSummary: () => api.get('/analytics/summary'),
  getCityAnalytics: (city) => api.get(`/analytics/city/${city}`),
  getTrends: (pollutantId = 'PM2.5', days = 7) => 
    api.get('/analytics/trends', { params: { pollutant_id: pollutantId, days } }),
  
  // Admin
  refreshViews: () => api.post('/admin/refresh-views'),
  getModelsInfo: () => api.get('/admin/models'),
  
  // Alerts
  getAlertSettings: () => api.get('/alerts/settings'),
  updateAlertEmail: (email) => api.post('/alerts/email', { email }),
  createAlert: (alertData) => api.post('/alerts', alertData),
  updateAlert: (alertId, data) => api.put(`/alerts/${alertId}`, data),
  deleteAlert: (alertId) => api.delete(`/alerts/${alertId}`),
  testAlert: (alertId) => api.post(`/alerts/${alertId}/test`),
};

export default apiService;
