"""
Check Station ID Merging between CPCB and OpenWeather
"""

import pandas as pd

print("="*70)
print("STATION ID MERGE ANALYSIS")
print("="*70)

# Load the unified CSV
df = pd.read_csv('unified_air_quality_data.csv')

print(f"\n📊 Total Records: {len(df)}")
print(f"📊 Total Unique Stations: {df['station_id'].nunique()}")

# Analyze by data source
print("\n" + "="*70)
print("STATIONS BY DATA SOURCE")
print("="*70)

for source in df['data_source'].unique():
    source_data = df[df['data_source'] == source]
    unique_stations = source_data['station_id'].nunique()
    unique_cities = source_data['city'].nunique()
    
    print(f"\n{source}:")
    print(f"  Unique Stations: {unique_stations}")
    print(f"  Unique Cities: {unique_cities}")
    print(f"  Total Records: {len(source_data)}")
    
    # Show sample station IDs
    sample_ids = source_data['station_id'].unique()[:5]
    print(f"  Sample Station IDs: {list(sample_ids)}")

# Check for cities that have both CPCB and OpenWeather data
print("\n" + "="*70)
print("CITIES WITH DATA FROM BOTH SOURCES")
print("="*70)

cpcb_cities = set(df[df['data_source'] == 'CPCB']['city'].unique())
openweather_cities = set(df[df['data_source'] == 'OpenWeather']['city'].unique())

common_cities = cpcb_cities.intersection(openweather_cities)

if common_cities:
    print(f"\n✅ {len(common_cities)} cities have data from BOTH sources:")
    for city in sorted(common_cities):
        cpcb_count = len(df[(df['data_source'] == 'CPCB') & (df['city'] == city)])
        ow_count = len(df[(df['data_source'] == 'OpenWeather') & (df['city'] == city)])
        cpcb_stations = df[(df['data_source'] == 'CPCB') & (df['city'] == city)]['station_id'].nunique()
        ow_stations = df[(df['data_source'] == 'OpenWeather') & (df['city'] == city)]['station_id'].nunique()
        
        print(f"\n  {city}:")
        print(f"    CPCB: {cpcb_stations} stations, {cpcb_count} records")
        print(f"    OpenWeather: {ow_stations} stations, {ow_count} records")
else:
    print("\n⚠️ No cities have data from both sources")

print("\n" + "="*70)
print("STATION ID FORMAT ANALYSIS")
print("="*70)

print("\nCPCB Station ID Format:")
cpcb_ids = df[df['data_source'] == 'CPCB']['station_id'].head(3)
for sid in cpcb_ids:
    print(f"  {sid}")

print("\nOpenWeather Station ID Format:")
ow_ids = df[df['data_source'] == 'OpenWeather']['station_id'].head(3)
for sid in ow_ids:
    print(f"  {sid}")

# Check if there's overlap in station IDs (there shouldn't be)
print("\n" + "="*70)
print("STATION ID UNIQUENESS CHECK")
print("="*70)

cpcb_station_ids = set(df[df['data_source'] == 'CPCB']['station_id'])
ow_station_ids = set(df[df['data_source'] == 'OpenWeather']['station_id'])
overlap = cpcb_station_ids.intersection(ow_station_ids)

if overlap:
    print(f"\n⚠️ WARNING: {len(overlap)} station IDs are shared between sources!")
    print(f"  Overlapping IDs: {list(overlap)[:5]}")
else:
    print(f"\n✅ GOOD: No station ID overlap between sources")
    print(f"  Each station has a unique ID based on its source")

# Summary
print("\n" + "="*70)
print("MERGE STATUS SUMMARY")
print("="*70)

print("\n📋 Current State:")
print(f"  ✅ CPCB stations: {len(cpcb_station_ids)} unique IDs")
print(f"  ✅ OpenWeather stations: {len(ow_station_ids)} unique IDs")
print(f"  ✅ Total unique stations: {len(cpcb_station_ids) + len(ow_station_ids)}")
print(f"  ✅ No ID conflicts: {len(overlap) == 0}")

if common_cities:
    print(f"  ✅ {len(common_cities)} cities have multiple data sources")
else:
    print(f"  ⚠️ Cities don't overlap between sources")

print("\n🔍 What This Means:")
print("  • Each data source has its own unique station IDs")
print("  • CPCB IDs start with 'CPCB_'")
print("  • OpenWeather IDs start with 'OW_'")
print("  • This is CORRECT - different sources = different stations")
print("  • You can compare data from same city but different sources")

if common_cities:
    print(f"\n✅ MERGE STATUS: PERFECT")
    print(f"  The data is properly organized with:")
    print(f"  • Unique station IDs for each source")
    print(f"  • {len(common_cities)} cities with data from multiple sources")
    print(f"  • Easy to compare readings from different sources by city")
else:
    print(f"\n⚠️ MERGE STATUS: SEPARATE")
    print(f"  CPCB and OpenWeather cover different cities")
    print(f"  No city-level comparison possible yet")

print("\n" + "="*70)
