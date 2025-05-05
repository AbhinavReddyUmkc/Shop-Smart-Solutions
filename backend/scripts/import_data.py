# backend/scripts/import_data.py
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime
import os

# Database connection parameters
DB_NAME = os.environ.get("DB_NAME", "threat_intelligence")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "1234")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

# CSV file path
CSV_FILE_PATH = r"C:\Users\mutlu\Downloads\it-assets-comprehensive-data.csv"

def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )

def import_asset_data():
    conn = None
    try:
        # Connect to the database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Read CSV file
        print(f"Reading CSV file from: {CSV_FILE_PATH}")
        df = pd.read_csv(CSV_FILE_PATH)
        
        # Convert date columns to proper format
        for date_col in ['purchase_date', 'vulnerabilities_last_scan_date']:
            if date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce').dt.date
        
        # Prepare data for insertion
        columns = df.columns.tolist()
        values = [tuple(row) for row in df.values]
        
        # Create the INSERT query
        insert_query = f"""
        INSERT INTO assets ({', '.join(columns)})
        VALUES %s
        ON CONFLICT (asset_id) DO UPDATE 
        SET {', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'asset_id'])}
        """
        
        # Execute batch insert
        execute_values(cursor, insert_query, values)
        
        # Commit the transaction
        conn.commit()
        print(f"Successfully imported {len(df)} assets.")
    
    except Exception as e:
        print(f"Error: {e}")
        if conn:
            conn.rollback()
    
    finally:
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    import_asset_data()
    print("Data import complete!")