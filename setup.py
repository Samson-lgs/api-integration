"""
Quick Setup and Test Script
Tests database connection and runs initial data collection
"""

import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

def test_database_connection():
    """Test connection to PostgreSQL"""
    print("Testing PostgreSQL connection...")
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='postgres',
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.close()
        print("✓ PostgreSQL connection successful!")
        return True
    except Exception as e:
        print(f"✗ PostgreSQL connection failed: {e}")
        print("\nPlease ensure:")
        print("1. PostgreSQL is installed and running")
        print("2. Database credentials in .env file are correct")
        print("3. PostgreSQL service is started")
        return False

def setup_database():
    """Run database setup"""
    print("\nRunning database setup...")
    try:
        from database_setup import create_database, create_tables
        if create_database():
            if create_tables():
                print("✓ Database setup completed!")
                return True
        return False
    except Exception as e:
        print(f"✗ Database setup failed: {e}")
        return False

def collect_initial_data():
    """Collect initial batch of data"""
    print("\nCollecting initial data from CPCB API...")
    try:
        from cpcb_data_collector import CPCBDataCollector
        collector = CPCBDataCollector()
        collector.fetch_and_store()
        collector.close()
        print("✓ Initial data collection completed!")
        return True
    except Exception as e:
        print(f"✗ Data collection failed: {e}")
        return False

def main():
    print("="*60)
    print("CPCB Air Quality Data Collector - Setup")
    print("="*60)
    
    # Test database connection
    if not test_database_connection():
        print("\n⚠ Please fix database connection issues before proceeding.")
        print("\nUpdate the .env file with your PostgreSQL credentials:")
        print("  DB_HOST=localhost")
        print("  DB_PORT=5432")
        print("  DB_NAME=air_quality_db")
        print("  DB_USER=postgres")
        print("  DB_PASSWORD=your_password")
        return
    
    # Setup database
    if not setup_database():
        print("\n⚠ Database setup failed. Please check the error messages above.")
        return
    
    # Collect initial data
    if not collect_initial_data():
        print("\n⚠ Initial data collection failed. You can try running cpcb_data_collector.py manually.")
        return
    
    print("\n" + "="*60)
    print("✓ Setup completed successfully!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run 'python scheduled_collector.py' for continuous data collection")
    print("2. Run 'python data_query.py' to query and analyze data")
    print("3. Check README.md for more information")

if __name__ == "__main__":
    main()
