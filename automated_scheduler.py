"""
Automated Scheduler for AQI Prediction System
Handles hourly data collection and daily model retraining
"""

import schedule
import time
import logging
from datetime import datetime
from real_time_collector import MultiSourceDataCollector
from ml_prediction_engine import AQIPredictionEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def collect_data():
    """Run hourly data collection"""
    try:
        logger.info("\n" + "="*70)
        logger.info("HOURLY DATA COLLECTION STARTED")
        logger.info("="*70)
        
        collector = MultiSourceDataCollector()
        collector.collect_all_sources()
        
        logger.info("="*70)
        logger.info("HOURLY DATA COLLECTION COMPLETED")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Data collection failed: {e}")


def generate_predictions():
    """Generate predictions for all cities"""
    try:
        logger.info("\n" + "="*70)
        logger.info("PREDICTION GENERATION STARTED")
        logger.info("="*70)
        
        engine = AQIPredictionEngine(model_type='xgboost')
        
        # Load existing model
        try:
            engine.load_model()
        except FileNotFoundError:
            logger.warning("No existing model found. Training new model...")
            df = engine.fetch_training_data(days=30)
            if not df.empty:
                from sklearn.model_selection import train_test_split
                X, y = engine.prepare_data(df)
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
                engine.train_model(X_train, y_train)
                metrics = engine.evaluate_model(X_test, y_test)
                engine.save_model(metrics)
        
        # Generate predictions for all cities
        cities = [
            'Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Kolkata',
            'Hyderabad', 'Pune', 'Ahmedabad', 'Jaipur', 'Lucknow'
        ]
        
        for city in cities:
            logger.info(f"Generating predictions for {city}...")
            predictions = engine.predict_future(city, hours_ahead=48)
            if predictions:
                engine.store_predictions(predictions)
                logger.info(f"  ✓ Stored {len(predictions)} predictions")
            else:
                logger.warning(f"  ✗ No predictions generated for {city}")
        
        logger.info("="*70)
        logger.info("PREDICTION GENERATION COMPLETED")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Prediction generation failed: {e}")


def retrain_models():
    """Retrain ML models with new data"""
    try:
        logger.info("\n" + "="*70)
        logger.info("MODEL RETRAINING STARTED")
        logger.info("="*70)
        
        # Train all model types
        model_types = ['xgboost', 'random_forest', 'linear']
        
        for model_type in model_types:
            logger.info(f"\nRetraining {model_type} model...")
            engine = AQIPredictionEngine(model_type=model_type)
            
            success = engine.auto_retrain(retrain_threshold_days=7)
            
            if success:
                logger.info(f"✓ {model_type} model retrained successfully")
            else:
                logger.warning(f"✗ {model_type} model retraining skipped")
        
        logger.info("\n" + "="*70)
        logger.info("MODEL RETRAINING COMPLETED")
        logger.info("="*70 + "\n")
        
    except Exception as e:
        logger.error(f"Model retraining failed: {e}")


def check_alerts():
    """Check for health alerts and send notifications"""
    try:
        import psycopg2
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        conn = psycopg2.connect(os.getenv('DATABASE_URL'))
        cursor = conn.cursor()
        
        # Find cities with high AQI
        cursor.execute("""
            SELECT 
                city,
                ROUND(AVG(aqi)) as aqi,
                get_aqi_category(ROUND(AVG(aqi))) as category
            FROM raw_air_quality_data
            WHERE timestamp >= NOW() - INTERVAL '1 hour'
            GROUP BY city
            HAVING AVG(aqi) > 150
        """)
        
        high_aqi_cities = cursor.fetchall()
        
        for city_data in high_aqi_cities:
            city, aqi, category = city_data
            
            # Check if alert already exists
            cursor.execute("""
                SELECT COUNT(*) 
                FROM health_alerts 
                WHERE city = %s 
                    AND is_active = TRUE 
                    AND created_at >= NOW() - INTERVAL '1 hour'
            """, (city,))
            
            existing = cursor.fetchone()[0]
            
            if existing == 0:
                # Create new alert
                severity = 'unhealthy' if aqi <= 200 else 'very_unhealthy' if aqi <= 300 else 'hazardous'
                message = f"Air quality in {city} is {category} (AQI: {aqi}). Limit outdoor activities."
                
                cursor.execute("""
                    INSERT INTO health_alerts (city, alert_type, severity, message, aqi_value)
                    VALUES (%s, %s, %s, %s, %s)
                """, (city, 'aqi_high', severity, message, aqi))
                
                logger.info(f"⚠️  Alert created for {city}: AQI {aqi} ({category})")
        
        conn.commit()
        conn.close()
        
    except Exception as e:
        logger.error(f"Alert check failed: {e}")


def run_scheduler():
    """Run the scheduler"""
    logger.info("\n" + "="*70)
    logger.info("AQI PREDICTION SYSTEM - AUTOMATED SCHEDULER")
    logger.info("="*70)
    logger.info("Schedule:")
    logger.info("  • Data Collection: Every hour at :00")
    logger.info("  • Prediction Generation: Every hour at :15")
    logger.info("  • Model Retraining: Daily at 02:00 AM")
    logger.info("  • Health Alerts Check: Every 30 minutes")
    logger.info("="*70 + "\n")
    
    # Schedule tasks
    schedule.every().hour.at(":00").do(collect_data)
    schedule.every().hour.at(":15").do(generate_predictions)
    schedule.every().day.at("02:00").do(retrain_models)
    schedule.every(30).minutes.do(check_alerts)
    
    # Run initial collection
    logger.info("Running initial data collection...")
    collect_data()
    
    logger.info("Running initial prediction generation...")
    generate_predictions()
    
    logger.info("\nScheduler is now running. Press Ctrl+C to stop.")
    
    # Keep running
    while True:
        try:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")
            break
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
            time.sleep(60)  # Wait before retrying


if __name__ == "__main__":
    run_scheduler()
