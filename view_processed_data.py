import pandas as pd

df = pd.read_csv('processed_air_quality_data.csv')

print('='*80)
print('✅ PROCESSED DATA STRUCTURE')
print('='*80)

print(f'\n📊 Shape: {df.shape[0]} rows × {df.shape[1]} columns')

print(f'\n📋 All {len(df.columns)} Columns:')
for i, col in enumerate(df.columns, 1):
    print(f'{i:3d}. {col}')

print(f'\n📅 Sample Data (first 3 rows):')
print(df.head(3))

print(f'\n✨ Feature Categories:')
temporal = [c for c in df.columns if any(x in c for x in ['hour', 'day', 'month', 'year', 'season', 'weekend', 'rush'])]
pollutant = [c for c in df.columns if any(x in c for x in ['pm', 'no2', 'so2', 'co', 'o3', 'nh3', 'aqi']) and 'rolling' not in c and 'lag' not in c]
weather = [c for c in df.columns if any(x in c for x in ['temp', 'humidity', 'wind', 'pressure', 'heat']) and 'rolling' not in c and 'lag' not in c]
rolling = [c for c in df.columns if 'rolling' in c]
lag = [c for c in df.columns if 'lag' in c]

print(f'  • Temporal: {len(temporal)}')
print(f'  • Pollutant: {len(pollutant)}')
print(f'  • Weather: {len(weather)}')
print(f'  • Rolling: {len(rolling)}')
print(f'  • Lag: {len(lag)}')
