"""
Advanced Data Preprocessing and Feature Engineering for Air Quality Data
Includes: Missing value imputation, outlier detection, consistency checks, temporal features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from scipy import stats
from sklearn.preprocessing import StandardScaler
from sklearn.impute import KNNImputer
import warnings
warnings.filterwarnings('ignore')


class AirQualityPreprocessor:
    """
    Comprehensive preprocessing pipeline for air quality data from multiple sources
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.imputer = KNNImputer(n_neighbors=5)
        self.outlier_stats = {}
        self.preprocessing_report = {
            'missing_values': {},
            'outliers_removed': {},
            'imputed_values': {},
            'feature_engineering': {}
        }
    
    def load_data(self, source='csv', filepath=None, db_connection=None):
        """
        Load data from CSV or database
        """
        if source == 'csv':
            df = pd.read_csv(filepath)
        elif source == 'database':
            query = "SELECT * FROM air_quality_data ORDER BY recorded_at DESC"
            df = pd.read_sql(query, db_connection)
        
        print(f"✅ Loaded {len(df)} records from {source}")
        return df
    
    def initial_data_inspection(self, df):
        """
        Comprehensive initial data quality check
        """
        print("\n" + "="*80)
        print("📊 INITIAL DATA INSPECTION")
        print("="*80)
        
        # Basic info
        print(f"\n📌 Dataset Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"📅 Date Range: {df['recorded_at'].min()} to {df['recorded_at'].max()}")
        
        # Data sources
        if 'source' in df.columns:
            print(f"\n🌐 Data Sources:")
            print(df['source'].value_counts())
        
        # Missing values summary
        print(f"\n❌ Missing Values Summary:")
        missing = df.isnull().sum()
        missing_pct = (missing / len(df) * 100).round(2)
        missing_df = pd.DataFrame({
            'Column': missing.index,
            'Missing_Count': missing.values,
            'Missing_Percentage': missing_pct.values
        })
        missing_df = missing_df[missing_df['Missing_Count'] > 0].sort_values('Missing_Count', ascending=False)
        print(missing_df.to_string(index=False))
        
        self.preprocessing_report['missing_values']['initial'] = missing_df.to_dict()
        
        return missing_df
    
    def clean_data_types(self, df):
        """
        Ensure correct data types for all columns
        """
        print("\n" + "="*80)
        print("🔧 DATA TYPE CLEANING")
        print("="*80)
        
        # Convert timestamp
        if 'recorded_at' in df.columns:
            df['recorded_at'] = pd.to_datetime(df['recorded_at'], errors='coerce')
            print("✅ Converted 'recorded_at' to datetime")
        
        # Numeric columns that should be float
        numeric_cols = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'nh3', 
                       'temperature', 'humidity', 'wind_speed', 'pressure', 'aqi']
        
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
                print(f"✅ Converted '{col}' to numeric")
        
        return df
    
    def detect_outliers_iqr(self, df, column, multiplier=1.5):
        """
        Detect outliers using Interquartile Range (IQR) method
        """
        if column not in df.columns or df[column].isnull().all():
            return pd.Series([False] * len(df))
        
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        
        outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        self.outlier_stats[column] = {
            'Q1': Q1,
            'Q3': Q3,
            'IQR': IQR,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound,
            'outlier_count': outliers.sum()
        }
        
        return outliers
    
    def detect_outliers_zscore(self, df, column, threshold=3):
        """
        Detect outliers using Z-score method
        """
        if column not in df.columns or df[column].isnull().all():
            return pd.Series([False] * len(df))
        
        z_scores = np.abs(stats.zscore(df[column].dropna()))
        outliers_idx = df[column].dropna().index[z_scores > threshold]
        
        outliers = pd.Series([False] * len(df), index=df.index)
        outliers.loc[outliers_idx] = True
        
        return outliers
    
    def handle_outliers(self, df, method='cap', iqr_multiplier=1.5, zscore_threshold=3):
        """
        Comprehensive outlier detection and handling
        method: 'remove', 'cap', or 'keep'
        """
        print("\n" + "="*80)
        print("🔍 OUTLIER DETECTION AND HANDLING")
        print("="*80)
        
        pollutant_cols = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'nh3']
        weather_cols = ['temperature', 'humidity', 'wind_speed', 'pressure']
        all_numeric_cols = pollutant_cols + weather_cols + ['aqi']
        
        outliers_summary = []
        
        for col in all_numeric_cols:
            if col not in df.columns:
                continue
            
            # Detect outliers using IQR
            outliers_iqr = self.detect_outliers_iqr(df, col, iqr_multiplier)
            outliers_zscore = self.detect_outliers_zscore(df, col, zscore_threshold)
            
            # Combine both methods (outlier if detected by either method)
            outliers = outliers_iqr | outliers_zscore
            outlier_count = outliers.sum()
            
            if outlier_count > 0:
                outliers_summary.append({
                    'Column': col,
                    'Outliers_Count': outlier_count,
                    'Outliers_Percentage': f"{(outlier_count/len(df)*100):.2f}%"
                })
                
                if method == 'remove':
                    df = df[~outliers]
                    print(f"❌ Removed {outlier_count} outliers from '{col}'")
                elif method == 'cap':
                    # Cap outliers at bounds
                    if col in self.outlier_stats:
                        lower = self.outlier_stats[col]['lower_bound']
                        upper = self.outlier_stats[col]['upper_bound']
                        df.loc[df[col] < lower, col] = lower
                        df.loc[df[col] > upper, col] = upper
                        print(f"📌 Capped {outlier_count} outliers in '{col}'")
                else:  # keep
                    print(f"⚠️ Kept {outlier_count} outliers in '{col}'")
        
        if outliers_summary:
            outliers_df = pd.DataFrame(outliers_summary)
            print(f"\n📊 Outliers Summary:")
            print(outliers_df.to_string(index=False))
            self.preprocessing_report['outliers_removed'] = outliers_df.to_dict()
        
        return df
    
    def cross_source_consistency_check(self, df):
        """
        Check consistency across different data sources for same location/time
        """
        print("\n" + "="*80)
        print("🔄 CROSS-SOURCE CONSISTENCY CHECKS")
        print("="*80)
        
        if 'city' not in df.columns or 'source' not in df.columns:
            print("⚠️ Need 'city' and 'source' columns for consistency checks")
            return df
        
        # Check cities with multiple sources
        cities_multi_source = df.groupby('city')['source'].nunique()
        cities_multi_source = cities_multi_source[cities_multi_source > 1]
        
        print(f"🌍 Cities with multiple data sources: {len(cities_multi_source)}")
        
        consistency_issues = []
        
        for city in cities_multi_source.index:
            city_data = df[df['city'] == city].copy()
            
            # Compare AQI values across sources
            if 'aqi' in city_data.columns:
                aqi_by_source = city_data.groupby('source')['aqi'].mean()
                
                if len(aqi_by_source) > 1:
                    aqi_diff = aqi_by_source.max() - aqi_by_source.min()
                    aqi_std = aqi_by_source.std()
                    
                    if aqi_diff > 50:  # Threshold for significant difference
                        consistency_issues.append({
                            'city': city,
                            'metric': 'AQI',
                            'difference': f"{aqi_diff:.2f}",
                            'std_dev': f"{aqi_std:.2f}",
                            'sources': ', '.join(aqi_by_source.index)
                        })
        
        if consistency_issues:
            print(f"\n⚠️ Found {len(consistency_issues)} consistency issues:")
            consistency_df = pd.DataFrame(consistency_issues)
            print(consistency_df.to_string(index=False))
        else:
            print("✅ No major consistency issues found")
        
        return df
    
    def impute_missing_values(self, df, method='knn'):
        """
        Advanced missing value imputation
        method: 'knn', 'mean', 'median', 'forward_fill', 'interpolate'
        """
        print("\n" + "="*80)
        print("🔧 MISSING VALUE IMPUTATION")
        print("="*80)
        
        numeric_cols = ['pm25', 'pm10', 'no2', 'so2', 'co', 'o3', 'nh3',
                       'temperature', 'humidity', 'wind_speed', 'pressure', 'aqi']
        
        imputation_summary = []
        
        for col in numeric_cols:
            if col not in df.columns:
                continue
            
            missing_count = df[col].isnull().sum()
            if missing_count == 0:
                continue
            
            missing_pct = (missing_count / len(df) * 100)
            
            if method == 'knn':
                # KNN imputation (uses correlation with other features)
                temp_cols = [c for c in numeric_cols if c in df.columns and df[c].notnull().sum() > 0]
                if len(temp_cols) > 1:
                    imputer = KNNImputer(n_neighbors=5)
                    df[temp_cols] = imputer.fit_transform(df[temp_cols])
                    method_used = 'KNN'
                else:
                    df[col].fillna(df[col].median(), inplace=True)
                    method_used = 'Median (fallback)'
            
            elif method == 'mean':
                df[col].fillna(df[col].mean(), inplace=True)
                method_used = 'Mean'
            
            elif method == 'median':
                df[col].fillna(df[col].median(), inplace=True)
                method_used = 'Median'
            
            elif method == 'forward_fill':
                df.sort_values('recorded_at', inplace=True)
                df[col].fillna(method='ffill', inplace=True)
                df[col].fillna(method='bfill', inplace=True)  # Fill remaining
                method_used = 'Forward Fill'
            
            elif method == 'interpolate':
                df.sort_values('recorded_at', inplace=True)
                df[col].interpolate(method='linear', inplace=True)
                method_used = 'Linear Interpolation'
            
            imputation_summary.append({
                'Column': col,
                'Missing_Count': missing_count,
                'Missing_Percentage': f"{missing_pct:.2f}%",
                'Method': method_used
            })
        
        if imputation_summary:
            imputation_df = pd.DataFrame(imputation_summary)
            print(imputation_df.to_string(index=False))
            self.preprocessing_report['imputed_values'] = imputation_df.to_dict()
            print(f"\n✅ Imputed missing values using {method} method")
        
        return df
    
    def engineer_temporal_features(self, df):
        """
        Create comprehensive temporal features
        """
        print("\n" + "="*80)
        print("⏰ TEMPORAL FEATURE ENGINEERING")
        print("="*80)
        
        if 'recorded_at' not in df.columns:
            print("⚠️ No 'recorded_at' column found")
            return df
        
        df['recorded_at'] = pd.to_datetime(df['recorded_at'])
        
        # Extract basic temporal features
        df['year'] = df['recorded_at'].dt.year
        df['month'] = df['recorded_at'].dt.month
        df['day'] = df['recorded_at'].dt.day
        df['hour'] = df['recorded_at'].dt.hour
        df['day_of_week'] = df['recorded_at'].dt.dayofweek  # 0=Monday, 6=Sunday
        df['day_of_year'] = df['recorded_at'].dt.dayofyear
        df['week_of_year'] = df['recorded_at'].dt.isocalendar().week
        
        # Weekend indicator
        df['is_weekend'] = (df['day_of_week'] >= 5).astype(int)
        
        # Time of day categories
        def categorize_time_of_day(hour):
            if 6 <= hour < 12:
                return 'morning'
            elif 12 <= hour < 17:
                return 'afternoon'
            elif 17 <= hour < 21:
                return 'evening'
            else:
                return 'night'
        
        df['time_of_day'] = df['hour'].apply(categorize_time_of_day)
        
        # Season (Northern Hemisphere - India)
        def get_season(month):
            if month in [3, 4, 5]:
                return 'summer'
            elif month in [6, 7, 8, 9]:
                return 'monsoon'
            elif month in [10, 11]:
                return 'post_monsoon'
            else:  # 12, 1, 2
                return 'winter'
        
        df['season'] = df['month'].apply(get_season)
        
        # Rush hour indicator (morning: 7-10, evening: 17-20)
        df['is_rush_hour'] = ((df['hour'].between(7, 10)) | (df['hour'].between(17, 20))).astype(int)
        
        # Cyclical encoding for hour (preserves circular nature)
        df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24)
        df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24)
        
        # Cyclical encoding for month
        df['month_sin'] = np.sin(2 * np.pi * df['month'] / 12)
        df['month_cos'] = np.cos(2 * np.pi * df['month'] / 12)
        
        temporal_features = ['year', 'month', 'day', 'hour', 'day_of_week', 'day_of_year',
                           'week_of_year', 'is_weekend', 'time_of_day', 'season', 
                           'is_rush_hour', 'hour_sin', 'hour_cos', 'month_sin', 'month_cos']
        
        print(f"✅ Created {len(temporal_features)} temporal features:")
        for feat in temporal_features:
            print(f"   • {feat}")
        
        self.preprocessing_report['feature_engineering']['temporal'] = temporal_features
        
        return df
    
    def engineer_pollutant_features(self, df):
        """
        Create derived pollutant metrics and ratios
        """
        print("\n" + "="*80)
        print("🏭 POLLUTANT FEATURE ENGINEERING")
        print("="*80)
        
        pollutant_features = []
        
        # PM2.5 to PM10 ratio (indicates fine vs coarse particles)
        if 'pm25' in df.columns and 'pm10' in df.columns:
            df['pm25_pm10_ratio'] = df['pm25'] / (df['pm10'] + 1e-6)  # Avoid division by zero
            pollutant_features.append('pm25_pm10_ratio')
        
        # NO2 to SO2 ratio (traffic vs industrial pollution indicator)
        if 'no2' in df.columns and 'so2' in df.columns:
            df['no2_so2_ratio'] = df['no2'] / (df['so2'] + 1e-6)
            pollutant_features.append('no2_so2_ratio')
        
        # Total particulate matter
        if 'pm25' in df.columns and 'pm10' in df.columns:
            df['total_pm'] = df['pm25'] + df['pm10']
            pollutant_features.append('total_pm')
        
        # Nitrogen oxides proxy (if we had NO, but using NO2 as indicator)
        if 'no2' in df.columns:
            df['nox_indicator'] = df['no2'] * 1.5  # Approximate NOx from NO2
            pollutant_features.append('nox_indicator')
        
        # Pollutant severity categories
        if 'pm25' in df.columns:
            def categorize_pm25(value):
                if pd.isna(value):
                    return 'unknown'
                elif value <= 30:
                    return 'good'
                elif value <= 60:
                    return 'satisfactory'
                elif value <= 90:
                    return 'moderate'
                elif value <= 120:
                    return 'poor'
                elif value <= 250:
                    return 'very_poor'
                else:
                    return 'severe'
            
            df['pm25_category'] = df['pm25'].apply(categorize_pm25)
            pollutant_features.append('pm25_category')
        
        if 'aqi' in df.columns:
            def categorize_aqi(value):
                if pd.isna(value):
                    return 'unknown'
                elif value <= 50:
                    return 'good'
                elif value <= 100:
                    return 'moderate'
                elif value <= 200:
                    return 'unhealthy_sensitive'
                elif value <= 300:
                    return 'unhealthy'
                elif value <= 400:
                    return 'very_unhealthy'
                else:
                    return 'hazardous'
            
            df['aqi_category'] = df['aqi'].apply(categorize_aqi)
            pollutant_features.append('aqi_category')
        
        print(f"✅ Created {len(pollutant_features)} pollutant features:")
        for feat in pollutant_features:
            print(f"   • {feat}")
        
        self.preprocessing_report['feature_engineering']['pollutants'] = pollutant_features
        
        return df
    
    def engineer_weather_features(self, df):
        """
        Create derived weather metrics
        """
        print("\n" + "="*80)
        print("🌤️ WEATHER FEATURE ENGINEERING")
        print("="*80)
        
        weather_features = []
        
        # Heat Index (feels like temperature considering humidity)
        if 'temperature' in df.columns and 'humidity' in df.columns:
            def calculate_heat_index(temp, humidity):
                if pd.isna(temp) or pd.isna(humidity):
                    return np.nan
                # Simplified heat index formula
                hi = 0.5 * (temp + 61.0 + ((temp - 68.0) * 1.2) + (humidity * 0.094))
                return hi
            
            df['heat_index'] = df.apply(lambda x: calculate_heat_index(x['temperature'], x['humidity']), axis=1)
            weather_features.append('heat_index')
        
        # Temperature category
        if 'temperature' in df.columns:
            def categorize_temp(temp):
                if pd.isna(temp):
                    return 'unknown'
                elif temp < 15:
                    return 'cold'
                elif temp < 25:
                    return 'moderate'
                elif temp < 35:
                    return 'warm'
                else:
                    return 'hot'
            
            df['temp_category'] = df['temperature'].apply(categorize_temp)
            weather_features.append('temp_category')
        
        # Humidity category
        if 'humidity' in df.columns:
            def categorize_humidity(humidity):
                if pd.isna(humidity):
                    return 'unknown'
                elif humidity < 30:
                    return 'dry'
                elif humidity < 60:
                    return 'comfortable'
                else:
                    return 'humid'
            
            df['humidity_category'] = df['humidity'].apply(categorize_humidity)
            weather_features.append('humidity_category')
        
        # Wind speed category
        if 'wind_speed' in df.columns:
            def categorize_wind(speed):
                if pd.isna(speed):
                    return 'unknown'
                elif speed < 5:
                    return 'calm'
                elif speed < 15:
                    return 'light'
                elif speed < 25:
                    return 'moderate'
                else:
                    return 'strong'
            
            df['wind_category'] = df['wind_speed'].apply(categorize_wind)
            weather_features.append('wind_category')
        
        print(f"✅ Created {len(weather_features)} weather features:")
        for feat in weather_features:
            print(f"   • {feat}")
        
        self.preprocessing_report['feature_engineering']['weather'] = weather_features
        
        return df
    
    def engineer_rolling_features(self, df, windows=[3, 6, 12, 24]):
        """
        Create rolling/moving average features
        windows: list of window sizes (in hours)
        """
        print("\n" + "="*80)
        print("📊 ROLLING/MOVING AVERAGE FEATURES")
        print("="*80)
        
        if 'recorded_at' not in df.columns:
            print("⚠️ Need 'recorded_at' column for rolling features")
            return df
        
        # Sort by timestamp and city for proper rolling calculation
        df = df.sort_values(['city', 'recorded_at'])
        
        rolling_cols = ['pm25', 'pm10', 'no2', 'aqi', 'temperature']
        rolling_features = []
        
        for col in rolling_cols:
            if col not in df.columns:
                continue
            
            for window in windows:
                # Rolling mean
                col_name = f'{col}_rolling_mean_{window}h'
                df[col_name] = df.groupby('city')[col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).mean()
                )
                rolling_features.append(col_name)
                
                # Rolling std (volatility)
                col_name = f'{col}_rolling_std_{window}h'
                df[col_name] = df.groupby('city')[col].transform(
                    lambda x: x.rolling(window=window, min_periods=1).std()
                )
                rolling_features.append(col_name)
        
        # Rate of change features
        for col in rolling_cols:
            if col not in df.columns:
                continue
            
            # 1-hour change
            col_name = f'{col}_change_1h'
            df[col_name] = df.groupby('city')[col].diff(1)
            rolling_features.append(col_name)
            
            # Percentage change
            col_name = f'{col}_pct_change_1h'
            df[col_name] = df.groupby('city')[col].pct_change(1) * 100
            rolling_features.append(col_name)
        
        print(f"✅ Created {len(rolling_features)} rolling/lag features")
        print(f"   • Windows: {windows} hours")
        print(f"   • Metrics: mean, std, change, pct_change")
        
        self.preprocessing_report['feature_engineering']['rolling'] = {
            'count': len(rolling_features),
            'windows': windows
        }
        
        return df
    
    def create_lag_features(self, df, lags=[1, 3, 6, 12, 24]):
        """
        Create lag features (previous values)
        lags: list of lag periods (in hours)
        """
        print("\n" + "="*80)
        print("⏮️ LAG FEATURES")
        print("="*80)
        
        df = df.sort_values(['city', 'recorded_at'])
        
        lag_cols = ['pm25', 'pm10', 'aqi', 'temperature', 'humidity']
        lag_features = []
        
        for col in lag_cols:
            if col not in df.columns:
                continue
            
            for lag in lags:
                col_name = f'{col}_lag_{lag}h'
                df[col_name] = df.groupby('city')[col].shift(lag)
                lag_features.append(col_name)
        
        print(f"✅ Created {len(lag_features)} lag features")
        print(f"   • Lags: {lags} hours")
        
        self.preprocessing_report['feature_engineering']['lags'] = {
            'count': len(lag_features),
            'lags': lags
        }
        
        return df
    
    def get_preprocessing_summary(self):
        """
        Print comprehensive preprocessing summary
        """
        print("\n" + "="*80)
        print("📋 PREPROCESSING SUMMARY REPORT")
        print("="*80)
        
        print("\n1️⃣ Missing Values:")
        if 'initial' in self.preprocessing_report['missing_values']:
            print("   Handled through imputation")
        
        print("\n2️⃣ Outliers:")
        if self.preprocessing_report['outliers_removed']:
            print("   Detected and handled")
        
        print("\n3️⃣ Feature Engineering:")
        if 'temporal' in self.preprocessing_report['feature_engineering']:
            print(f"   • Temporal features: {len(self.preprocessing_report['feature_engineering']['temporal'])}")
        if 'pollutants' in self.preprocessing_report['feature_engineering']:
            print(f"   • Pollutant features: {len(self.preprocessing_report['feature_engineering']['pollutants'])}")
        if 'weather' in self.preprocessing_report['feature_engineering']:
            print(f"   • Weather features: {len(self.preprocessing_report['feature_engineering']['weather'])}")
        if 'rolling' in self.preprocessing_report['feature_engineering']:
            print(f"   • Rolling features: {self.preprocessing_report['feature_engineering']['rolling']['count']}")
        if 'lags' in self.preprocessing_report['feature_engineering']:
            print(f"   • Lag features: {self.preprocessing_report['feature_engineering']['lags']['count']}")
        
        return self.preprocessing_report
    
    def run_full_pipeline(self, df, imputation_method='knn', outlier_method='cap',
                         add_rolling=True, add_lags=True):
        """
        Run complete preprocessing pipeline
        """
        print("\n" + "🚀"*40)
        print("STARTING FULL PREPROCESSING PIPELINE")
        print("🚀"*40)
        
        # Step 1: Initial inspection
        self.initial_data_inspection(df)
        
        # Step 2: Data type cleaning
        df = self.clean_data_types(df)
        
        # Step 3: Outlier handling
        df = self.handle_outliers(df, method=outlier_method)
        
        # Step 4: Cross-source consistency
        df = self.cross_source_consistency_check(df)
        
        # Step 5: Missing value imputation
        df = self.impute_missing_values(df, method=imputation_method)
        
        # Step 6: Temporal features
        df = self.engineer_temporal_features(df)
        
        # Step 7: Pollutant features
        df = self.engineer_pollutant_features(df)
        
        # Step 8: Weather features
        df = self.engineer_weather_features(df)
        
        # Step 9: Rolling features (optional)
        if add_rolling:
            df = self.engineer_rolling_features(df, windows=[3, 6, 12, 24])
        
        # Step 10: Lag features (optional)
        if add_lags:
            df = self.create_lag_features(df, lags=[1, 3, 6, 12, 24])
        
        # Final summary
        self.get_preprocessing_summary()
        
        print("\n" + "✅"*40)
        print(f"PREPROCESSING COMPLETE!")
        print(f"Final dataset shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print("✅"*40 + "\n")
        
        return df
    
    def save_processed_data(self, df, filepath='processed_air_quality_data.csv'):
        """
        Save processed data to CSV
        """
        df.to_csv(filepath, index=False)
        print(f"💾 Saved processed data to: {filepath}")
        print(f"   • Rows: {len(df)}")
        print(f"   • Columns: {len(df.columns)}")
        return filepath


# Example usage
if __name__ == "__main__":
    # Initialize preprocessor
    preprocessor = AirQualityPreprocessor()
    
    # Load data
    print("Loading data from CSV...")
    df = preprocessor.load_data(source='csv', filepath='unified_air_quality_data.csv')
    
    # Run full pipeline
    df_processed = preprocessor.run_full_pipeline(
        df,
        imputation_method='knn',  # Options: 'knn', 'mean', 'median', 'interpolate'
        outlier_method='cap',      # Options: 'cap', 'remove', 'keep'
        add_rolling=True,          # Add rolling averages
        add_lags=True              # Add lag features
    )
    
    # Save processed data
    preprocessor.save_processed_data(df_processed, 'processed_air_quality_data.csv')
    
    # Display sample
    print("\n📊 Sample of processed data:")
    print(df_processed.head())
    
    print("\n📋 All columns:")
    for i, col in enumerate(df_processed.columns, 1):
        print(f"{i}. {col}")
