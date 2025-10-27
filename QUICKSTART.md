# CPCB Air Quality Data Collection - Quick Start Guide

## What Has Been Created

I've set up a complete system to collect air quality data from CPCB API and store it in PostgreSQL for air quality prediction. Here's what was created:

### Files Created:

1. **cpcb_data_collector.py** - Main data collection script
2. **database_setup.py** - Database schema creation
3. **scheduled_collector.py** - Automated scheduled data collection
4. **data_query.py** - Query and analyze stored data
5. **setup.py** - Quick setup and test script
6. **requirements.txt** - Python dependencies
7. **.env** - Configuration file (contains your API key)
8. **README.md** - Complete documentation

## Prerequisites Checklist

Before running the collector, ensure you have:

- [x] Python 3.8+ installed ✓
- [x] Required Python packages installed ✓
- [ ] PostgreSQL installed and running
- [ ] PostgreSQL credentials configured in .env file

## Quick Setup (3 Steps)

### Step 1: Configure Database Credentials

Edit the `.env` file and update your PostgreSQL credentials:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=air_quality_db
DB_USER=postgres
DB_PASSWORD=YOUR_ACTUAL_PASSWORD
```

**Note:** Your CPCB API key is already configured!

### Step 2: Install PostgreSQL (if not installed)

**Windows:**
1. Download from: https://www.postgresql.org/download/windows/
2. Run installer and follow prompts
3. Remember the password you set for 'postgres' user
4. Use that password in .env file

### Step 3: Run Setup

```bash
python setup.py
```

This will:
- Test database connection
- Create database and tables
- Collect initial data from CPCB

## Usage

### One-Time Data Collection
```bash
python cpcb_data_collector.py
```

### Continuous Scheduled Collection (Recommended)
```bash
python scheduled_collector.py
```
This runs every 60 minutes automatically.

### Query and Analyze Data
```bash
python data_query.py
```

## What Data is Collected

The system collects the following from CPCB API:

- **Station Information:**
  - Station ID, Name, City, State
  - Location coordinates

- **Air Quality Measurements:**
  - PM2.5 (Particulate Matter 2.5)
  - PM10 (Particulate Matter 10)
  - NO2 (Nitrogen Dioxide)
  - SO2 (Sulfur Dioxide)
  - CO (Carbon Monoxide)
  - O3 (Ozone)
  - NH3 (Ammonia)

- **Air Quality Index (AQI):**
  - AQI value
  - AQI category (Good/Satisfactory/Moderate/Poor/Very Poor/Severe)

## Database Schema

### stations table
- station_id (Primary Key)
- station_name
- city
- state
- latitude, longitude
- created_at

### air_quality_data table
- id (Primary Key)
- station_id (Foreign Key)
- recorded_at
- pollutant_id (PM2.5, PM10, NO2, SO2, CO, O3, NH3)
- pollutant_avg
- aqi
- aqi_category
- created_at

## Using Data for Prediction

Once data is collected, you can use it for AQI prediction:

### 1. Load Data with Pandas
```python
from data_query import AirQualityQuery

query = AirQualityQuery()
data = query.get_data_by_date_range('2025-01-01', '2025-10-27')
```

### 2. Export to CSV for ML
```python
query.export_to_csv(data, 'training_data.csv')
```

### 3. Use with Scikit-learn
```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor

# Load data
df = pd.read_csv('training_data.csv')

# Prepare features and target
X = df[['pollutant_avg', 'hour', 'day', 'month']]
y = df['aqi']

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model = RandomForestRegressor()
model.fit(X_train, y_train)
```

## Troubleshooting

### "Connection refused" error
- PostgreSQL is not running
- Solution: Start PostgreSQL service

### "Authentication failed" error
- Wrong password in .env file
- Solution: Update DB_PASSWORD in .env

### "API returned status code 403"
- API key issue or rate limit
- Solution: Verify API key, wait and retry

### "No module named 'psycopg2'"
- Packages not installed
- Solution: Run `pip install -r requirements.txt`

## Data Collection Schedule

By default:
- Collects data every 60 minutes
- Stores all pollutants and AQI values
- Automatically handles duplicate records

To change frequency, edit `scheduled_collector.py`:
```python
run_scheduler(interval_minutes=30)  # Collect every 30 minutes
```

## API Information

- **API Provider:** CPCB (Central Pollution Control Board)
- **API Key:** Already configured in .env
- **Data Source:** data.gov.in
- **Update Frequency:** Real-time

## Next Steps After Setup

1. **Verify Data Collection:**
   ```bash
   python data_query.py
   ```

2. **Start Scheduled Collection:**
   ```bash
   python scheduled_collector.py
   ```
   Leave this running to continuously collect data.

3. **Build Prediction Model:**
   - Collect data for several days/weeks
   - Use the collected data to train ML models
   - Build time-series forecasting models
   - Create prediction APIs

4. **Create Visualizations:**
   - Use matplotlib/seaborn for plots
   - Create dashboards with Plotly/Dash
   - Build interactive web apps

## Support

For issues with:
- **Script errors:** Check error messages and logs
- **Database issues:** Verify PostgreSQL is running
- **API issues:** Check CPCB API status
- **Python issues:** Ensure all packages are installed

## Important Notes

- ✅ API key is already configured
- ✅ All Python dependencies are installed
- ⚠️ You need to configure PostgreSQL credentials
- ⚠️ PostgreSQL must be running before setup

## Success Indicators

After running setup.py, you should see:
```
✓ PostgreSQL connection successful!
✓ Database setup completed!
✓ Initial data collection completed!
```

Then you're ready to use the system for air quality prediction!
