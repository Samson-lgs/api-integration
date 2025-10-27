"""
Demo: Create sample air quality data and run preprocessing pipeline
This demonstrates all preprocessing capabilities without needing API calls
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from data_preprocessing import AirQualityPreprocessor


def create_sample_data(num_days=7, cities=['Delhi', 'Mumbai', 'Bangalore']):
    """
    Create realistic sample air quality data for demonstration
    """
    print("\n🎬 Creating sample air quality data...")
    
    np.random.seed(42)
    
    data = []
    start_date = datetime.now() - timedelta(days=num_days)
    
    for city in cities:
        for day in range(num_days):
            for hour in range(24):  # Hourly data
                timestamp = start_date + timedelta(days=day, hours=hour)
                
                # Simulate realistic patterns
                # Higher pollution in morning/evening rush hours
                rush_hour_factor = 1.5 if hour in [7, 8, 9, 17, 18, 19, 20] else 1.0
                
                # Weekend effect (lower pollution)
                weekend_factor = 0.7 if timestamp.weekday() >= 5 else 1.0
                
                # Base pollution levels (Delhi > Mumbai > Chennai > Bangalore)
                base_pm25 = {'Delhi': 120, 'Mumbai': 80, 'Chennai': 70, 'Bangalore': 60}[city]
                base_aqi = {'Delhi': 200, 'Mumbai': 150, 'Chennai': 125, 'Bangalore': 100}[city]
                
                # Add randomness and patterns
                pm25 = base_pm25 * rush_hour_factor * weekend_factor * np.random.uniform(0.7, 1.3)
                pm10 = pm25 * np.random.uniform(1.5, 2.0)
                no2 = np.random.uniform(20, 80) * rush_hour_factor
                so2 = np.random.uniform(10, 40)
                co = np.random.uniform(0.5, 2.5) * rush_hour_factor
                o3 = np.random.uniform(20, 100) * (1.5 if 12 <= hour <= 16 else 0.8)  # Higher in afternoon
                nh3 = np.random.uniform(5, 25)
                
                # Weather parameters
                temp_base = {'Delhi': 25, 'Mumbai': 28, 'Chennai': 30, 'Bangalore': 22}[city]
                temperature = temp_base + np.random.uniform(-5, 5) + (5 if 12 <= hour <= 16 else -2)
                humidity = np.random.uniform(40, 80)
                wind_speed = np.random.uniform(2, 15)
                pressure = np.random.uniform(1000, 1020)
                
                # Calculate AQI (simplified)
                aqi = base_aqi * rush_hour_factor * weekend_factor * np.random.uniform(0.8, 1.2)
                
                # Randomly introduce some missing values (10% missing rate)
                if np.random.random() < 0.1:
                    pm25 = np.nan
                if np.random.random() < 0.08:
                    no2 = np.nan
                if np.random.random() < 0.05:
                    temperature = np.nan
                
                # Randomly introduce some outliers (2% outlier rate)
                if np.random.random() < 0.02:
                    pm25 = pm25 * 5 if not np.isnan(pm25) else np.nan  # Extreme spike
                if np.random.random() < 0.02:
                    aqi = aqi * 3 if not np.isnan(aqi) else np.nan
                
                # Create data point
                data.append({
                    'station_id': f'CPCB_{city}_Station1',
                    'city': city,
                    'state': {'Delhi': 'Delhi', 'Mumbai': 'Maharashtra', 'Chennai': 'Tamil Nadu', 'Bangalore': 'Karnataka'}[city],
                    'source': 'CPCB',
                    'recorded_at': timestamp,
                    'pm25': pm25,
                    'pm10': pm10,
                    'no2': no2,
                    'so2': so2,
                    'co': co,
                    'o3': o3,
                    'nh3': nh3,
                    'temperature': temperature,
                    'humidity': humidity,
                    'wind_speed': wind_speed,
                    'pressure': pressure,
                    'aqi': aqi
                })
    
    df = pd.DataFrame(data)
    
    print(f"✅ Created {len(df)} sample records")
    print(f"   • Cities: {', '.join(cities)}")
    print(f"   • Date range: {num_days} days")
    print(f"   • Frequency: Hourly")
    print(f"   • Records per city: {len(df) // len(cities)}")
    
    return df


def main():
    print("\n" + "="*80)
    print("🎬 PREPROCESSING PIPELINE DEMO")
    print("="*80)
    
    # Create sample data
    df_raw = create_sample_data(num_days=7, cities=['Delhi', 'Mumbai', 'Bangalore', 'Chennai'])
    
    # Save raw sample data
    df_raw.to_csv('sample_air_quality_data.csv', index=False)
    print(f"💾 Saved sample data to: sample_air_quality_data.csv")
    
    # Show initial statistics
    print(f"\n📊 Raw Data Statistics:")
    print(f"   • Total records: {len(df_raw)}")
    print(f"   • Missing values: {df_raw.isnull().sum().sum()}")
    print(f"   • Date range: {df_raw['recorded_at'].min()} to {df_raw['recorded_at'].max()}")
    
    # Initialize preprocessor
    print("\n" + "="*80)
    print("🚀 RUNNING PREPROCESSING PIPELINE")
    print("="*80)
    
    preprocessor = AirQualityPreprocessor()
    
    # Run full preprocessing pipeline
    df_processed = preprocessor.run_full_pipeline(
        df_raw,
        imputation_method='knn',  # KNN imputation for correlated features
        outlier_method='cap',     # Cap outliers instead of removing
        add_rolling=True,         # Add rolling averages
        add_lags=True             # Add lag features
    )
    
    # Save processed data
    output_file = 'processed_air_quality_data.csv'
    preprocessor.save_processed_data(df_processed, output_file)
    
    # Display final summary
    print("\n" + "="*80)
    print("📊 FINAL RESULTS")
    print("="*80)
    
    print(f"\n📏 Data Transformation:")
    print(f"   • Raw: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
    print(f"   • Processed: {df_processed.shape[0]} rows × {df_processed.shape[1]} columns")
    print(f"   • Features added: {df_processed.shape[1] - df_raw.shape[1]}")
    
    print(f"\n🌍 Data Coverage:")
    print(f"   • Cities: {df_processed['city'].nunique()}")
    print(f"   • Stations: {df_processed['station_id'].nunique()}")
    print(f"   • Time span: {(df_processed['recorded_at'].max() - df_processed['recorded_at'].min()).days} days")
    
    # Feature breakdown
    all_cols = df_processed.columns.tolist()
    original_cols = df_raw.columns.tolist()
    new_cols = [col for col in all_cols if col not in original_cols]
    
    temporal_cols = [col for col in new_cols if any(x in col for x in ['hour', 'day', 'month', 'year', 'season', 'weekend', 'rush'])]
    pollutant_cols = [col for col in new_cols if any(x in col for x in ['pm', 'no2', 'so2', 'aqi']) and 'rolling' not in col and 'lag' not in col]
    weather_cols = [col for col in new_cols if any(x in col for x in ['temp', 'humidity', 'heat']) and 'rolling' not in col and 'lag' not in col]
    rolling_cols = [col for col in new_cols if 'rolling' in col]
    lag_cols = [col for col in new_cols if 'lag' in col]
    
    print(f"\n🏗️ Features Engineered:")
    print(f"   • Temporal features: {len(temporal_cols)}")
    print(f"   • Pollutant features: {len(pollutant_cols)}")
    print(f"   • Weather features: {len(weather_cols)}")
    print(f"   • Rolling averages: {len(rolling_cols)}")
    print(f"   • Lag features: {len(lag_cols)}")
    print(f"   • Total new features: {len(new_cols)}")
    
    # Data quality improvements
    missing_before = df_raw.isnull().sum().sum()
    missing_after = df_processed.isnull().sum().sum()
    
    print(f"\n✨ Data Quality:")
    print(f"   • Missing values (before): {missing_before}")
    print(f"   • Missing values (after): {missing_after}")
    print(f"   • Values imputed: {missing_before - missing_after}")
    
    # Show sample of key features
    print(f"\n📋 Sample of Processed Data (Key Features):")
    sample_cols = ['city', 'recorded_at', 'pm25', 'aqi', 'temperature', 
                   'hour', 'season', 'time_of_day', 'is_weekend', 
                   'pm25_category', 'aqi_category', 'pm25_rolling_mean_6h']
    available_cols = [col for col in sample_cols if col in df_processed.columns]
    print(df_processed[available_cols].head(10).to_string())
    
    # Show some specific engineered features
    print(f"\n🔬 Example Engineered Features:")
    
    if 'pm25_rolling_mean_6h' in df_processed.columns:
        print(f"\n1️⃣ Rolling Averages (PM2.5):")
        rolling_pm25_cols = [col for col in df_processed.columns if 'pm25_rolling' in col][:4]
        print(df_processed[['city', 'recorded_at', 'pm25'] + rolling_pm25_cols].head(5).to_string())
    
    if 'pm25_lag_1h' in df_processed.columns:
        print(f"\n2️⃣ Lag Features (PM2.5 - Historical Values):")
        lag_cols = [col for col in df_processed.columns if 'pm25_lag' in col][:4]
        print(df_processed[['city', 'recorded_at', 'pm25'] + lag_cols].head(5).to_string())
    
    if 'pm25_pm10_ratio' in df_processed.columns:
        print(f"\n3️⃣ Derived Metrics:")
        derived_cols = [col for col in df_processed.columns if 'ratio' in col or 'total' in col][:3]
        print(df_processed[['city', 'pm25', 'pm10'] + derived_cols].head(5).to_string())
    
    print("\n" + "="*80)
    print("✅ DEMO COMPLETE!")
    print("="*80)
    
    print(f"\n📁 Output Files Created:")
    print(f"   • sample_air_quality_data.csv - Raw sample data")
    print(f"   • {output_file} - Fully preprocessed data")
    
    print(f"\n🤖 Ready for Machine Learning!")
    print(f"\n✨ All preprocessing steps demonstrated:")
    print(f"   ✅ Missing value imputation (KNN)")
    print(f"   ✅ Outlier detection & handling (IQR + Z-score)")
    print(f"   ✅ Cross-source consistency checks")
    print(f"   ✅ Temporal feature engineering (15+ features)")
    print(f"   ✅ Pollutant feature engineering (ratios, categories)")
    print(f"   ✅ Weather feature engineering")
    print(f"   ✅ Rolling/Moving averages (multiple windows)")
    print(f"   ✅ Lag features (historical values)")
    print(f"\n🎯 Next: Use this data to build AQI prediction models! 🎯\n")


if __name__ == "__main__":
    main()
