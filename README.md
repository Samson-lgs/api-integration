# CPCB Air Quality Data Collection System

This project collects air quality data from the Central Pollution Control Board (CPCB) API and stores it in a PostgreSQL database for air quality index prediction and analysis.

## Features

- Fetch real-time air quality data from CPCB API
- Store data in PostgreSQL database with proper schema
- Support for multiple pollutants (PM2.5, PM10, NO2, SO2, CO, O3, NH3)
- AQI calculation and categorization
- Scheduled data collection at regular intervals
- Query utilities for data analysis
- Export data to CSV for further analysis

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12 or higher
- CPCB API Key (already configured)

## Installation

1. Install required Python packages:
```bash
pip install -r requirements.txt
```

2. Configure your database credentials in `.env` file:
```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=air_quality_db
DB_USER=postgres
DB_PASSWORD=your_password_here
```

3. Set up the database:
```bash
python database_setup.py
```

## Usage

### One-time Data Collection

To collect data once:
```bash
python cpcb_data_collector.py
```

### Scheduled Data Collection

To run continuous data collection (every 60 minutes):
```bash
python scheduled_collector.py
```

### Query Data

To query and analyze stored data:
```bash
python data_query.py
```

## Database Schema

### Stations Table
- `station_id` (Primary Key): Unique identifier for the monitoring station
- `station_name`: Name of the station
- `city`: City where station is located
- `state`: State where station is located
- `latitude`, `longitude`: GPS coordinates
- `created_at`: Timestamp of record creation

### Air Quality Data Table
- `id` (Primary Key): Auto-increment ID
- `station_id` (Foreign Key): Reference to stations table
- `recorded_at`: Timestamp when data was recorded
- `pollutant_id`: Type of pollutant (PM2.5, PM10, etc.)
- `pollutant_avg`: Average pollutant value
- `aqi`: Air Quality Index value
- `aqi_category`: Category (Good, Satisfactory, Moderate, Poor, Very Poor, Severe)
- `created_at`: Timestamp of record creation

## AQI Categories

| AQI Range | Category |
|-----------|----------|
| 0-50 | Good |
| 51-100 | Satisfactory |
| 101-200 | Moderate |
| 201-300 | Poor |
| 301-400 | Very Poor |
| 401+ | Severe |

## API Configuration

The CPCB API key is already configured in the `.env` file:
```
CPCB_API_KEY=579b464db66ec23bdd000001eed35a78497b4993484cd437724fd5dd
```

## Data Collection Intervals

By default, scheduled collection runs every 60 minutes. You can adjust this in `scheduled_collector.py`:
```python
run_scheduler(interval_minutes=60)  # Change this value as needed
```

## Querying Data

The `data_query.py` script provides several utility functions:

- `get_latest_data(limit)`: Get most recent readings
- `get_station_data(city, state)`: Get station information
- `get_data_by_date_range(start, end)`: Get historical data
- `get_aqi_statistics(city)`: Get AQI statistics
- `get_pollutant_trends(pollutant_id, days)`: Get pollutant trends
- `export_to_csv(dataframe, filename)`: Export data to CSV

## Data Flow

1. **Collection**: `cpcb_data_collector.py` fetches data from CPCB API
2. **Storage**: Data is parsed and stored in PostgreSQL
3. **Scheduling**: `scheduled_collector.py` automates regular collection
4. **Analysis**: `data_query.py` provides tools to query and analyze data

## Troubleshooting

### Connection Issues
- Verify PostgreSQL is running
- Check database credentials in `.env` file
- Ensure database user has proper permissions

### API Issues
- Verify API key is correct
- Check internet connectivity
- API may have rate limits or temporary downtime

### Data Issues
- Check if data format from API has changed
- Review error logs for parsing issues
- Verify database schema matches data structure

## Next Steps for Prediction

With data collected in PostgreSQL, you can:

1. Use pandas to load data for analysis
2. Train machine learning models for AQI prediction
3. Perform time series forecasting
4. Create visualizations and dashboards
5. Build predictive alerts for poor air quality

## License

This project is for educational and research purposes.

## Contact

For issues or questions, please refer to CPCB API documentation: https://api.data.gov.in
