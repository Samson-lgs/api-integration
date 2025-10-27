"""
Complete pipeline: Collect data + Preprocess
"""

import pandas as pd
import sys
import os
from multi_source_collector import MultiSourceAirQualityCollector
from data_preprocessing import AirQualityPreprocessor


def main():
    print("\n" + "="*80)
    print("COMPLETE PIPELINE: DATA COLLECTION + PREPROCESSING")
    print("="*80 + "\n")
    
    # Step 1: Collect Data
    print("STEP 1: DATA COLLECTION")
    print("-" * 80)
    
    # Check if data already exists
    if os.path.exists('unified_air_quality_data.csv'):
        print("✅ Found existing data file: unified_air_quality_data.csv")
        use_existing = input("Use existing data? (y/n): ").lower()
        
        if use_existing == 'y':
            df_raw = pd.read_csv('unified_air_quality_data.csv')
            print(f"✅ Loaded {len(df_raw)} existing records")
        else:
            print("\n📡 Collecting fresh data from APIs...")
            collector = MultiSourceAirQualityCollector(db_path='air_quality_multi.db')
            collector.collect_all_data()
            collector.export_to_csv()
            df_raw = pd.read_csv('unified_air_quality_data.csv')
    else:
        print("📡 No existing data found. Collecting from APIs...")
        collector = MultiSourceAirQualityCollector(db_path='air_quality_multi.db')
        collector.collect_all_data()
        collector.export_to_csv()
        df_raw = pd.read_csv('unified_air_quality_data.csv')
    
    print(f"\n✅ Data Collection Complete: {len(df_raw)} records\n")
    
    # Step 2: Preprocess Data
    print("\n" + "="*80)
    print("STEP 2: DATA PREPROCESSING")
    print("="*80 + "\n")
    
    # Initialize preprocessor
    preprocessor = AirQualityPreprocessor()
    
    # Configuration
    config = {
        'imputation_method': 'knn',  # Best for correlated features
        'outlier_method': 'cap',     # Preserve data while handling extremes
        'add_rolling': True,         # Add moving averages
        'add_lags': True             # Add historical values
    }
    
    print("⚙️ Preprocessing Configuration:")
    for key, value in config.items():
        print(f"   • {key}: {value}")
    print()
    
    # Run preprocessing
    df_processed = preprocessor.run_full_pipeline(
        df_raw,
        imputation_method=config['imputation_method'],
        outlier_method=config['outlier_method'],
        add_rolling=config['add_rolling'],
        add_lags=config['add_lags']
    )
    
    # Save processed data
    output_file = 'processed_air_quality_data.csv'
    preprocessor.save_processed_data(df_processed, output_file)
    
    # Final Summary
    print("\n" + "="*80)
    print("📊 FINAL SUMMARY")
    print("="*80)
    
    print(f"\n📏 Dataset Dimensions:")
    print(f"   • Raw data: {df_raw.shape[0]} rows × {df_raw.shape[1]} columns")
    print(f"   • Processed data: {df_processed.shape[0]} rows × {df_processed.shape[1]} columns")
    
    print(f"\n📅 Date Range:")
    print(f"   • From: {df_processed['recorded_at'].min()}")
    print(f"   • To: {df_processed['recorded_at'].max()}")
    
    print(f"\n🌍 Coverage:")
    print(f"   • Cities: {df_processed['city'].nunique()}")
    print(f"   • Stations: {df_processed['station_id'].nunique()}")
    print(f"   • Sources: {', '.join(df_processed['source'].unique())}")
    
    # Feature breakdown
    all_cols = df_processed.columns.tolist()
    temporal_features = [col for col in all_cols if any(x in col for x in ['hour', 'day', 'month', 'year', 'season', 'weekend', 'rush'])]
    pollutant_features = [col for col in all_cols if any(x in col for x in ['pm', 'no2', 'so2', 'co', 'o3', 'nh3', 'aqi']) and 'rolling' not in col and 'lag' not in col]
    weather_features = [col for col in all_cols if any(x in col for x in ['temp', 'humidity', 'wind', 'pressure', 'heat']) and 'rolling' not in col and 'lag' not in col]
    rolling_features = [col for col in all_cols if 'rolling' in col]
    lag_features = [col for col in all_cols if 'lag' in col]
    derived_features = [col for col in all_cols if any(x in col for x in ['ratio', 'category', 'change', 'pct', 'total', 'indicator'])]
    
    print(f"\n🏷️ Feature Engineering Results:")
    print(f"   • Temporal features: {len(temporal_features)}")
    print(f"   • Pollutant features: {len(pollutant_features)}")
    print(f"   • Weather features: {len(weather_features)}")
    print(f"   • Rolling/Moving avg: {len(rolling_features)}")
    print(f"   • Lag features: {len(lag_features)}")
    print(f"   • Derived metrics: {len(derived_features)}")
    print(f"   • Total columns: {len(all_cols)}")
    
    # Data quality
    missing_raw = df_raw.isnull().sum().sum()
    missing_processed = df_processed.isnull().sum().sum()
    
    print(f"\n✨ Data Quality Improvements:")
    print(f"   • Missing values (raw): {missing_raw}")
    print(f"   • Missing values (processed): {missing_processed}")
    print(f"   • Improvement: {missing_raw - missing_processed} values imputed")
    
    # Sample output
    print(f"\n📋 Sample of Processed Data:")
    print(df_processed[['city', 'recorded_at', 'pm25', 'aqi', 'temperature', 
                        'season', 'time_of_day', 'pm25_category', 'aqi_category']].head(10))
    
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE!")
    print("="*80)
    
    print(f"\n📁 Output Files:")
    print(f"   • Raw data: unified_air_quality_data.csv ({df_raw.shape})")
    print(f"   • Processed data: {output_file} ({df_processed.shape})")
    print(f"   • Database: air_quality_multi.db")
    
    print(f"\n🤖 Next Steps for ML:")
    print(f"   1. Load processed_air_quality_data.csv")
    print(f"   2. Split into train/test sets")
    print(f"   3. Build AQI prediction models")
    print(f"   4. Evaluate and deploy")
    
    print("\n✨ Your data is ML-ready! ✨\n")


if __name__ == "__main__":
    main()
