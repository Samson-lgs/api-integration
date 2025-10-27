/**
 * Stations Page
 * View and manage monitoring stations
 */

import { useState, useEffect } from 'react';
import { MapPin, AlertCircle, ExternalLink } from 'lucide-react';
import apiService from '../services/api';
import '../App.css';

function StationsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [stations, setStations] = useState([]);
  const [selectedStation, setSelectedStation] = useState(null);

  useEffect(() => {
    loadStations();
  }, []);

  const loadStations = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiService.getStations(true);
      setStations(response.data || []);
    } catch (err) {
      console.error('Failed to load stations:', err);
      setError('Failed to load stations. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const viewStationDetails = async (stationId) => {
    try {
      const response = await apiService.getStation(stationId);
      setSelectedStation(response);
    } catch (err) {
      console.error('Failed to load station details:', err);
      alert('Failed to load station details');
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
    <div className="stations-page">
      <div className="page-header">
        <h1 className="page-title">Monitoring Stations</h1>
        <p className="page-description">
          {stations.length} active monitoring stations across India
        </p>
      </div>

      <div className="grid grid-cols-2 gap-lg">
        {/* Stations List */}
        <div>
          <div className="data-table-container">
            <div className="table-header">
              <h3 className="mb-0">All Stations</h3>
              <button className="btn-primary" onClick={loadStations}>
                Refresh
              </button>
            </div>
            <div className="table-wrapper">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Station Name</th>
                    <th>City</th>
                    <th>State</th>
                    <th>Source</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {stations.map((station) => (
                    <tr key={station.station_id}>
                      <td className="font-medium">
                        <div className="flex items-center gap-sm">
                          <MapPin size={16} color="#64748b" />
                          {station.station_name}
                        </div>
                      </td>
                      <td>{station.city}</td>
                      <td>{station.state || 'N/A'}</td>
                      <td>
                        <span className="text-sm" style={{ 
                          padding: '0.25rem 0.5rem', 
                          backgroundColor: '#f1f5f9', 
                          borderRadius: '0.25rem' 
                        }}>
                          {station.data_source}
                        </span>
                      </td>
                      <td>
                        <button
                          className="btn-outline"
                          style={{ padding: '0.25rem 0.75rem', fontSize: '0.875rem' }}
                          onClick={() => viewStationDetails(station.station_id)}
                        >
                          <ExternalLink size={14} />
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Station Details */}
        <div>
          {selectedStation ? (
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">Station Details</h3>
              </div>
              <div>
                <table style={{ width: '100%' }}>
                  <tbody>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>Station ID:</td>
                      <td style={{ padding: '0.5rem' }}>{selectedStation.station?.station_id}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>Name:</td>
                      <td style={{ padding: '0.5rem' }}>{selectedStation.station?.station_name}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>City:</td>
                      <td style={{ padding: '0.5rem' }}>{selectedStation.station?.city}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>State:</td>
                      <td style={{ padding: '0.5rem' }}>{selectedStation.station?.state || 'N/A'}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>Location:</td>
                      <td style={{ padding: '0.5rem' }}>
                        {selectedStation.station?.latitude && selectedStation.station?.longitude
                          ? `${selectedStation.station.latitude}, ${selectedStation.station.longitude}`
                          : 'N/A'}
                      </td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>Data Source:</td>
                      <td style={{ padding: '0.5rem' }}>{selectedStation.station?.data_source}</td>
                    </tr>
                    <tr>
                      <td style={{ padding: '0.5rem', fontWeight: 600 }}>Status:</td>
                      <td style={{ padding: '0.5rem' }}>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          backgroundColor: selectedStation.station?.is_active ? '#dcfce7' : '#fee2e2',
                          color: selectedStation.station?.is_active ? '#065f46' : '#991b1b',
                          borderRadius: '0.25rem',
                          fontSize: '0.875rem'
                        }}>
                          {selectedStation.station?.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                    </tr>
                  </tbody>
                </table>

                {selectedStation.recent_readings && selectedStation.recent_readings.length > 0 && (
                  <>
                    <h4 className="mt-lg mb-md">Recent Readings</h4>
                    <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                      <table className="data-table">
                        <thead>
                          <tr>
                            <th>Pollutant</th>
                            <th>Value</th>
                            <th>AQI</th>
                            <th>Time</th>
                          </tr>
                        </thead>
                        <tbody>
                          {selectedStation.recent_readings.map((reading, index) => (
                            <tr key={index}>
                              <td>{reading.pollutant_id}</td>
                              <td>{reading.pollutant_avg?.toFixed(2)}</td>
                              <td className="font-semibold">{reading.aqi?.toFixed(0)}</td>
                              <td className="text-sm">
                                {reading.recorded_at ? new Date(reading.recorded_at).toLocaleString() : 'N/A'}
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  </>
                )}
              </div>
            </div>
          ) : (
            <div className="card text-center" style={{ padding: '3rem' }}>
              <MapPin size={48} color="#cbd5e1" style={{ margin: '0 auto 1rem' }} />
              <p className="text-muted">Select a station to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StationsPage;
