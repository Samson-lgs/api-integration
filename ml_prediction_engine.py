"""
ML-Based AQI Prediction Engine
Trains models on historical data and generates 1-48 hour forecasts
Supports Linear Regression, Random Forest, XGBoost, and LSTM
"""

import os
import numpy as np
import pandas as pd
import psycopg2
from datetime import datetime, timedelta
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import xgboost as xgb
import pickle
import logging
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AQIPredictionEngine:
    """ML-based prediction engine for AQI forecasting"""
    
    def __init__(self, model_type='xgboost'):
        self.db_url = os.getenv('DATABASE_URL')
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = [
            'pm25', 'pm10', 'no2', 'so2', 'co', 'o3',
            'hour', 'day_of_week', 'month',
            'pm25_lag1', 'pm25_lag3', 'pm25_lag6',
            'pm25_rolling_mean_3h', 'pm25_rolling_mean_6h'
        ]
        
    def get_db_connection(self):
        """Get PostgreSQL connection"""
        return psycopg2.connect(self.db_url)
    
    def fetch_training_data(self, days=30):
        """Fetch historical data for training"""
        try:
            conn = self.get_db_connection()
            
            query = """
                SELECT 
                    city,
                    timestamp,
                    pm25,
                    pm10,
                    no2,
                    so2,
                    co,
                    o3,
                    aqi
                FROM raw_air_quality_data
                WHERE timestamp >= NOW() - INTERVAL '%s days'
                    AND pm25 IS NOT NULL
                    AND aqi IS NOT NULL
                ORDER BY city, timestamp
            """
            
            df = pd.read_sql_query(query, conn, params=(days,))
            conn.close()
            
            logger.info(f"Fetched {len(df)} records from last {days} days")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching training data: {e}")
            return pd.DataFrame()
    
    def engineer_features(self, df):
        """Create time-based and lag features"""
        # Time features
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        df['day_of_week'] = pd.to_datetime(df['timestamp']).dt.dayofweek
        df['month'] = pd.to_datetime(df['timestamp']).dt.month
        
        # Lag features for each city
        for city in df['city'].unique():
            city_mask = df['city'] == city
            df.loc[city_mask, 'pm25_lag1'] = df.loc[city_mask, 'pm25'].shift(1)
            df.loc[city_mask, 'pm25_lag3'] = df.loc[city_mask, 'pm25'].shift(3)
            df.loc[city_mask, 'pm25_lag6'] = df.loc[city_mask, 'pm25'].shift(6)
            
            # Rolling averages
            df.loc[city_mask, 'pm25_rolling_mean_3h'] = df.loc[city_mask, 'pm25'].rolling(window=3, min_periods=1).mean()
            df.loc[city_mask, 'pm25_rolling_mean_6h'] = df.loc[city_mask, 'pm25'].rolling(window=6, min_periods=1).mean()
        
        # Fill NaN values
        df = df.fillna(method='bfill').fillna(method='ffill')
        
        return df
    
    def prepare_data(self, df):
        """Prepare data for model training"""
        # Engineer features
        df = self.engineer_features(df)
        
        # Select features
        X = df[self.feature_columns]
        y = df['aqi']
        
        # Handle any remaining NaN
        X = X.fillna(X.mean())
        
        return X, y
    
    def train_model(self, X_train, y_train):
        """Train the selected ML model"""
        if self.model_type == 'linear':
            self.model = LinearRegression()
            logger.info("Training Linear Regression model...")
            
        elif self.model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                random_state=42,
                n_jobs=-1
            )
            logger.info("Training Random Forest model...")
            
        elif self.model_type == 'xgboost':
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                n_jobs=-1
            )
            logger.info("Training XGBoost model...")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        logger.info("Model training completed!")
    
    def evaluate_model(self, X_test, y_test):
        """Evaluate model performance"""
        X_test_scaled = self.scaler.transform(X_test)
        predictions = self.model.predict(X_test_scaled)
        
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        r2 = r2_score(y_test, predictions)
        
        logger.info(f"\nModel Evaluation:")
        logger.info(f"  MAE: {mae:.2f}")
        logger.info(f"  RMSE: {rmse:.2f}")
        logger.info(f"  R² Score: {r2:.4f}")
        
        return {
            'mae': mae,
            'rmse': rmse,
            'r2': r2,
            'model_type': self.model_type
        }
    
    def save_model(self, metrics, filepath='models/'):
        """Save trained model and scaler"""
        os.makedirs(filepath, exist_ok=True)
        
        model_file = f"{filepath}aqi_model_{self.model_type}.pkl"
        scaler_file = f"{filepath}aqi_scaler_{self.model_type}.pkl"
        metrics_file = f"{filepath}metrics.json"
        
        with open(model_file, 'wb') as f:
            pickle.dump(self.model, f)
        
        with open(scaler_file, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        # Save metrics
        import json
        with open(metrics_file, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        logger.info(f"Model saved to {model_file}")
        logger.info(f"Scaler saved to {scaler_file}")
    
    def load_model(self, filepath='models/'):
        """Load trained model and scaler"""
        model_file = f"{filepath}aqi_model_{self.model_type}.pkl"
        scaler_file = f"{filepath}aqi_scaler_{self.model_type}.pkl"
        
        with open(model_file, 'rb') as f:
            self.model = pickle.load(f)
        
        with open(scaler_file, 'rb') as f:
            self.scaler = pickle.load(f)
        
        logger.info(f"Model loaded from {model_file}")
    
    def predict_future(self, city, hours_ahead=48):
        """Generate predictions for 1-48 hours ahead"""
        try:
            conn = self.get_db_connection()
            
            # Get latest data for the city
            query = """
                SELECT *
                FROM raw_air_quality_data
                WHERE city = %s
                    AND timestamp >= NOW() - INTERVAL '24 hours'
                ORDER BY timestamp DESC
                LIMIT 24
            """
            
            df = pd.read_sql_query(query, conn, params=(city,))
            conn.close()
            
            if df.empty:
                logger.warning(f"No recent data for {city}")
                return []
            
            # Engineer features
            df = self.engineer_features(df)
            
            predictions = []
            last_timestamp = df['timestamp'].iloc[0]
            
            # Generate predictions for each hour
            for hour in range(1, hours_ahead + 1):
                pred_timestamp = last_timestamp + timedelta(hours=hour)
                
                # Prepare features (using latest data)
                features = df[self.feature_columns].iloc[0].copy()
                features['hour'] = pred_timestamp.hour
                features['day_of_week'] = pred_timestamp.dayofweek
                features['month'] = pred_timestamp.month
                
                # Make prediction
                X = np.array([features.values])
                X_scaled = self.scaler.transform(X)
                predicted_aqi = self.model.predict(X_scaled)[0]
                
                predictions.append({
                    'city': city,
                    'timestamp': pred_timestamp,
                    'predicted_aqi': float(predicted_aqi),
                    'hours_ahead': hour
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Prediction error for {city}: {e}")
            return []
    
    def store_predictions(self, predictions):
        """Store predictions in database"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            insert_query = """
                INSERT INTO aqi_predictions 
                (city, prediction_timestamp, predicted_aqi, hours_ahead, model_type, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (city, prediction_timestamp) 
                DO UPDATE SET 
                    predicted_aqi = EXCLUDED.predicted_aqi,
                    updated_at = NOW()
            """
            
            for pred in predictions:
                cursor.execute(insert_query, (
                    pred['city'],
                    pred['timestamp'],
                    pred['predicted_aqi'],
                    pred['hours_ahead'],
                    self.model_type,
                    datetime.now()
                ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Stored {len(predictions)} predictions in database")
            
        except Exception as e:
            logger.error(f"Error storing predictions: {e}")
    
    def auto_retrain(self, retrain_threshold_days=7):
        """Automatically retrain model with new data"""
        logger.info("\n" + "="*60)
        logger.info("AUTO-RETRAINING PROCESS STARTED")
        logger.info("="*60)
        
        # Fetch training data
        df = self.fetch_training_data(days=30)
        
        if len(df) < 100:
            logger.warning("Insufficient data for retraining. Need at least 100 records.")
            return False
        
        # Prepare data
        X, y = self.prepare_data(df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Train model
        self.train_model(X_train, y_train)
        
        # Evaluate
        metrics = self.evaluate_model(X_test, y_test)
        
        # Save model
        self.save_model(metrics)
        
        logger.info("="*60)
        logger.info("AUTO-RETRAINING COMPLETED SUCCESSFULLY")
        logger.info("="*60 + "\n")
        
        return True


if __name__ == "__main__":
    # Create prediction engine
    engine = AQIPredictionEngine(model_type='xgboost')
    
    # Train initial model
    logger.info("Training initial model...")
    df = engine.fetch_training_data(days=30)
    
    if not df.empty:
        X, y = engine.prepare_data(df)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        engine.train_model(X_train, y_train)
        metrics = engine.evaluate_model(X_test, y_test)
        engine.save_model(metrics)
        
        # Generate predictions for all cities
        cities = ['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata']
        for city in cities:
            logger.info(f"\nGenerating 48-hour predictions for {city}...")
            predictions = engine.predict_future(city, hours_ahead=48)
            engine.store_predictions(predictions)
        
        logger.info("\nPrediction engine ready!")
    else:
        logger.error("No training data available!")
