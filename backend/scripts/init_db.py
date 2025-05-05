import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time


def main():
    """Initialize the database and tables"""
    # Database connection parameters
    DB_NAME = os.environ.get("DB_NAME", "threat_intelligence")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASS = os.environ.get("DB_PASS", "1234")
    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "5432")
    
    # Wait for PostgreSQL to be available
    max_attempts = 10
    attempt = 0
    connected = False
    
    while attempt < max_attempts and not connected:
        try:
            # Connect to PostgreSQL server
            conn = psycopg2.connect(
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST,
                port=DB_PORT
            )
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            connected = True
            print("Connected to PostgreSQL server")
        except psycopg2.OperationalError:
            attempt += 1
            print(f"Waiting for PostgreSQL server (attempt {attempt}/{max_attempts})...")
            time.sleep(5)
    
    if not connected:
        print("Failed to connect to PostgreSQL server")
        return
    
    cursor = conn.cursor()
    
    # Check if database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
    database_exists = cursor.fetchone()
    
    # Create database if it doesn't exist
    if not database_exists:
        print(f"Creating database '{DB_NAME}'...")
        cursor.execute(f"CREATE DATABASE {DB_NAME}")
        print(f"Database '{DB_NAME}' created")
    else:
        print(f"Database '{DB_NAME}' already exists")
    
    # Close connection to server
    cursor.close()
    conn.close()
    
    # Connect to the database
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    print("Creating tables...")
    
    # Assets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assets (
        asset_id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        type VARCHAR(50) NOT NULL,
        department VARCHAR(50),
        location VARCHAR(100),
        manufacturer VARCHAR(100),
        model VARCHAR(100),
        operating_system VARCHAR(100),
        os_version VARCHAR(50),
        software_installed TEXT,
        hardware_version VARCHAR(50),
        firmware_version VARCHAR(50),
        product_id VARCHAR(100),
        cpe_identifier VARCHAR(255),
        serial_number VARCHAR(100),
        purchase_date DATE,
        ip_address VARCHAR(20),
        mac_address VARCHAR(20),
        status VARCHAR(20),
        criticality VARCHAR(20),
        vulnerabilities_last_scan_date DATE,
        owner VARCHAR(100),
        asset_description TEXT,
        data_classification VARCHAR(50)
    )
    """)
    
    # Vulnerabilities table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS vulnerabilities (
        id SERIAL PRIMARY KEY,
        cve_id VARCHAR(50) UNIQUE NOT NULL,
        description TEXT,
        severity VARCHAR(20),
        cvss_score FLOAT,
        published_date TIMESTAMP,
        last_modified TIMESTAMP
    )
    """)
    
    # Asset-Vulnerabilities mapping table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asset_vulnerabilities (
        asset_id INTEGER NOT NULL,
        vulnerability_id INTEGER NOT NULL,
        detected_date TIMESTAMP NOT NULL,
        PRIMARY KEY (asset_id, vulnerability_id),
        FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE,
        FOREIGN KEY (vulnerability_id) REFERENCES vulnerabilities (id) ON DELETE CASCADE
    )
    """)
    
    # Threats table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS threats (
        id SERIAL PRIMARY KEY,
        source VARCHAR(50) NOT NULL,
        external_id VARCHAR(100) NOT NULL,
        name VARCHAR(255),
        description TEXT,
        severity VARCHAR(20),
        confidence INTEGER,
        first_seen TIMESTAMP,
        last_seen TIMESTAMP,
        UNIQUE(source, external_id)
    )
    """)
    
    # Asset-Threats mapping table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS asset_threats (
        asset_id INTEGER NOT NULL,
        threat_id INTEGER NOT NULL,
        detected_date TIMESTAMP NOT NULL,
        PRIMARY KEY (asset_id, threat_id),
        FOREIGN KEY (asset_id) REFERENCES assets (asset_id) ON DELETE CASCADE,
        FOREIGN KEY (threat_id) REFERENCES threats (id) ON DELETE CASCADE
    )
    """)
    
    # API calls log table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS api_calls_log (
        log_id SERIAL PRIMARY KEY,
        api_name VARCHAR(50),
        endpoint VARCHAR(255),
        request_params JSONB,
        response_status INTEGER,
        response_data JSONB,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Risk analysis table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS risk_analysis (
        analysis_id SERIAL PRIMARY KEY,
        asset_id INTEGER REFERENCES assets(asset_id),
        threat_id INTEGER REFERENCES threats(id),
        llm_model VARCHAR(100),
        prompt TEXT,
        response TEXT,
        risk_score DECIMAL(3,1),
        confidence_score DECIMAL(3,1),
        analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Create indices for performance
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_assets_criticality ON assets(criticality);
    CREATE INDEX IF NOT EXISTS idx_assets_type ON assets(type);
    CREATE INDEX IF NOT EXISTS idx_assets_department ON assets(department);
    CREATE INDEX IF NOT EXISTS idx_asset_vulnerabilities_asset_id ON asset_vulnerabilities(asset_id);
    CREATE INDEX IF NOT EXISTS idx_asset_vulnerabilities_vulnerability_id ON asset_vulnerabilities(vulnerability_id);
    CREATE INDEX IF NOT EXISTS idx_asset_threats_asset_id ON asset_threats(asset_id);
    CREATE INDEX IF NOT EXISTS idx_asset_threats_threat_id ON asset_threats(threat_id);
    """)
    
    print("Tables created successfully")
    
    # Close connection
    cursor.close()
    conn.close()
    print("Database initialization complete")

if __name__ == "__main__":
    main()