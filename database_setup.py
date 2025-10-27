"""
Database setup script for CPCB Air Quality Data
Creates necessary tables in PostgreSQL
"""

import psycopg2
from psycopg2 import sql
import os
from dotenv import load_dotenv

load_dotenv()

def create_database_connection():
    """Create a connection to PostgreSQL server"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database='postgres',  # Connect to default database first
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        conn.autocommit = True
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None

def create_database():
    """Create the air quality database if it doesn't exist"""
    conn = create_database_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        db_name = os.getenv('DB_NAME')
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(sql.SQL("CREATE DATABASE {}").format(
                sql.Identifier(db_name)
            ))
            print(f"Database '{db_name}' created successfully")
        else:
            print(f"Database '{db_name}' already exists")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating database: {e}")
        return False

def create_tables():
    """Create tables for storing air quality data"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        cursor = conn.cursor()
        
        # Create stations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stations (
                station_id VARCHAR(100) PRIMARY KEY,
                station_name VARCHAR(255) NOT NULL,
                city VARCHAR(100),
                state VARCHAR(100),
                latitude DECIMAL(10, 8),
                longitude DECIMAL(11, 8),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create air quality data table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS air_quality_data (
                id SERIAL PRIMARY KEY,
                station_id VARCHAR(100) REFERENCES stations(station_id),
                recorded_at TIMESTAMP NOT NULL,
                pollutant_id VARCHAR(50),
                pollutant_avg DECIMAL(10, 4),
                pollutant_max DECIMAL(10, 4),
                pollutant_min DECIMAL(10, 4),
                aqi DECIMAL(10, 2),
                aqi_category VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(station_id, recorded_at, pollutant_id)
            )
        """)
        
        # Create index for faster queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_station_recorded 
            ON air_quality_data(station_id, recorded_at)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_recorded_at 
            ON air_quality_data(recorded_at)
        """)
        
        conn.commit()
        print("Tables created successfully")
        
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error creating tables: {e}")
        return False

if __name__ == "__main__":
    print("Setting up database for CPCB Air Quality Data...")
    if create_database():
        if create_tables():
            print("\nDatabase setup completed successfully!")
        else:
            print("\nFailed to create tables")
    else:
        print("\nFailed to create database")
