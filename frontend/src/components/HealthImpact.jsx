/**
 * Health Impact Component
 * Display health implications and activity recommendations based on AQI
 */

import { AlertCircle, Heart, Activity, Home, Wind, Users, Shield } from 'lucide-react';

const healthData = {
  good: {
    range: '0-50',
    category: 'Good',
    color: '#10b981',
    icon: '😊',
    healthImplications: 'Air quality is satisfactory, and air pollution poses little or no risk.',
    generalAdvice: 'It\'s a great day to be active outside. Enjoy outdoor activities!',
    sensitiveGroups: 'Everyone can continue their outdoor activities normally.',
    recommendations: [
      { icon: Activity, text: 'Perfect for outdoor exercise', color: '#10b981' },
      { icon: Wind, text: 'Windows can be kept open', color: '#10b981' },
      { icon: Users, text: 'Safe for all age groups', color: '#10b981' },
      { icon: Heart, text: 'No health precautions needed', color: '#10b981' }
    ]
  },
  satisfactory: {
    range: '51-100',
    category: 'Satisfactory',
    color: '#fbbf24',
    icon: '🙂',
    healthImplications: 'Air quality is acceptable for most people. However, unusually sensitive individuals may experience minor respiratory symptoms.',
    generalAdvice: 'Enjoy your outdoor activities. Unusually sensitive people should consider limiting prolonged outdoor exertion.',
    sensitiveGroups: 'People with respiratory conditions should monitor their symptoms.',
    recommendations: [
      { icon: Activity, text: 'Outdoor activities are generally safe', color: '#fbbf24' },
      { icon: Wind, text: 'Ventilation is fine', color: '#fbbf24' },
      { icon: Users, text: 'Most people can continue normal activities', color: '#fbbf24' },
      { icon: Shield, text: 'Sensitive individuals: watch for symptoms', color: '#fbbf24' }
    ]
  },
  moderate: {
    range: '101-200',
    category: 'Moderate',
    color: '#f97316',
    icon: '😐',
    healthImplications: 'Members of sensitive groups may experience health effects. The general public is less likely to be affected.',
    generalAdvice: 'Active children and adults, and people with respiratory disease should limit prolonged outdoor exertion.',
    sensitiveGroups: 'People with heart or lung disease, older adults, children, and teenagers should limit outdoor activities.',
    recommendations: [
      { icon: Activity, text: 'Limit prolonged outdoor exercise', color: '#f97316' },
      { icon: Wind, text: 'Use air purifiers indoors', color: '#f97316' },
      { icon: Users, text: 'Sensitive groups: reduce exposure', color: '#f97316' },
      { icon: Shield, text: 'Consider wearing masks outdoors', color: '#f97316' }
    ]
  },
  poor: {
    range: '201-300',
    category: 'Poor',
    color: '#ef4444',
    icon: '😷',
    healthImplications: 'Everyone may begin to experience health effects. Members of sensitive groups may experience more serious health effects.',
    generalAdvice: 'People with heart or lung disease, older adults, children should avoid prolonged outdoor exertion. Everyone else should limit prolonged outdoor exertion.',
    sensitiveGroups: 'Sensitive groups should avoid all outdoor activities. General public should limit outdoor activities.',
    recommendations: [
      { icon: Activity, text: 'Avoid outdoor physical activities', color: '#ef4444' },
      { icon: Wind, text: 'Keep windows closed', color: '#ef4444' },
      { icon: Users, text: 'Children and elderly stay indoors', color: '#ef4444' },
      { icon: Shield, text: 'Wear N95 masks if going outside', color: '#ef4444' }
    ]
  },
  veryPoor: {
    range: '301-400',
    category: 'Very Poor',
    color: '#8b5cf6',
    icon: '😨',
    healthImplications: 'Health alert: The risk of health effects is increased for everyone. Sensitive groups should take extra precautions.',
    generalAdvice: 'Everyone should avoid all outdoor physical activity. People with heart or lung disease, older adults, children should remain indoors.',
    sensitiveGroups: 'Emergency conditions for sensitive groups. Everyone should avoid going outdoors.',
    recommendations: [
      { icon: Activity, text: 'Stay indoors, avoid all outdoor activities', color: '#8b5cf6' },
      { icon: Wind, text: 'Use air purifiers, keep windows closed', color: '#8b5cf6' },
      { icon: Users, text: 'All vulnerable groups stay home', color: '#8b5cf6' },
      { icon: Shield, text: 'N95/N99 masks essential if must go out', color: '#8b5cf6' }
    ]
  },
  severe: {
    range: '400+',
    category: 'Severe',
    color: '#991b1b',
    icon: '☠️',
    healthImplications: 'Health warning of emergency conditions: everyone is more likely to be affected. Serious health effects for all.',
    generalAdvice: 'Everyone should avoid all outdoor activities. Remain indoors and keep activity levels low. Follow guidelines from local health authorities.',
    sensitiveGroups: 'Emergency health warning. All populations at high risk. Seek medical attention if experiencing symptoms.',
    recommendations: [
      { icon: Activity, text: 'Complete outdoor activity ban', color: '#991b1b' },
      { icon: Wind, text: 'Seal windows, maximum air filtration', color: '#991b1b' },
      { icon: Users, text: 'Everyone stays indoors', color: '#991b1b' },
      { icon: Shield, text: 'Medical consultation recommended', color: '#991b1b' }
    ]
  }
};

function getHealthInfo(aqi) {
  if (aqi <= 50) return healthData.good;
  if (aqi <= 100) return healthData.satisfactory;
  if (aqi <= 200) return healthData.moderate;
  if (aqi <= 300) return healthData.poor;
  if (aqi <= 400) return healthData.veryPoor;
  return healthData.severe;
}

function HealthImpact({ aqi = 0, city = '' }) {
  const healthInfo = getHealthInfo(aqi);

  return (
    <div className="health-impact">
      {/* AQI Summary Card */}
      <div className="card" style={{ 
        border: `3px solid ${healthInfo.color}`,
        backgroundColor: `${healthInfo.color}10`
      }}>
        <div style={{ padding: '24px', textAlign: 'center' }}>
          <div style={{ fontSize: '48px', marginBottom: '12px' }}>
            {healthInfo.icon}
          </div>
          <h2 style={{ 
            margin: '0 0 8px 0', 
            fontSize: '32px',
            color: healthInfo.color,
            fontWeight: 700
          }}>
            {aqi}
          </h2>
          <div style={{
            display: 'inline-block',
            padding: '8px 16px',
            borderRadius: '20px',
            backgroundColor: healthInfo.color,
            color: '#fff',
            fontWeight: 600,
            fontSize: '16px',
            marginBottom: '8px'
          }}>
            {healthInfo.category}
          </div>
          {city && (
            <p style={{ margin: '8px 0 0 0', color: '#6b7280', fontSize: '14px' }}>
              Current air quality in {city}
            </p>
          )}
        </div>
      </div>

      {/* Health Implications */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Heart size={20} style={{ color: healthInfo.color }} />
            Health Implications
          </h3>
        </div>
        <div style={{ padding: '20px' }}>
          <p style={{ 
            fontSize: '16px', 
            lineHeight: '1.6', 
            color: '#374151',
            marginBottom: '16px'
          }}>
            {healthInfo.healthImplications}
          </p>
          
          <div style={{ 
            backgroundColor: '#f9fafb', 
            padding: '16px', 
            borderRadius: '8px',
            borderLeft: `4px solid ${healthInfo.color}`,
            marginBottom: '16px'
          }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 600, color: '#1f2937' }}>
              General Public
            </h4>
            <p style={{ margin: 0, fontSize: '14px', color: '#4b5563', lineHeight: '1.5' }}>
              {healthInfo.generalAdvice}
            </p>
          </div>

          <div style={{ 
            backgroundColor: '#fef3c7', 
            padding: '16px', 
            borderRadius: '8px',
            borderLeft: '4px solid #f59e0b'
          }}>
            <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', fontWeight: 600, color: '#1f2937' }}>
              Sensitive Groups (Children, Elderly, Respiratory/Heart Patients)
            </h4>
            <p style={{ margin: 0, fontSize: '14px', color: '#4b5563', lineHeight: '1.5' }}>
              {healthInfo.sensitiveGroups}
            </p>
          </div>
        </div>
      </div>

      {/* Activity Recommendations */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Activity size={20} style={{ color: healthInfo.color }} />
            Activity Recommendations
          </h3>
        </div>
        <div style={{ padding: '20px' }}>
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', 
            gap: '16px'
          }}>
            {healthInfo.recommendations.map((rec, index) => {
              const Icon = rec.icon;
              return (
                <div key={index} style={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: '12px',
                  padding: '16px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '8px',
                  border: `1px solid ${rec.color}20`
                }}>
                  <div style={{
                    padding: '8px',
                    backgroundColor: `${rec.color}20`,
                    borderRadius: '8px',
                    color: rec.color
                  }}>
                    <Icon size={20} />
                  </div>
                  <p style={{ 
                    margin: 0, 
                    fontSize: '14px', 
                    color: '#374151',
                    lineHeight: '1.5'
                  }}>
                    {rec.text}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Additional Health Tips */}
      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={20} style={{ color: '#6366f1' }} />
            Additional Health Tips
          </h3>
        </div>
        <div style={{ padding: '20px' }}>
          <ul style={{ 
            margin: 0, 
            paddingLeft: '20px', 
            lineHeight: '2',
            color: '#374151'
          }}>
            <li>Stay hydrated by drinking plenty of water</li>
            <li>Keep indoor air clean with air purifiers</li>
            <li>Avoid smoking and exposure to secondhand smoke</li>
            <li>Monitor local air quality forecasts regularly</li>
            <li>Have a supply of masks (N95/N99) at home</li>
            <li>Consult a doctor if you experience respiratory symptoms</li>
            <li>Keep emergency medications accessible</li>
            <li>Follow local health authority guidelines</li>
          </ul>
        </div>
      </div>

      {/* Emergency Contacts (for severe conditions) */}
      {aqi > 300 && (
        <div className="card" style={{ 
          marginTop: '24px',
          border: '2px solid #ef4444',
          backgroundColor: '#fef2f2'
        }}>
          <div className="card-header" style={{ backgroundColor: '#fee2e2' }}>
            <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#991b1b' }}>
              <AlertCircle size={20} />
              Emergency Alert
            </h3>
          </div>
          <div style={{ padding: '20px' }}>
            <p style={{ 
              margin: '0 0 12px 0', 
              fontSize: '16px', 
              fontWeight: 600, 
              color: '#991b1b'
            }}>
              Air quality is at hazardous levels. Immediate action required:
            </p>
            <ul style={{ margin: 0, paddingLeft: '20px', color: '#7f1d1d' }}>
              <li>Stay indoors with windows and doors closed</li>
              <li>Run air purifiers on maximum setting</li>
              <li>Avoid all outdoor activities</li>
              <li>Seek medical attention if experiencing symptoms</li>
              <li>Follow local emergency protocols</li>
            </ul>
            <div style={{ 
              marginTop: '16px', 
              padding: '12px', 
              backgroundColor: '#fff',
              borderRadius: '8px',
              border: '1px solid #fca5a5'
            }}>
              <p style={{ margin: 0, fontSize: '14px', color: '#7f1d1d' }}>
                <strong>Emergency Services:</strong> 108 (India) | <strong>Air Quality Hotline:</strong> 1800-xxx-xxxx
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default HealthImpact;
