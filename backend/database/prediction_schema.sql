-- Database Schema for AQI Prediction System
-- Stores raw data from APIs and ML predictions

-- Table for raw air quality data from multiple sources
CREATE TABLE IF NOT EXISTS raw_air_quality_data (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,  -- 'openweather', 'iqair', 'cpcb'
    city VARCHAR(100) NOT NULL,
    station_name VARCHAR(200),
    latitude FLOAT,
    longitude FLOAT,
    pm25 FLOAT,
    pm10 FLOAT,
    no2 FLOAT,
    so2 FLOAT,
    co FLOAT,
    o3 FLOAT,
    nh3 FLOAT,
    aqi INTEGER,
    timestamp TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(source, city, station_name, timestamp)
);

-- Indexes for faster queries
CREATE INDEX IF NOT EXISTS idx_raw_data_city_timestamp 
    ON raw_air_quality_data(city, timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_raw_data_timestamp 
    ON raw_air_quality_data(timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_raw_data_source 
    ON raw_air_quality_data(source);

-- Table for ML predictions
CREATE TABLE IF NOT EXISTS aqi_predictions (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    prediction_timestamp TIMESTAMPTZ NOT NULL,
    predicted_aqi FLOAT NOT NULL,
    hours_ahead INTEGER NOT NULL,
    model_type VARCHAR(50) NOT NULL,  -- 'linear', 'random_forest', 'xgboost', 'lstm'
    confidence_lower FLOAT,
    confidence_upper FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(city, prediction_timestamp, model_type)
);

-- Indexes for predictions
CREATE INDEX IF NOT EXISTS idx_predictions_city_timestamp 
    ON aqi_predictions(city, prediction_timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_predictions_timestamp 
    ON aqi_predictions(prediction_timestamp DESC);

-- Table for model metadata
CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    model_type VARCHAR(50) NOT NULL,
    model_version VARCHAR(50) NOT NULL,
    training_date TIMESTAMPTZ NOT NULL,
    mae FLOAT,
    rmse FLOAT,
    r2_score FLOAT,
    training_samples INTEGER,
    features_used TEXT[],
    is_active BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(model_type, model_version)
);

-- Table for data collection logs
CREATE TABLE IF NOT EXISTS collection_logs (
    id SERIAL PRIMARY KEY,
    source VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    status VARCHAR(20) NOT NULL,  -- 'success', 'failure'
    records_collected INTEGER DEFAULT 0,
    error_message TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Table for health alerts
CREATE TABLE IF NOT EXISTS health_alerts (
    id SERIAL PRIMARY KEY,
    city VARCHAR(100) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,  -- 'aqi_high', 'pollution_spike', etc.
    severity VARCHAR(20) NOT NULL,  -- 'moderate', 'unhealthy', 'hazardous'
    message TEXT NOT NULL,
    aqi_value INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    is_active BOOLEAN DEFAULT TRUE
);

-- Index for active alerts
CREATE INDEX IF NOT EXISTS idx_alerts_city_active 
    ON health_alerts(city, is_active, created_at DESC);

-- View for latest readings per city
CREATE OR REPLACE VIEW latest_city_readings AS
SELECT DISTINCT ON (city)
    city,
    source,
    pm25,
    pm10,
    no2,
    so2,
    co,
    o3,
    aqi,
    timestamp,
    latitude,
    longitude
FROM raw_air_quality_data
ORDER BY city, timestamp DESC;

-- View for latest predictions per city
CREATE OR REPLACE VIEW latest_city_predictions AS
SELECT DISTINCT ON (city, prediction_timestamp)
    city,
    prediction_timestamp,
    predicted_aqi,
    hours_ahead,
    model_type,
    created_at
FROM aqi_predictions
WHERE prediction_timestamp >= NOW()
ORDER BY city, prediction_timestamp, created_at DESC;

-- Function to calculate AQI category
CREATE OR REPLACE FUNCTION get_aqi_category(aqi_value INTEGER)
RETURNS VARCHAR(20) AS $$
BEGIN
    IF aqi_value <= 50 THEN
        RETURN 'Good';
    ELSIF aqi_value <= 100 THEN
        RETURN 'Moderate';
    ELSIF aqi_value <= 150 THEN
        RETURN 'Unhealthy for Sensitive Groups';
    ELSIF aqi_value <= 200 THEN
        RETURN 'Unhealthy';
    ELSIF aqi_value <= 300 THEN
        RETURN 'Very Unhealthy';
    ELSE
        RETURN 'Hazardous';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Function to get health recommendations
CREATE OR REPLACE FUNCTION get_health_recommendation(aqi_value INTEGER)
RETURNS TEXT AS $$
BEGIN
    IF aqi_value <= 50 THEN
        RETURN 'Air quality is satisfactory. Outdoor activities are safe.';
    ELSIF aqi_value <= 100 THEN
        RETURN 'Air quality is acceptable. Unusually sensitive people should limit outdoor exertion.';
    ELSIF aqi_value <= 150 THEN
        RETURN 'Sensitive groups should reduce prolonged outdoor exertion.';
    ELSIF aqi_value <= 200 THEN
        RETURN 'Everyone should reduce prolonged outdoor exertion.';
    ELSIF aqi_value <= 300 THEN
        RETURN 'Everyone should avoid prolonged outdoor exertion. Sensitive groups should remain indoors.';
    ELSE
        RETURN 'Health alert! Everyone should avoid outdoor activities.';
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Cleanup old data (keep last 90 days)
CREATE OR REPLACE FUNCTION cleanup_old_data()
RETURNS void AS $$
BEGIN
    DELETE FROM raw_air_quality_data 
    WHERE timestamp < NOW() - INTERVAL '90 days';
    
    DELETE FROM aqi_predictions 
    WHERE prediction_timestamp < NOW() - INTERVAL '30 days';
    
    DELETE FROM collection_logs 
    WHERE timestamp < NOW() - INTERVAL '30 days';
END;
$$ LANGUAGE plpgsql;

-- Grant permissions (adjust as needed for your setup)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO postgres;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO postgres;
