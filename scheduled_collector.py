"""
Scheduled CPCB Data Collector
Runs data collection at regular intervals for continuous monitoring
"""

import time
import schedule
from cpcb_data_collector import CPCBDataCollector
from datetime import datetime

def collect_data():
    """Function to be run on schedule"""
    print(f"\n{'='*60}")
    print(f"Data Collection Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    collector = CPCBDataCollector()
    try:
        collector.fetch_and_store()
    except Exception as e:
        print(f"Error during data collection: {e}")
    finally:
        collector.close()
    
    print(f"\n{'='*60}")
    print(f"Data Collection Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

def run_scheduler(interval_minutes=60):
    """Run the data collector on a schedule"""
    print(f"Starting scheduled data collection (every {interval_minutes} minutes)")
    print(f"Press Ctrl+C to stop\n")
    
    # Run immediately on start
    collect_data()
    
    # Schedule subsequent runs
    schedule.every(interval_minutes).minutes.do(collect_data)
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n\nScheduler stopped by user")
            break

if __name__ == "__main__":
    # Default: collect data every 60 minutes (1 hour)
    # You can change this value as needed
    run_scheduler(interval_minutes=60)
