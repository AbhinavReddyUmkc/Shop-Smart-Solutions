from flask import Flask, jsonify
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a simple Flask app for testing
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    """Root endpoint for basic testing"""
    logger.info("Root endpoint accessed")
    return "Root endpoint is working!"

@app.route('/test', methods=['GET'])
def test():
    """Test endpoint"""
    logger.info("Test endpoint accessed")
    return "Test endpoint is working!"

@app.route('/api/test', methods=['GET'])
def api_test():
    """API test endpoint"""
    logger.info("API test endpoint accessed")
    return "API test endpoint is working!"

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    logger.info("Health endpoint accessed")
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

if __name__ == '__main__':
    # Print all registered routes
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"Route: {rule}, Endpoint: {rule.endpoint}")
    
    # Run the app
    print("\nStarting test server...")
    app.run(host='0.0.0.0', port=5001, debug=True)
