"""
Quick script to run data preprocessing pipeline
"""

import pandas as pd
import sys
from data_preprocessing import AirQualityPreprocessor


def main():
    """
    Run preprocessing on unified air quality data
    """
    
    print("\n" + "="*80)
    print("AIR QUALITY DATA PREPROCESSING PIPELINE")
    print("="*80 + "\n")
    
    # Initialize preprocessor
    preprocessor = AirQualityPreprocessor()
    
    # Load data
    try:
        print("📂 Loading data from CSV...")
        df = pd.read_csv('unified_air_quality_data.csv')
        print(f"✅ Loaded {len(df)} records\n")
    except FileNotFoundError:
        print("❌ Error: unified_air_quality_data.csv not found!")
        print("Please run the data collection script first.")
        sys.exit(1)
    
    # Configuration
    config = {
        'imputation_method': 'knn',  # Best for correlated features
        'outlier_method': 'cap',     # Preserve data while handling extremes
        'add_rolling': True,         # Add moving averages
        'add_lags': True             # Add historical values
    }
    
    print("⚙️ Configuration:")
    for key, value in config.items():
        print(f"   • {key}: {value}")
    print()
    
    # Run full preprocessing pipeline
    df_processed = preprocessor.run_full_pipeline(
        df,
        imputation_method=config['imputation_method'],
        outlier_method=config['outlier_method'],
        add_rolling=config['add_rolling'],
        add_lags=config['add_lags']
    )
    
    # Save processed data
    output_file = 'processed_air_quality_data.csv'
    preprocessor.save_processed_data(df_processed, output_file)
    
    # Display statistics
    print("\n" + "="*80)
    print("📊 PROCESSED DATA STATISTICS")
    print("="*80)
    
    print(f"\n📏 Shape: {df_processed.shape[0]} rows × {df_processed.shape[1]} columns")
    
    print(f"\n📅 Date Range:")
    print(f"   • From: {df_processed['recorded_at'].min()}")
    print(f"   • To: {df_processed['recorded_at'].max()}")
    
    print(f"\n🌍 Coverage:")
    print(f"   • Cities: {df_processed['city'].nunique()}")
    print(f"   • Stations: {df_processed['station_id'].nunique()}")
    print(f"   • Sources: {df_processed['source'].nunique()}")
    
    # Feature categories
    temporal_features = [col for col in df_processed.columns if any(x in col for x in ['hour', 'day', 'month', 'year', 'season', 'weekend', 'rush'])]
    pollutant_features = [col for col in df_processed.columns if any(x in col for x in ['pm', 'no2', 'so2', 'co', 'o3', 'nh3', 'aqi'])]
    weather_features = [col for col in df_processed.columns if any(x in col for x in ['temp', 'humidity', 'wind', 'pressure', 'heat'])]
    rolling_features = [col for col in df_processed.columns if 'rolling' in col]
    lag_features = [col for col in df_processed.columns if 'lag' in col]
    
    print(f"\n🏷️ Feature Categories:")
    print(f"   • Temporal features: {len(temporal_features)}")
    print(f"   • Pollutant features: {len(pollutant_features)}")
    print(f"   • Weather features: {len(weather_features)}")
    print(f"   • Rolling features: {len(rolling_features)}")
    print(f"   • Lag features: {len(lag_features)}")
    print(f"   • Total features: {len(df_processed.columns)}")
    
    # Missing values after preprocessing
    missing_after = df_processed.isnull().sum().sum()
    print(f"\n❌ Missing values after preprocessing: {missing_after}")
    
    # Sample data
    print(f"\n📋 Sample of processed data (first 5 rows):")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    print(df_processed.head())
    
    print("\n" + "="*80)
    print("✅ PREPROCESSING COMPLETE!")
    print(f"💾 Processed data saved to: {output_file}")
    print("="*80 + "\n")
    
    # Ready for ML
    print("🤖 Your data is now ready for machine learning!")
    print("   • Next step: Build AQI prediction models")
    print("   • Use: processed_air_quality_data.csv")
    print()


if __name__ == "__main__":
    main()
