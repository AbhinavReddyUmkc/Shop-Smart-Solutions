from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Enable CORS for all routes and all origins
CORS(app)

# Import blueprints after app creation to avoid circular imports
from api import assets, threats, analysis

# Register blueprints
app.register_blueprint(assets.bp)
app.register_blueprint(threats.bp)
app.register_blueprint(analysis.bp)

# Load configuration based on environment
if os.environ.get('FLASK_ENV') == 'production':
    app.config.from_object('config.ProductionConfig')
else:
    app.config.from_object('config.DevelopmentConfig')

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic testing"""
    logger.info("Root endpoint accessed")
    return jsonify({
        "message": "Threat Intelligence API is running",
        "version": "1.0.0"
    })

# Import database connection after app creation
from services.database import get_db_connection

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring"""
    logger.info("Health check endpoint accessed")
    try:
        # Test database connection
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            logger.info(f"Database connection test result: {result}")
        
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

if __name__ == '__main__':
     # debug helper: list all registered routes
    for rule in app.url_map.iter_rules():
        print(rule)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))