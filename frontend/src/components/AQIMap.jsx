/**
 * Interactive AQI Map Component
 * Real-time air quality map with color-coded markers
 */

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, CircleMarker, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import * as L from 'leaflet';

// Fix for default marker icons in React-Leaflet
if (L && L.Icon && L.Icon.Default && L.Icon.Default.prototype) {
  delete L.Icon.Default.prototype._getIconUrl;
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
  });
}

// AQI color mapping
const getAQIColor = (aqi) => {
  if (aqi <= 50) return '#00e400'; // Good
  if (aqi <= 100) return '#ffff00'; // Satisfactory
  if (aqi <= 200) return '#ff7e00'; // Moderate
  if (aqi <= 300) return '#ff0000'; // Poor
  if (aqi <= 400) return '#8f3f97'; // Very Poor
  return '#7e0023'; // Severe
};

const getAQICategory = (aqi) => {
  if (aqi <= 50) return 'Good';
  if (aqi <= 100) return 'Satisfactory';
  if (aqi <= 200) return 'Moderate';
  if (aqi <= 300) return 'Poor';
  if (aqi <= 400) return 'Very Poor';
  return 'Severe';
};

// Component to auto-fit bounds to markers
function MapBounds({ stations }) {
  const map = useMap();
  
  useEffect(() => {
    if (stations && stations.length > 0) {
      const bounds = stations
        .filter(s => s.latitude && s.longitude)
        .map(s => [s.latitude, s.longitude]);
      
      if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 10 });
      }
    }
  }, [stations, map]);
  
  return null;
}

function AQIMap({ data = [], height = '500px', autoRefresh = true, refreshInterval = 60000 }) {
  const [selectedStation, setSelectedStation] = useState(null);
  const [mapData, setMapData] = useState(data);
  const [mapError, setMapError] = useState(null);

  useEffect(() => {
    try {
      setMapData(data);
      setMapError(null);
    } catch (error) {
      console.error('Error setting map data:', error);
      setMapError(error.message);
    }
  }, [data]);

  // Auto-refresh functionality
  useEffect(() => {
    if (!autoRefresh) return;

    const interval = setInterval(() => {
      // Trigger parent component refresh
      // In a real implementation, this would call the API
      console.log('Auto-refreshing map data...');
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [autoRefresh, refreshInterval]);

  // Default center (India)
  const defaultCenter = [20.5937, 78.9629];
  const defaultZoom = 5;

  // Error state
  if (mapError) {
    return (
      <div style={{ 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#fee',
        borderRadius: '8px',
        border: '1px solid #fcc'
      }}>
        <p style={{ color: '#c00' }}>Map Error: {mapError}</p>
      </div>
    );
  }

  // Filter valid stations with coordinates
  const validStations = mapData.filter(
    station => station.latitude && station.longitude && !isNaN(station.latitude) && !isNaN(station.longitude)
  );

  if (validStations.length === 0) {
    return (
      <div style={{ 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f3f4f6',
        borderRadius: '8px'
      }}>
        <p style={{ color: '#6b7280' }}>No location data available</p>
      </div>
    );
  }

  try {
    return (
      <div style={{ height, borderRadius: '8px', overflow: 'hidden', position: 'relative' }}>
        <MapContainer
          center={defaultCenter}
          zoom={defaultZoom}
          style={{ height: '100%', width: '100%' }}
          scrollWheelZoom={true}
        >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapBounds stations={validStations} />

        {validStations.map((station, index) => {
          const aqi = station.aqi || 0;
          const color = getAQIColor(aqi);
          const category = getAQICategory(aqi);

          return (
            <CircleMarker
              key={station.station_id || index}
              center={[station.latitude, station.longitude]}
              radius={15}
              pathOptions={{
                fillColor: color,
                fillOpacity: 0.7,
                color: '#fff',
                weight: 2,
              }}
              eventHandlers={{
                click: () => setSelectedStation(station),
              }}
            >
              <Popup>
                <div style={{ minWidth: '200px' }}>
                  <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', fontWeight: 600 }}>
                    {station.station_name || station.city}
                  </h3>
                  <div style={{ marginBottom: '8px' }}>
                    <span style={{ 
                      display: 'inline-block',
                      padding: '4px 8px',
                      backgroundColor: color,
                      color: '#fff',
                      borderRadius: '4px',
                      fontSize: '12px',
                      fontWeight: 600
                    }}>
                      AQI: {aqi} ({category})
                    </span>
                  </div>
                  <div style={{ fontSize: '14px', color: '#4b5563' }}>
                    <p style={{ margin: '4px 0' }}>
                      <strong>PM2.5:</strong> {station.pm25?.toFixed(1) || 'N/A'} µg/m³
                    </p>
                    <p style={{ margin: '4px 0' }}>
                      <strong>PM10:</strong> {station.pm10?.toFixed(1) || 'N/A'} µg/m³
                    </p>
                    <p style={{ margin: '4px 0' }}>
                      <strong>NO2:</strong> {station.no2?.toFixed(1) || 'N/A'} µg/m³
                    </p>
                    {station.timestamp && (
                      <p style={{ margin: '8px 0 0 0', fontSize: '12px', color: '#9ca3af' }}>
                        Updated: {new Date(station.timestamp).toLocaleString()}
                      </p>
                    )}
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div style={{
        position: 'absolute',
        bottom: '20px',
        right: '20px',
        backgroundColor: 'white',
        padding: '12px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
        zIndex: 1000
      }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '12px', fontWeight: 600 }}>AQI Legend</h4>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
          {[
            { range: '0-50', label: 'Good', color: '#00e400' },
            { range: '51-100', label: 'Satisfactory', color: '#ffff00' },
            { range: '101-200', label: 'Moderate', color: '#ff7e00' },
            { range: '201-300', label: 'Poor', color: '#ff0000' },
            { range: '301-400', label: 'Very Poor', color: '#8f3f97' },
            { range: '400+', label: 'Severe', color: '#7e0023' },
          ].map(item => (
            <div key={item.range} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <div style={{
                width: '16px',
                height: '16px',
                borderRadius: '50%',
                backgroundColor: item.color,
                border: '2px solid #fff'
              }} />
              <span style={{ fontSize: '11px', color: '#4b5563' }}>
                {item.range}: {item.label}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
  } catch (error) {
    console.error('Map rendering error:', error);
    return (
      <div style={{ 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#fee',
        borderRadius: '8px',
        border: '1px solid #fcc',
        flexDirection: 'column',
        gap: '10px'
      }}>
        <p style={{ color: '#c00', fontWeight: 'bold' }}>Map Failed to Load</p>
        <p style={{ color: '#666', fontSize: '0.9em' }}>{error.message}</p>
        <button 
          onClick={() => window.location.reload()} 
          style={{
            padding: '8px 16px',
            backgroundColor: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer'
          }}
        >
          Reload Page
        </button>
      </div>
    );
  }
}

export default AQIMap;
