-- ============================================================================
-- AIR QUALITY MONITORING SYSTEM - OPTIMIZED POSTGRESQL SCHEMA
-- Time-series optimized database design for efficient storage and querying
-- ============================================================================

-- Drop existing tables (for clean setup)
DROP TABLE IF EXISTS predictions CASCADE;
DROP TABLE IF EXISTS air_quality_data CASCADE;
DROP TABLE IF EXISTS stations CASCADE;
DROP TABLE IF EXISTS pollutants CASCADE;
DROP TABLE IF EXISTS aqi_categories CASCADE;

-- Enable TimescaleDB extension for time-series optimization (optional but recommended)
-- CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;

-- ============================================================================
-- REFERENCE TABLES
-- ============================================================================

-- AQI Categories lookup table
CREATE TABLE aqi_categories (
    category_id SERIAL PRIMARY KEY,
    category_name VARCHAR(20) NOT NULL UNIQUE,
    min_aqi INTEGER NOT NULL,
    max_aqi INTEGER NOT NULL,
    color_code VARCHAR(7),
    health_advisory TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert standard AQI categories
INSERT INTO aqi_categories (category_name, min_aqi, max_aqi, color_code, health_advisory) VALUES
('Good', 0, 50, '#00E400', 'Air quality is satisfactory, and air pollution poses little or no risk.'),
('Satisfactory', 51, 100, '#FFFF00', 'Air quality is acceptable. However, there may be a risk for some people.'),
('Moderate', 101, 200, '#FF7E00', 'Members of sensitive groups may experience health effects.'),
('Poor', 201, 300, '#FF0000', 'Some members of the general public may experience health effects.'),
('Very Poor', 301, 400, '#8F3F97', 'Health alert: The risk of health effects is increased for everyone.'),
('Severe', 401, 500, '#7E0023', 'Health warning of emergency conditions. Everyone is more likely to be affected.');

-- Pollutants lookup table
CREATE TABLE pollutants (
    pollutant_id VARCHAR(10) PRIMARY KEY,
    pollutant_name VARCHAR(50) NOT NULL,
    unit VARCHAR(20) NOT NULL,
    safe_limit DECIMAL(10,2),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert common pollutants
INSERT INTO pollutants (pollutant_id, pollutant_name, unit, safe_limit, description) VALUES
('PM2.5', 'Particulate Matter 2.5', 'µg/m³', 60.0, 'Fine particles less than 2.5 micrometers'),
('PM10', 'Particulate Matter 10', 'µg/m³', 100.0, 'Particles less than 10 micrometers'),
('NO2', 'Nitrogen Dioxide', 'µg/m³', 80.0, 'Harmful gas from combustion'),
('SO2', 'Sulfur Dioxide', 'µg/m³', 80.0, 'Gas from burning fossil fuels'),
('CO', 'Carbon Monoxide', 'mg/m³', 2.0, 'Colorless, odorless toxic gas'),
('O3', 'Ozone', 'µg/m³', 100.0, 'Ground-level ozone'),
('NH3', 'Ammonia', 'µg/m³', 400.0, 'Pungent gas');

-- ============================================================================
-- MAIN TABLES
-- ============================================================================

-- Monitoring Stations
CREATE TABLE stations (
    station_id VARCHAR(50) PRIMARY KEY,
    station_name VARCHAR(200) NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'India',
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7),
    data_source VARCHAR(50) NOT NULL, -- 'CPCB', 'OpenWeather', etc.
    is_active BOOLEAN DEFAULT TRUE,
    last_updated TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB -- Additional station info
);

-- Indexes for stations
CREATE INDEX idx_stations_city ON stations(city);
CREATE INDEX idx_stations_state ON stations(state);
CREATE INDEX idx_stations_data_source ON stations(data_source);
CREATE INDEX idx_stations_location ON stations(latitude, longitude);
CREATE INDEX idx_stations_active ON stations(is_active);

-- Air Quality Time-Series Data (main table)
CREATE TABLE air_quality_data (
    id BIGSERIAL PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL REFERENCES stations(station_id) ON DELETE CASCADE,
    recorded_at TIMESTAMP NOT NULL,
    pollutant_id VARCHAR(10) NOT NULL REFERENCES pollutants(pollutant_id),
    pollutant_avg DECIMAL(10,2),
    pollutant_min DECIMAL(10,2),
    pollutant_max DECIMAL(10,2),
    aqi DECIMAL(10,2),
    aqi_category_id INTEGER REFERENCES aqi_categories(category_id),
    temperature DECIMAL(5,2), -- Celsius
    humidity DECIMAL(5,2), -- Percentage
    wind_speed DECIMAL(5,2), -- m/s
    wind_direction DECIMAL(5,2), -- Degrees
    pressure DECIMAL(7,2), -- hPa
    data_source VARCHAR(50),
    data_quality_flag VARCHAR(10) DEFAULT 'GOOD', -- GOOD, SUSPECT, INVALID
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Critical indexes for time-series queries
CREATE INDEX idx_aq_recorded_at ON air_quality_data(recorded_at DESC);
CREATE INDEX idx_aq_station_time ON air_quality_data(station_id, recorded_at DESC);
CREATE INDEX idx_aq_pollutant_time ON air_quality_data(pollutant_id, recorded_at DESC);
CREATE INDEX idx_aq_aqi_category ON air_quality_data(aqi_category_id);
CREATE INDEX idx_aq_data_source ON air_quality_data(data_source);
CREATE INDEX idx_aq_composite ON air_quality_data(station_id, pollutant_id, recorded_at DESC);

-- Composite index for common query patterns
CREATE INDEX idx_aq_city_time ON air_quality_data(station_id, recorded_at DESC) 
    WHERE aqi IS NOT NULL;

-- Convert to TimescaleDB hypertable for better time-series performance (optional)
-- SELECT create_hypertable('air_quality_data', 'recorded_at', chunk_time_interval => INTERVAL '7 days');

-- ============================================================================
-- ML PREDICTIONS TABLE
-- ============================================================================

-- Store ML model predictions
CREATE TABLE predictions (
    id BIGSERIAL PRIMARY KEY,
    station_id VARCHAR(50) NOT NULL REFERENCES stations(station_id),
    prediction_time TIMESTAMP NOT NULL,
    predicted_for TIMESTAMP NOT NULL, -- Future timestamp
    model_name VARCHAR(50) NOT NULL, -- 'Linear_Regression', 'Ensemble', etc.
    predicted_aqi DECIMAL(10,2),
    predicted_category_id INTEGER REFERENCES aqi_categories(category_id),
    confidence_lower DECIMAL(10,2),
    confidence_upper DECIMAL(10,2),
    model_version VARCHAR(20),
    features_used JSONB, -- Store input features
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for predictions
CREATE INDEX idx_pred_station_time ON predictions(station_id, predicted_for DESC);
CREATE INDEX idx_pred_model ON predictions(model_name);
CREATE INDEX idx_pred_prediction_time ON predictions(prediction_time DESC);

-- ============================================================================
-- MATERIALIZED VIEWS FOR PERFORMANCE
-- ============================================================================

-- Latest readings per station (refreshed periodically)
CREATE MATERIALIZED VIEW latest_station_readings AS
SELECT DISTINCT ON (station_id, pollutant_id)
    station_id,
    pollutant_id,
    recorded_at,
    pollutant_avg,
    aqi,
    aqi_category_id,
    temperature,
    humidity
FROM air_quality_data
ORDER BY station_id, pollutant_id, recorded_at DESC;

CREATE UNIQUE INDEX idx_latest_station_poll ON latest_station_readings(station_id, pollutant_id);

-- Daily aggregates for fast historical queries
CREATE MATERIALIZED VIEW daily_air_quality_stats AS
SELECT 
    station_id,
    pollutant_id,
    DATE(recorded_at) AS date,
    AVG(pollutant_avg) AS avg_pollutant,
    MIN(pollutant_avg) AS min_pollutant,
    MAX(pollutant_avg) AS max_pollutant,
    AVG(aqi) AS avg_aqi,
    MAX(aqi) AS max_aqi,
    AVG(temperature) AS avg_temp,
    AVG(humidity) AS avg_humidity,
    COUNT(*) AS reading_count
FROM air_quality_data
WHERE pollutant_avg IS NOT NULL
GROUP BY station_id, pollutant_id, DATE(recorded_at);

CREATE INDEX idx_daily_stats_station_date ON daily_air_quality_stats(station_id, date DESC);
CREATE INDEX idx_daily_stats_pollutant_date ON daily_air_quality_stats(pollutant_id, date DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to refresh materialized views
CREATE OR REPLACE FUNCTION refresh_materialized_views()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY latest_station_readings;
    REFRESH MATERIALIZED VIEW CONCURRENTLY daily_air_quality_stats;
END;
$$ LANGUAGE plpgsql;

-- Function to get AQI category from AQI value
CREATE OR REPLACE FUNCTION get_aqi_category(aqi_value DECIMAL)
RETURNS VARCHAR AS $$
DECLARE
    category VARCHAR(20);
BEGIN
    SELECT category_name INTO category
    FROM aqi_categories
    WHERE aqi_value BETWEEN min_aqi AND max_aqi
    LIMIT 1;
    
    RETURN COALESCE(category, 'Unknown');
END;
$$ LANGUAGE plpgsql;

-- Function to calculate AQI from pollutant concentration (simplified)
CREATE OR REPLACE FUNCTION calculate_aqi(pollutant VARCHAR, concentration DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    -- Simplified AQI calculation (actual formula is more complex)
    CASE pollutant
        WHEN 'PM2.5' THEN 
            RETURN CASE 
                WHEN concentration <= 30 THEN (concentration / 30) * 50
                WHEN concentration <= 60 THEN 50 + ((concentration - 30) / 30) * 50
                WHEN concentration <= 90 THEN 100 + ((concentration - 60) / 30) * 100
                WHEN concentration <= 120 THEN 200 + ((concentration - 90) / 30) * 100
                WHEN concentration <= 250 THEN 300 + ((concentration - 120) / 130) * 100
                ELSE 400 + ((concentration - 250) / 130) * 100
            END;
        WHEN 'PM10' THEN 
            RETURN CASE 
                WHEN concentration <= 50 THEN (concentration / 50) * 50
                WHEN concentration <= 100 THEN 50 + ((concentration - 50) / 50) * 50
                WHEN concentration <= 250 THEN 100 + ((concentration - 100) / 150) * 100
                WHEN concentration <= 350 THEN 200 + ((concentration - 250) / 100) * 100
                WHEN concentration <= 430 THEN 300 + ((concentration - 350) / 80) * 100
                ELSE 400 + ((concentration - 430) / 80) * 100
            END;
        ELSE RETURN NULL;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- DATA PARTITIONING (for large datasets)
-- ============================================================================

-- Partition air_quality_data by month (uncomment if needed for large datasets)
/*
ALTER TABLE air_quality_data PARTITION BY RANGE (recorded_at);

-- Create partitions for 2025
CREATE TABLE air_quality_data_2025_01 PARTITION OF air_quality_data
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
CREATE TABLE air_quality_data_2025_02 PARTITION OF air_quality_data
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');
-- Add more partitions as needed...
*/

-- ============================================================================
-- MAINTENANCE & MONITORING
-- ============================================================================

-- Function to get database statistics
CREATE OR REPLACE FUNCTION get_db_statistics()
RETURNS TABLE (
    total_stations BIGINT,
    total_readings BIGINT,
    latest_reading TIMESTAMP,
    oldest_reading TIMESTAMP,
    data_sources TEXT[],
    cities_covered BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        (SELECT COUNT(*) FROM stations)::BIGINT,
        (SELECT COUNT(*) FROM air_quality_data)::BIGINT,
        (SELECT MAX(recorded_at) FROM air_quality_data),
        (SELECT MIN(recorded_at) FROM air_quality_data),
        (SELECT ARRAY_AGG(DISTINCT data_source) FROM stations),
        (SELECT COUNT(DISTINCT city) FROM stations)::BIGINT;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- SAMPLE QUERIES
-- ============================================================================

/*
-- Get latest AQI for all cities
SELECT DISTINCT ON (s.city)
    s.city,
    s.station_name,
    aq.recorded_at,
    aq.aqi,
    ac.category_name,
    ac.color_code
FROM air_quality_data aq
JOIN stations s ON aq.station_id = s.station_id
JOIN aqi_categories ac ON aq.aqi_category_id = ac.category_id
WHERE aq.aqi IS NOT NULL
ORDER BY s.city, aq.recorded_at DESC;

-- Get 7-day trend for a specific station
SELECT 
    DATE(recorded_at) AS date,
    pollutant_id,
    AVG(pollutant_avg) AS avg_concentration,
    AVG(aqi) AS avg_aqi
FROM air_quality_data
WHERE station_id = 'YOUR_STATION_ID'
    AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '7 days'
GROUP BY DATE(recorded_at), pollutant_id
ORDER BY date DESC, pollutant_id;

-- Get hourly averages for prediction
SELECT 
    DATE_TRUNC('hour', recorded_at) AS hour,
    AVG(pollutant_avg) AS pm25_avg,
    AVG(temperature) AS temp_avg,
    AVG(humidity) AS humidity_avg
FROM air_quality_data
WHERE pollutant_id = 'PM2.5'
    AND recorded_at >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
GROUP BY DATE_TRUNC('hour', recorded_at)
ORDER BY hour DESC;
*/

-- ============================================================================
-- GRANTS & SECURITY
-- ============================================================================

-- Grant appropriate permissions (adjust as needed)
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO app_user;
-- GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO app_user;
