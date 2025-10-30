/**
 * Alert Settings Component
 * Configure email alerts for AQI thresholds
 */

import { useState, useEffect } from 'react';
import { Bell, Mail, Save, Trash2, Plus, CheckCircle } from 'lucide-react';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import apiService from '../services/api';

function AlertSettings() {
  const [email, setEmail] = useState('');
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [newAlert, setNewAlert] = useState({
    city: '',
    threshold: 100,
    frequency: 'once', // 'once', 'hourly', 'daily'
    enabled: true
  });
  const [cities, setCities] = useState([]);

  useEffect(() => {
    loadCities();
    loadAlertSettings();
  }, []);

  const loadCities = async () => {
    try {
      const response = await apiService.getCities();
      setCities(response.data || []);
    } catch (err) {
      console.error('Failed to load cities:', err);
    }
  };

  const loadAlertSettings = async () => {
    try {
      const response = await apiService.getAlertSettings();
      if (response.status === 'success') {
        setEmail(response.data.email || '');
        setAlerts(response.data.alerts || []);
      }
    } catch (err) {
      console.error('Failed to load alert settings:', err);
      // Initialize empty if no settings exist
      setAlerts([]);
    }
  };

  const handleSaveEmail = async () => {
    if (!email || !email.includes('@')) {
      toast.error('Please enter a valid email address');
      return;
    }

    try {
      setLoading(true);
      await apiService.updateAlertEmail(email);
      toast.success('Email saved successfully!');
    } catch (err) {
      toast.error('Failed to save email');
    } finally {
      setLoading(false);
    }
  };

  const handleAddAlert = async () => {
    if (!newAlert.city) {
      toast.error('Please select a city');
      return;
    }

    if (!email) {
      toast.error('Please save your email address first');
      return;
    }

    try {
      setLoading(true);
      const response = await apiService.createAlert(newAlert);
      
      if (response.status === 'success') {
        setAlerts([...alerts, response.data]);
        setNewAlert({
          city: '',
          threshold: 100,
          frequency: 'once',
          enabled: true
        });
        toast.success('Alert created successfully!');
      }
    } catch (err) {
      toast.error('Failed to create alert');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAlert = async (alertId) => {
    try {
      setLoading(true);
      await apiService.deleteAlert(alertId);
      setAlerts(alerts.filter(a => a.id !== alertId));
      toast.success('Alert deleted');
    } catch (err) {
      toast.error('Failed to delete alert');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleAlert = async (alertId, enabled) => {
    try {
      await apiService.updateAlert(alertId, { enabled });
      setAlerts(alerts.map(a => 
        a.id === alertId ? { ...a, enabled } : a
      ));
      toast.success(enabled ? 'Alert enabled' : 'Alert disabled');
    } catch (err) {
      toast.error('Failed to update alert');
    }
  };

  const getThresholdColor = (threshold) => {
    if (threshold <= 50) return '#10b981';
    if (threshold <= 100) return '#fbbf24';
    if (threshold <= 200) return '#f97316';
    if (threshold <= 300) return '#ef4444';
    return '#991b1b';
  };

  const getThresholdCategory = (threshold) => {
    if (threshold <= 50) return 'Good';
    if (threshold <= 100) return 'Satisfactory';
    if (threshold <= 200) return 'Moderate';
    if (threshold <= 300) return 'Poor';
    return 'Very Poor+';
  };

  return (
    <div className="alert-settings">
      <ToastContainer position="top-right" autoClose={3000} />
      
      {/* Page Header */}
      <div className="page-header">
        <h1 className="page-title">Alert Settings</h1>
        <p className="page-description">Configure email notifications for air quality thresholds</p>
      </div>

      {/* Email Configuration */}
      <div className="card">
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Mail size={20} />
            Email Configuration
          </h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
            <div style={{ flex: 1 }}>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontSize: '14px', 
                fontWeight: 500, 
                color: '#374151'
              }}>
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your.email@example.com"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
            </div>
            <button
              onClick={handleSaveEmail}
              disabled={loading}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '10px 20px',
                backgroundColor: '#3b82f6',
                color: '#fff',
                border: 'none',
                borderRadius: '6px',
                cursor: 'pointer',
                fontWeight: 500,
                fontSize: '14px'
              }}
            >
              <Save size={16} />
              Save Email
            </button>
          </div>
          <p style={{ 
            margin: '12px 0 0 0', 
            fontSize: '13px', 
            color: '#6b7280'
          }}>
            You'll receive email notifications when AQI exceeds your configured thresholds
          </p>
        </div>
      </div>

      {/* Create New Alert */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Plus size={20} />
            Create New Alert
          </h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
            gap: '16px',
            marginBottom: '16px'
          }}>
            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontSize: '14px', 
                fontWeight: 500, 
                color: '#374151'
              }}>
                City
              </label>
              <select
                value={newAlert.city}
                onChange={(e) => setNewAlert({ ...newAlert, city: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="">Select City</option>
                {cities.map(cityObj => (
                  <option key={cityObj.city} value={cityObj.city}>
                    {cityObj.city}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontSize: '14px', 
                fontWeight: 500, 
                color: '#374151'
              }}>
                AQI Threshold
              </label>
              <input
                type="number"
                value={newAlert.threshold}
                onChange={(e) => setNewAlert({ ...newAlert, threshold: parseInt(e.target.value) })}
                min="0"
                max="500"
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              />
              <span style={{ 
                display: 'inline-block',
                marginTop: '4px',
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: getThresholdColor(newAlert.threshold),
                color: '#fff',
                fontSize: '12px',
                fontWeight: 600
              }}>
                {getThresholdCategory(newAlert.threshold)}
              </span>
            </div>

            <div>
              <label style={{ 
                display: 'block', 
                marginBottom: '8px', 
                fontSize: '14px', 
                fontWeight: 500, 
                color: '#374151'
              }}>
                Frequency
              </label>
              <select
                value={newAlert.frequency}
                onChange={(e) => setNewAlert({ ...newAlert, frequency: e.target.value })}
                style={{
                  width: '100%',
                  padding: '10px 12px',
                  border: '1px solid #d1d5db',
                  borderRadius: '6px',
                  fontSize: '14px'
                }}
              >
                <option value="once">Once (until resolved)</option>
                <option value="hourly">Hourly</option>
                <option value="daily">Daily</option>
              </select>
            </div>
          </div>

          <button
            onClick={handleAddAlert}
            disabled={loading || !email}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 20px',
              backgroundColor: '#10b981',
              color: '#fff',
              border: 'none',
              borderRadius: '6px',
              cursor: loading || !email ? 'not-allowed' : 'pointer',
              fontWeight: 500,
              fontSize: '14px',
              opacity: loading || !email ? 0.6 : 1
            }}
          >
            <Plus size={16} />
            Add Alert
          </button>
        </div>
      </div>

      {/* Active Alerts */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Bell size={20} />
            Active Alerts ({alerts.filter(a => a.enabled).length})
          </h3>
        </div>
        <div style={{ padding: '20px' }}>
          {alerts.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#6b7280', padding: '20px' }}>
              No alerts configured. Create your first alert above.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {alerts.map(alert => (
                <div 
                  key={alert.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '16px',
                    backgroundColor: alert.enabled ? '#f9fafb' : '#f3f4f6',
                    borderRadius: '8px',
                    border: `2px solid ${alert.enabled ? getThresholdColor(alert.threshold) : '#e5e7eb'}`
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flex: 1 }}>
                    <div style={{
                      padding: '8px',
                      backgroundColor: alert.enabled ? `${getThresholdColor(alert.threshold)}20` : '#e5e7eb',
                      borderRadius: '8px',
                      color: alert.enabled ? getThresholdColor(alert.threshold) : '#9ca3af'
                    }}>
                      <Bell size={20} />
                    </div>
                    
                    <div style={{ flex: 1 }}>
                      <h4 style={{ margin: '0 0 4px 0', fontSize: '16px', fontWeight: 600, color: '#1f2937' }}>
                        {alert.city}
                      </h4>
                      <p style={{ margin: 0, fontSize: '14px', color: '#6b7280' }}>
                        Alert when AQI exceeds <strong>{alert.threshold}</strong> ({getThresholdCategory(alert.threshold)})
                        {' • '}Notify {alert.frequency}
                      </p>
                    </div>
                  </div>

                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <button
                      onClick={() => handleToggleAlert(alert.id, !alert.enabled)}
                      style={{
                        padding: '8px 16px',
                        backgroundColor: alert.enabled ? '#fbbf24' : '#10b981',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '13px',
                        fontWeight: 500
                      }}
                    >
                      {alert.enabled ? 'Disable' : 'Enable'}
                    </button>
                    
                    <button
                      onClick={() => handleDeleteAlert(alert.id)}
                      style={{
                        padding: '8px',
                        backgroundColor: '#ef4444',
                        color: '#fff',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center'
                      }}
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Information */}
      <div className="card" style={{ marginTop: '24px', backgroundColor: '#eff6ff', border: '1px solid #3b82f6' }}>
        <div style={{ padding: '20px' }}>
          <h4 style={{ margin: '0 0 12px 0', fontSize: '16px', fontWeight: 600, color: '#1e40af', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CheckCircle size={20} />
            How Email Alerts Work
          </h4>
          <ul style={{ margin: 0, paddingLeft: '20px', color: '#1e3a8a', lineHeight: '1.8' }}>
            <li>You'll receive an email when AQI in your selected city exceeds the threshold</li>
            <li>"Once" frequency: Alert sent once when threshold is crossed, then paused until AQI drops below threshold</li>
            <li>"Hourly" frequency: Alert sent every hour while AQI is above threshold</li>
            <li>"Daily" frequency: Alert sent once per day while AQI is above threshold</li>
            <li>Disable alerts temporarily without deleting them</li>
            <li>You can configure multiple alerts for different cities and thresholds</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default AlertSettings;
