/**
 * Minimal Test App
 */

import { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';

function TestDashboard() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch('http://localhost:5000/api/analytics/summary')
      .then(res => res.json())
      .then(json => {
        console.log('Received data:', json);
        setData(json);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error:', err);
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) return <div style={{padding: '20px'}}>Loading...</div>;
  if (error) return <div style={{padding: '20px', color: 'red'}}>Error: {error}</div>;

  return (
    <div style={{padding: '20px'}}>
      <h1>Air Quality Dashboard</h1>
      <h2>Summary</h2>
      {data && data.summary && (
        <div>
          <p>Total Stations: {data.summary.total_stations}</p>
          <p>Average AQI: {data.summary.avg_aqi}</p>
          <p>Good: {data.summary.good}</p>
          <p>Moderate: {data.summary.moderate}</p>
          <p>Poor: {data.summary.poor}</p>
        </div>
      )}
    </div>
  );
}

function App() {
  return (
    <Router>
      <div style={{minHeight: '100vh', backgroundColor: '#f5f5f5'}}>
        <header style={{backgroundColor: '#2563eb', color: 'white', padding: '20px'}}>
          <h1>Air Quality Monitor - Test Mode</h1>
        </header>
        <Routes>
          <Route path="/" element={<TestDashboard />} />
          <Route path="*" element={<TestDashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
