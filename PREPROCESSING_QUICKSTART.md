# 🚀 Quick Start: Data Preprocessing

## ✅ What You Have Now

Three powerful preprocessing scripts ready to use:

### 1️⃣ `demo_preprocessing.py` - **Start Here!**
**Purpose**: See preprocessing in action with sample data

```bash
python demo_preprocessing.py
```

**What it does**:
- Creates 672 sample records (4 cities, 7 days, hourly)
- Runs complete preprocessing pipeline
- Shows all feature engineering
- Generates: `processed_air_quality_data.csv`

**Use when**: Learning or testing the system

---

### 2️⃣ `run_preprocessing.py` - **For Real Data**
**Purpose**: Preprocess your collected air quality data

```bash
python run_preprocessing.py
```

**What it does**:
- Loads `unified_air_quality_data.csv`
- Runs full preprocessing
- Saves `processed_air_quality_data.csv`

**Use when**: You have real data from APIs

---

### 3️⃣ `collect_and_preprocess.py` - **Full Pipeline**
**Purpose**: Collect data from APIs + preprocess in one go

```bash
python collect_and_preprocess.py
```

**What it does**:
- Collects from CPCB, OpenWeather, IQAir
- Saves to SQLite database
- Exports to CSV
- Runs preprocessing
- All automated!

**Use when**: Running regular data collection + preprocessing

---

## 📊 Quick Feature Overview

### From 17 → 117 Columns

**Input (Raw Data)**:
```
station_id, city, state, source, recorded_at,
pm25, pm10, no2, so2, co, o3, nh3,
temperature, humidity, wind_speed, pressure, aqi
```

**Output (Processed Data)** - Original + 100 new features:

#### 🕐 Temporal (15)
- hour, day, month, year, day_of_week
- season, time_of_day, is_weekend, is_rush_hour
- Cyclical encodings (sin/cos)

#### 🏭 Pollutants (6)
- pm25_pm10_ratio, no2_so2_ratio
- total_pm, nox_indicator
- pm25_category, aqi_category

#### 🌤️ Weather (4)
- heat_index
- temp_category, humidity_category, wind_category

#### 📈 Rolling Averages (50)
- For PM2.5, PM10, NO2, AQI, Temp
- Windows: 3h, 6h, 12h, 24h
- Metrics: mean, std, change, pct_change

#### ⏮️ Lag Features (25)
- Historical values: 1h, 3h, 6h, 12h, 24h ago
- For PM2.5, PM10, AQI, Temperature, Humidity

---

## 🎯 Common Tasks

### Task 1: Preprocess Sample Data (Demo)
```bash
python demo_preprocessing.py
```
**Output**: `processed_air_quality_data.csv` (672 rows × 117 cols)

---

### Task 2: Preprocess Real Data
```bash
# First, collect data
python multi_source_collector.py

# Then, preprocess
python run_preprocessing.py
```
**Output**: Your real data, fully preprocessed

---

### Task 3: Custom Preprocessing

```python
from data_preprocessing import AirQualityPreprocessor
import pandas as pd

# Load data
df = pd.read_csv('your_data.csv')

# Initialize
prep = AirQualityPreprocessor()

# Option A: Full pipeline
df_processed = prep.run_full_pipeline(
    df,
    imputation_method='knn',  # knn, mean, median, interpolate
    outlier_method='cap',     # cap, remove, keep
    add_rolling=True,         # True/False
    add_lags=True             # True/False
)

# Option B: Step by step
df = prep.clean_data_types(df)
df = prep.handle_outliers(df, method='cap')
df = prep.impute_missing_values(df, method='knn')
df = prep.engineer_temporal_features(df)
df = prep.engineer_pollutant_features(df)
df = prep.engineer_weather_features(df)
df = prep.engineer_rolling_features(df, windows=[3, 6, 12])
df = prep.create_lag_features(df, lags=[1, 3, 6])

# Save
prep.save_processed_data(df_processed, 'output.csv')
```

---

## 🔍 Inspect Preprocessing Results

```python
import pandas as pd

# Load processed data
df = pd.read_csv('processed_air_quality_data.csv')

# Basic info
print(f"Shape: {df.shape}")
print(f"Columns: {len(df.columns)}")
print(f"Missing: {df.isnull().sum().sum()}")

# See all columns
print(df.columns.tolist())

# Check sample
print(df.head())

# Specific features
print(df[['city', 'pm25', 'pm25_lag_1h', 'pm25_rolling_mean_6h']].head(10))
```

---

## 📋 Configuration Options

### Imputation Methods
```python
imputation_method = 'knn'         # Best for correlated features (recommended)
imputation_method = 'mean'        # Simple average
imputation_method = 'median'      # Robust to outliers
imputation_method = 'forward_fill'  # Use previous value
imputation_method = 'interpolate' # Linear interpolation
```

### Outlier Handling
```python
outlier_method = 'cap'    # Cap at bounds (recommended - preserves data)
outlier_method = 'remove' # Delete outliers (reduces dataset size)
outlier_method = 'keep'   # Keep all outliers (for exploratory analysis)
```

### Rolling Windows
```python
windows = [3, 6, 12, 24]  # Default: 3h, 6h, 12h, 24h
windows = [6, 12]         # Fewer features, faster
windows = [1, 3, 6, 12, 24, 48]  # More granular
```

### Lag Periods
```python
lags = [1, 3, 6, 12, 24]  # Default: 1h to 24h
lags = [1, 24]            # Minimal: last hour + same time yesterday
lags = [1, 2, 3, 6, 12, 24, 48]  # Extended for deeper history
```

---

## 🎯 ML-Ready Feature Sets

### Minimal Feature Set (Fast Training)
```python
features = [
    'pm25', 'pm10', 'no2',
    'temperature', 'humidity',
    'hour', 'day_of_week',
    'pm25_lag_1h', 'pm25_lag_24h'
]
```

### Recommended Feature Set (Balanced)
```python
features = [
    # Pollutants
    'pm25', 'pm10', 'no2', 'so2',
    
    # Weather
    'temperature', 'humidity', 'wind_speed', 'pressure',
    
    # Temporal
    'hour', 'day_of_week', 'season', 'is_rush_hour',
    
    # Lags
    'pm25_lag_1h', 'pm25_lag_3h', 'pm25_lag_24h',
    
    # Rolling
    'pm25_rolling_mean_6h', 'pm25_rolling_std_6h',
    
    # Derived
    'pm25_pm10_ratio', 'heat_index'
]
```

### Complete Feature Set (Maximum Accuracy)
```python
# Use all 117 features
features = df.columns.tolist()
features.remove('aqi')  # Remove target
features.remove('recorded_at')  # Remove timestamp
features.remove('station_id')  # Remove identifiers
features.remove('city')
features.remove('state')
```

---

## 💾 File Structure

```
api integration/
│
├── Data Preprocessing Scripts
│   ├── data_preprocessing.py         # Main preprocessing class
│   ├── demo_preprocessing.py         # Demo with sample data ⭐ START HERE
│   ├── run_preprocessing.py          # For real data
│   └── collect_and_preprocess.py     # Full pipeline
│
├── Data Files (Generated)
│   ├── sample_air_quality_data.csv        # Raw sample (17 cols)
│   ├── processed_air_quality_data.csv     # Processed (117 cols)
│   └── unified_air_quality_data.csv       # From APIs (17 cols)
│
└── Documentation
    ├── PREPROCESSING_SUMMARY.md      # Complete guide
    └── PREPROCESSING_QUICKSTART.md   # This file
```

---

## 🚦 Preprocessing Status Indicators

When you run preprocessing, watch for:

✅ **Green Checkmarks** - Step completed successfully  
⚠️ **Yellow Warnings** - Non-critical issues (e.g., no multi-source data)  
❌ **Red X's** - Errors or failures (e.g., missing columns)  
📊 **Statistics** - Summary of changes made  

Example output:
```
✅ Converted 'pm25' to numeric
📌 Capped 32 outliers in 'pm25'
⚠️ Need 'city' and 'source' columns for consistency checks
✅ Created 15 temporal features
```

---

## 🎓 Understanding the Output

### Processed Data Structure

Each row = One observation (city, time)  
Each column = One feature

**Row example** (Delhi, 2025-10-21 08:00):
```
city: Delhi
recorded_at: 2025-10-21 08:00:00
pm25: 145.2          # Current PM2.5
pm25_lag_1h: 138.5   # PM2.5 1 hour ago
pm25_lag_24h: 152.1  # PM2.5 yesterday same time
pm25_rolling_mean_6h: 141.8  # 6-hour average
hour: 8              # Rush hour
is_rush_hour: 1      # Yes
season: post_monsoon
time_of_day: morning
aqi: 198             # Target to predict
```

---

## ✅ Success Checklist

- [ ] Ran `python demo_preprocessing.py`
- [ ] Saw 117 columns in output
- [ ] Found `processed_air_quality_data.csv`
- [ ] Checked sample data looks good
- [ ] Understand rolling averages concept
- [ ] Understand lag features concept
- [ ] Ready to build ML models!

---

## 🆘 Troubleshooting

### "FileNotFoundError: unified_air_quality_data.csv"
**Solution**: Run demo first or collect data:
```bash
python demo_preprocessing.py
```

### "KeyError: 'recorded_at'"
**Solution**: Your CSV needs a `recorded_at` datetime column

### Too many NaN values in processed data
**Solution**: Normal for lag features! First 24 rows will have NaN for lag_24h

### Preprocessing takes too long
**Solution**: Reduce features:
```python
df_processed = prep.run_full_pipeline(
    df,
    add_rolling=False,  # Skip rolling features
    add_lags=False      # Skip lag features
)
```

---

## 🎯 Next Steps

1. ✅ Run demo: `python demo_preprocessing.py`
2. ✅ Inspect: `processed_air_quality_data.csv`
3. ✅ Learn: Read `PREPROCESSING_SUMMARY.md`
4. 🚀 Build: Train your AQI prediction model!

---

**Ready to preprocess your data? Start with the demo! 🎬**

```bash
python demo_preprocessing.py
```
