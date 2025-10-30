/**
 * Main App Component
 * Root component with routing and layout
 */

import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Cloud, Activity, TrendingUp, MapPin, Settings, Bell, GitCompare } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import StationsPage from './pages/StationsPage';
import PredictionsPage from './pages/PredictionsPage';
import AnalyticsPage from './pages/AnalyticsPage';
import CityComparison from './pages/CityComparison';
import AlertSettings from './pages/AlertSettings';
import apiService from './services/api';

function App() {
  const [healthStatus, setHealthStatus] = useState(null);
  const [currentPage, setCurrentPage] = useState('dashboard');

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 60000); // Check every minute
    return () => clearInterval(interval);
  }, []);

  const checkHealth = async () => {
    try {
      const data = await apiService.health();
      console.log('Health check response:', data);
      // Backend returns {status: 'ok', message: '...', timestamp: '...'}
      setHealthStatus({ ...data, status: data.status === 'ok' ? 'healthy' : data.status });
    } catch (error) {
      console.error('Health check failed:', error);
      setHealthStatus({ status: 'error', message: 'API unreachable' });
    }
  };

  return (
    <Router>
      <div className="app">
        {/* Header */}
        <header className="header">
          <div className="container">
            <div className="flex items-center justify-between" style={{ padding: '1rem 0' }}>
              <div className="flex items-center gap-md">
                <Cloud size={32} color="#2563eb" />
                <div>
                  <h1 style={{ margin: 0, fontSize: '1.5rem' }}>Air Quality Monitor</h1>
                  <p className="text-sm text-muted" style={{ margin: 0 }}>
                    Real-time monitoring with ML predictions
                  </p>
                </div>
              </div>
              
              <div className="flex items-center gap-md">
                <div className={`status-indicator ${healthStatus?.status === 'healthy' ? 'status-healthy' : 'status-error'}`}>
                  <span className="status-dot"></span>
                  <span className="text-sm">{healthStatus?.status || 'Checking...'}</span>
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Navigation */}
        <nav className="nav">
          <div className="container">
            <div className="nav-links">
              <Link 
                to="/" 
                className={`nav-link ${currentPage === 'dashboard' ? 'active' : ''}`}
                onClick={() => setCurrentPage('dashboard')}
              >
                <Activity size={18} />
                Dashboard
              </Link>
              <Link 
                to="/stations" 
                className={`nav-link ${currentPage === 'stations' ? 'active' : ''}`}
                onClick={() => setCurrentPage('stations')}
              >
                <MapPin size={18} />
                Stations
              </Link>
              <Link 
                to="/predictions" 
                className={`nav-link ${currentPage === 'predictions' ? 'active' : ''}`}
                onClick={() => setCurrentPage('predictions')}
              >
                <TrendingUp size={18} />
                Predictions
              </Link>
              <Link 
                to="/analytics" 
                className={`nav-link ${currentPage === 'analytics' ? 'active' : ''}`}
                onClick={() => setCurrentPage('analytics')}
              >
                <Settings size={18} />
                Analytics
              </Link>
              <Link 
                to="/comparison" 
                className={`nav-link ${currentPage === 'comparison' ? 'active' : ''}`}
                onClick={() => setCurrentPage('comparison')}
              >
                <GitCompare size={18} />
                Compare Cities
              </Link>
              <Link 
                to="/alerts" 
                className={`nav-link ${currentPage === 'alerts' ? 'active' : ''}`}
                onClick={() => setCurrentPage('alerts')}
              >
                <Bell size={18} />
                Alerts
              </Link>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main className="main-content">
          <div className="container">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/stations" element={<StationsPage />} />
              <Route path="/predictions" element={<PredictionsPage />} />
              <Route path="/analytics" element={<AnalyticsPage />} />
              <Route path="/comparison" element={<CityComparison />} />
              <Route path="/alerts" element={<AlertSettings />} />
            </Routes>
          </div>
        </main>

        {/* Footer */}
        <footer className="footer">
          <div className="container">
            <div className="flex items-center justify-between">
              <p className="text-sm text-muted">
                © 2025 Air Quality Monitoring System. Built with React + Flask + PostgreSQL
              </p>
              <p className="text-sm text-muted">
                {healthStatus?.statistics?.total_stations || 0} stations · {healthStatus?.statistics?.total_readings || 0} readings
              </p>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
