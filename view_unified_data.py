"""
Quick viewer to inspect the unified CSV data
"""

import pandas as pd

print("="*70)
print("UNIFIED AIR QUALITY DATA VIEWER")
print("="*70)

# Load the unified CSV
print("\n📂 Loading unified_air_quality_data.csv...")
df = pd.read_csv('unified_air_quality_data.csv')

print(f"\n✓ Loaded {len(df)} records")
print(f"✓ Columns: {list(df.columns)}")
print(f"✓ Data sources: {df['data_source'].unique()}")
print(f"✓ Pollutants: {df['pollutant_id'].unique()}")

print("\n" + "="*70)
print("DATA SUMMARY")
print("="*70)

print(f"\nRecords by Data Source:")
print(df['data_source'].value_counts())

print(f"\nRecords by Pollutant:")
print(df['pollutant_id'].value_counts())

print(f"\nTop 10 Cities by Data Points:")
print(df['city'].value_counts().head(10))

print("\n" + "="*70)
print("SAMPLE RECORDS FROM EACH SOURCE")
print("="*70)

for source in df['data_source'].unique():
    print(f"\n{source} Data Sample:")
    print("-" * 70)
    sample = df[df['data_source'] == source].head(3)
    print(sample[['station_id', 'station_name', 'city', 'pollutant_id', 
                  'pollutant_avg', 'aqi', 'aqi_category']].to_string(index=False))

print("\n" + "="*70)
print("DATA QUALITY CHECK")
print("="*70)

print(f"\nMissing Values:")
print(df.isnull().sum())

print(f"\nData Types:")
print(df.dtypes)

print("\n" + "="*70)
print("WEATHER PARAMETERS (From OpenWeather)")
print("="*70)

weather_data = df[df['data_source'] == 'OpenWeather'][['city', 'temperature', 'humidity', 
                                                          'pressure', 'wind_speed']].dropna()
if not weather_data.empty:
    print(f"\nWeather data available for {len(weather_data)} records")
    print(weather_data.head(10).to_string(index=False))
else:
    print("\nNo weather data available")

print("\n" + "="*70)
print("STATION ID EXAMPLES")
print("="*70)

print("\nUnique Station IDs by Source:")
for source in df['data_source'].unique():
    station_ids = df[df['data_source'] == source]['station_id'].unique()
    print(f"\n{source} ({len(station_ids)} stations):")
    print(f"  Examples: {list(station_ids[:5])}")

print("\n" + "="*70)
print("✓ Inspection completed!")
print("="*70)
print(f"\nFile: unified_air_quality_data.csv")
print(f"Size: {len(df)} rows × {len(df.columns)} columns")
print(f"Ready for Air Quality Index Prediction modeling!")
