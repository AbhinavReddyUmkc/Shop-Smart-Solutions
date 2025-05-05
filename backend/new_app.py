from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

# Database connection parameters
DB_NAME = os.environ.get("DB_NAME", "threat_intelligence")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "1234")
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "5432")

logger.info(f"Database connection parameters: DB_NAME={DB_NAME}, DB_USER={DB_USER}, DB_HOST={DB_HOST}, DB_PORT={DB_PORT}")

def get_db_connection():
    """Get a database connection"""
    try:
        logger.info(f"Connecting to database {DB_NAME} on {DB_HOST}:{DB_PORT} as user {DB_USER}")
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        logger.info("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        raise

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic testing"""
    logger.info("Root endpoint accessed")
    return jsonify({
        "message": "Threat Intelligence API is running",
        "version": "1.0.0"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check endpoint accessed")
    try:
        # Test database connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        logger.info(f"Database connection test result: {result}")
        conn.close()
        
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "database": "connected"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "version": "1.0.0",
            "database": "disconnected",
            "error": str(e)
        }), 500

@app.route('/api/assets/stats', methods=['GET'])
def get_asset_stats():
    """Get statistics about assets for dashboard"""
    logger.info("Asset stats endpoint accessed")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total asset count
        cursor.execute("SELECT COUNT(*) as total FROM assets")
        total_count = cursor.fetchone()['total']
        
        # Count by type
        cursor.execute("SELECT type, COUNT(*) as count FROM assets GROUP BY type ORDER BY count DESC")
        types = cursor.fetchall()
        
        # Count by department
        cursor.execute("SELECT department, COUNT(*) as count FROM assets GROUP BY department ORDER BY count DESC")
        departments = cursor.fetchall()
        
        # Count by criticality
        cursor.execute("""
            SELECT criticality, COUNT(*) as count FROM assets 
            GROUP BY criticality 
            ORDER BY CASE criticality 
                WHEN 'Critical' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Medium' THEN 3 
                WHEN 'Low' THEN 4 
                ELSE 5 END
        """)
        criticality = cursor.fetchall()
        
        # Count by operating system
        cursor.execute("SELECT operating_system, COUNT(*) as count FROM assets GROUP BY operating_system ORDER BY count DESC")
        operating_systems = cursor.fetchall()
        
        # Count by location
        cursor.execute("SELECT location, COUNT(*) as count FROM assets GROUP BY location ORDER BY count DESC")
        locations = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            "total_assets": total_count,
            "by_type": types,
            "by_department": departments,
            "by_criticality": criticality,
            "by_operating_system": operating_systems,
            "by_location": locations,
        })
    except Exception as e:
        logger.error(f"Asset stats error: {str(e)}")
        return jsonify({
            "error": "Failed to get asset statistics",
            "message": str(e)
        }), 500

@app.route('/api/analysis/dashboard', methods=['GET'])
def get_dashboard_summary():
    """Get summary data for the dashboard"""
    logger.info("Dashboard summary endpoint accessed")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get asset counts
        cursor.execute("SELECT COUNT(*) as total FROM assets")
        total_assets = cursor.fetchone()['total']
        
        cursor.execute("SELECT COUNT(*) as critical FROM assets WHERE criticality = 'Critical'")
        critical_assets = cursor.fetchone()['critical']
        
        # Get threat counts
        cursor.execute("SELECT COUNT(*) as total FROM threats")
        total_threats = cursor.fetchone()['total']
        
        # Get high risk asset-threats
        cursor.execute("""
            SELECT COUNT(*) as count FROM asset_threats WHERE risk_score >= 8.0
        """)
        critical_threats = cursor.fetchone()['count']
        
        # Get recent threats (last 30 days)
        cursor.execute("""
            SELECT COUNT(*) as count FROM threats 
            WHERE published_date >= CURRENT_DATE - INTERVAL '30 days'
        """)
        recent_threats = cursor.fetchone()['count']
        
        # Get top vulnerable assets
        cursor.execute("""
            SELECT a.asset_id, a.name, a.type, a.department, a.criticality, 
                   COUNT(at.mapping_id) as threat_count,
                   AVG(at.risk_score) as avg_risk_score
            FROM assets a
            JOIN asset_threats at ON a.asset_id = at.asset_id
            GROUP BY a.asset_id, a.name, a.type, a.department, a.criticality
            ORDER BY avg_risk_score DESC, threat_count DESC
            LIMIT 5
        """)
        top_vulnerable_assets = cursor.fetchall()
        
        # Get threat count by severity
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN risk_score >= 8.0 THEN 1 ELSE 0 END) as critical,
                SUM(CASE WHEN risk_score >= 6.0 AND risk_score < 8.0 THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN risk_score >= 4.0 AND risk_score < 6.0 THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN risk_score < 4.0 THEN 1 ELSE 0 END) as low
            FROM asset_threats
        """)
        severity_counts = cursor.fetchone()
        
        # Get threat trend (last 6 months)
        cursor.execute("""
            SELECT TO_CHAR(discovered_date, 'YYYY-MM') as month, COUNT(*) as count
            FROM asset_threats
            WHERE discovered_date >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY month
            ORDER BY month
        """)
        threat_trend = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            "total_assets": total_assets,
            "critical_assets": critical_assets,
            "total_threats": total_threats,
            "critical_threats": critical_threats,
            "recent_threats": recent_threats,
            "top_vulnerable_assets": top_vulnerable_assets,
            "severity_counts": severity_counts,
            "threat_trend": threat_trend
        })
    except Exception as e:
        logger.error(f"Dashboard summary error: {str(e)}")
        return jsonify({
            "error": "Failed to get dashboard summary",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    # Print all registered routes
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule}, Endpoint: {rule.endpoint}")
    
    # Run the app
    print("\nStarting server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
