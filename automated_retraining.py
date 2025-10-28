"""
Automated Model Retraining Pipeline
Triggered by new data arrivals or scheduled intervals
"""

import os
import sys
import time
import logging
import json
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/retraining.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/air_quality_db')
MODEL_PATH = Path(os.getenv('MODEL_PATH', './models'))
RETRAIN_INTERVAL_HOURS = int(os.getenv('RETRAIN_INTERVAL_HOURS', '24'))
MIN_NEW_SAMPLES = int(os.getenv('MIN_NEW_SAMPLES', '100'))
PERFORMANCE_THRESHOLD = float(os.getenv('PERFORMANCE_THRESHOLD', '0.1'))  # 10% degradation triggers retrain

# Ensure directories exist
MODEL_PATH.mkdir(exist_ok=True)
Path('logs').mkdir(exist_ok=True)


class ModelRetrainer:
    """Automated model retraining pipeline"""
    
    def __init__(self):
        self.db_url = DATABASE_URL
        self.model_path = MODEL_PATH
        self.metadata_path = MODEL_PATH / 'metadata.json'
        self.metrics_path = MODEL_PATH / 'metrics.json'
        self.models = {}
        self.metadata = self.load_metadata()
        
    def load_metadata(self):
        """Load training metadata"""
        if self.metadata_path.exists():
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {
            'last_training_time': None,
            'last_data_timestamp': None,
            'training_samples': 0,
            'model_versions': {}
        }
    
    def save_metadata(self):
        """Save training metadata"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2, default=str)
    
    def get_db_connection(self):
        """Get database connection"""
        return psycopg2.connect(self.db_url)
    
    def check_new_data(self):
        """Check if new data is available for retraining"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Get latest data timestamp
            cursor.execute("""
                SELECT MAX(timestamp) as latest_timestamp,
                       COUNT(*) as total_samples
                FROM air_quality_data
            """)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            if not result or not result['latest_timestamp']:
                logger.warning("No data found in database")
                return False, 0
            
            latest_timestamp = result['latest_timestamp']
            total_samples = result['total_samples']
            
            # Check if we have new data
            last_data_timestamp = self.metadata.get('last_data_timestamp')
            if last_data_timestamp:
                last_data_timestamp = datetime.fromisoformat(last_data_timestamp)
                if latest_timestamp <= last_data_timestamp:
                    logger.info("No new data since last training")
                    return False, 0
            
            # Count new samples
            if last_data_timestamp:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM air_quality_data
                    WHERE timestamp > %s
                """, (last_data_timestamp,))
                new_samples = cursor.fetchone()[0]
                cursor.close()
                conn.close()
            else:
                new_samples = total_samples
            
            logger.info(f"Found {new_samples} new samples (total: {total_samples})")
            
            return new_samples >= MIN_NEW_SAMPLES, new_samples
            
        except Exception as e:
            logger.error(f"Error checking new data: {e}")
            return False, 0
    
    def fetch_training_data(self):
        """Fetch data from database for training"""
        try:
            logger.info("Fetching training data from database...")
            conn = self.get_db_connection()
            
            query = """
                SELECT 
                    aqd.pm25,
                    aqd.pm10,
                    aqd.no2,
                    aqd.so2,
                    aqd.co,
                    aqd.o3,
                    aqd.temperature,
                    aqd.humidity,
                    aqd.wind_speed,
                    aqd.aqi,
                    aqd.timestamp,
                    s.city,
                    s.latitude,
                    s.longitude
                FROM air_quality_data aqd
                JOIN stations s ON aqd.station_id = s.station_id
                WHERE aqd.pm25 IS NOT NULL 
                  AND aqd.aqi IS NOT NULL
                ORDER BY aqd.timestamp DESC
            """
            
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                logger.error("No data retrieved from database")
                return None
            
            logger.info(f"Retrieved {len(df)} samples")
            
            # Feature engineering
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['hour'] = df['timestamp'].dt.hour
            df['day_of_week'] = df['timestamp'].dt.dayofweek
            df['month'] = df['timestamp'].dt.month
            
            # Fill missing values with median
            numeric_cols = ['pm10', 'no2', 'so2', 'co', 'o3', 'temperature', 
                          'humidity', 'wind_speed']
            for col in numeric_cols:
                if col in df.columns:
                    df[col].fillna(df[col].median(), inplace=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching training data: {e}")
            return None
    
    def prepare_features(self, df):
        """Prepare features and target for training"""
        feature_columns = [
            'pm25', 'pm10', 'no2', 'so2', 'co', 'o3',
            'temperature', 'humidity', 'wind_speed',
            'hour', 'day_of_week', 'month',
            'latitude', 'longitude'
        ]
        
        # Ensure all feature columns exist
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features].copy()
        y = df['aqi'].copy()
        
        # Remove any rows with NaN
        mask = ~(X.isna().any(axis=1) | y.isna())
        X = X[mask]
        y = y[mask]
        
        return X, y, available_features
    
    def train_models(self, X_train, y_train, X_test, y_test):
        """Train multiple models"""
        models_config = {
            'linear_regression': LinearRegression(),
            'random_forest': RandomForestRegressor(
                n_estimators=100,
                max_depth=20,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            ),
            'gradient_boosting': GradientBoostingRegressor(
                n_estimators=100,
                max_depth=10,
                learning_rate=0.1,
                random_state=42
            )
        }
        
        results = {}
        
        for name, model in models_config.items():
            try:
                logger.info(f"Training {name}...")
                
                # Train model
                start_time = time.time()
                model.fit(X_train, y_train)
                training_time = time.time() - start_time
                
                # Predictions
                y_pred_train = model.predict(X_train)
                y_pred_test = model.predict(X_test)
                
                # Metrics
                metrics = {
                    'train_rmse': float(np.sqrt(mean_squared_error(y_train, y_pred_train))),
                    'test_rmse': float(np.sqrt(mean_squared_error(y_test, y_pred_test))),
                    'train_mae': float(mean_absolute_error(y_train, y_pred_train)),
                    'test_mae': float(mean_absolute_error(y_test, y_pred_test)),
                    'train_r2': float(r2_score(y_train, y_pred_train)),
                    'test_r2': float(r2_score(y_test, y_pred_test)),
                    'training_time': training_time,
                    'training_samples': len(X_train),
                    'test_samples': len(X_test)
                }
                
                logger.info(f"{name} - Test RMSE: {metrics['test_rmse']:.2f}, R²: {metrics['test_r2']:.4f}")
                
                results[name] = {
                    'model': model,
                    'metrics': metrics
                }
                
            except Exception as e:
                logger.error(f"Error training {name}: {e}")
        
        return results
    
    def save_models(self, results, feature_names):
        """Save trained models and metrics"""
        try:
            timestamp = datetime.now().isoformat()
            all_metrics = {}
            
            for name, data in results.items():
                model = data['model']
                metrics = data['metrics']
                
                # Save model
                model_file = self.model_path / f'{name}_model.pkl'
                joblib.dump(model, model_file)
                logger.info(f"Saved {name} to {model_file}")
                
                # Update version info
                version = self.metadata['model_versions'].get(name, 0) + 1
                self.metadata['model_versions'][name] = version
                
                # Store metrics
                all_metrics[name] = {
                    **metrics,
                    'version': version,
                    'timestamp': timestamp,
                    'feature_names': feature_names
                }
            
            # Save metrics
            with open(self.metrics_path, 'w') as f:
                json.dump(all_metrics, f, indent=2)
            logger.info(f"Saved metrics to {self.metrics_path}")
            
            # Update metadata
            self.metadata['last_training_time'] = timestamp
            self.save_metadata()
            
        except Exception as e:
            logger.error(f"Error saving models: {e}")
    
    def check_performance_degradation(self):
        """Check if current models need retraining due to performance degradation"""
        # This would compare current prediction errors with historical baseline
        # For now, we'll implement a simple check based on time
        if not self.metadata.get('last_training_time'):
            return True
        
        last_training = datetime.fromisoformat(self.metadata['last_training_time'])
        hours_since_training = (datetime.now() - last_training).total_seconds() / 3600
        
        return hours_since_training >= RETRAIN_INTERVAL_HOURS
    
    def run_retraining(self):
        """Execute the retraining pipeline"""
        logger.info("=" * 80)
        logger.info("Starting automated retraining pipeline")
        logger.info("=" * 80)
        
        try:
            # Check if retraining is needed
            has_new_data, new_samples = self.check_new_data()
            needs_retrain = self.check_performance_degradation()
            
            if not has_new_data and not needs_retrain:
                logger.info("No retraining needed at this time")
                return False
            
            logger.info(f"Retraining triggered - New samples: {new_samples}, Time-based: {needs_retrain}")
            
            # Fetch data
            df = self.fetch_training_data()
            if df is None or len(df) < 100:
                logger.error("Insufficient data for training")
                return False
            
            # Prepare features
            X, y, feature_names = self.prepare_features(df)
            logger.info(f"Prepared {len(X)} samples with {len(feature_names)} features")
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Train models
            results = self.train_models(X_train, y_train, X_test, y_test)
            
            if not results:
                logger.error("No models were successfully trained")
                return False
            
            # Save models
            self.save_models(results, feature_names)
            
            # Update metadata with latest data timestamp
            self.metadata['last_data_timestamp'] = df['timestamp'].max().isoformat()
            self.metadata['training_samples'] = len(X)
            self.save_metadata()
            
            logger.info("=" * 80)
            logger.info("Retraining completed successfully!")
            logger.info("=" * 80)
            
            return True
            
        except Exception as e:
            logger.error(f"Error in retraining pipeline: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False


def main():
    """Main execution loop"""
    logger.info("Automated Retraining Service Started")
    logger.info(f"Retrain interval: {RETRAIN_INTERVAL_HOURS} hours")
    logger.info(f"Minimum new samples: {MIN_NEW_SAMPLES}")
    
    retrainer = ModelRetrainer()
    
    # Run initial training if no models exist
    if not list(MODEL_PATH.glob('*_model.pkl')):
        logger.info("No existing models found. Running initial training...")
        retrainer.run_retraining()
    
    # Continuous monitoring loop
    while True:
        try:
            retrainer.run_retraining()
            
            # Wait for next check (check every hour)
            sleep_time = 3600  # 1 hour
            logger.info(f"Waiting {sleep_time/3600:.1f} hours until next check...")
            time.sleep(sleep_time)
            
        except KeyboardInterrupt:
            logger.info("Retraining service stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(300)  # Wait 5 minutes before retry


if __name__ == '__main__':
    main()
