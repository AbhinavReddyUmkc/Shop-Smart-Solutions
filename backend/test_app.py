from flask import Flask, jsonify

# Create a minimal Flask app
app = Flask(__name__)

@app.route('/', methods=['GET'])
def root():
    return "Root is working!"

@app.route('/health', methods=['GET'])
def health():
    return "Health is working!"

@app.route('/api/test', methods=['GET'])
def api_test():
    return "API test is working!"

if __name__ == '__main__':
    print("Starting minimal test server...")
    app.run(host='0.0.0.0', port=5000, debug=True)
