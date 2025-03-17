import requests
import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

# Shodan API configuration
SHODAN_API_KEY = "your_shodan_api_key"  # Replace with your Shodan API key
SHODAN_URL = "https://api.shodan.io/shodan/host/{ip}?key={api_key}"

# Database configuration
DB_CONFIG = {
    "dbname": "threat_intel", 
    "user": "admin",           
    "password": "1234",  
    "host": "localhost",       
    "port": "5432"             
}

def fetch_shodan_data(ip_address):
    """
    Fetch data from the Shodan API for a given IP address.
    """
    url = SHODAN_URL.format(ip=ip_address, api_key=SHODAN_API_KEY)
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from Shodan: {e}")
        return None

def store_threat_data(ip_address, data):
    """
    Store the fetched threat data in the PostgreSQL database.
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Insert the data into the threat_data table
        cursor.execute(
            "INSERT INTO threat_data (ip_address, ports, services) VALUES (%s, %s, %s)",
            (ip_address, str(data.get('ports')), str(data.get('hostnames')))
        conn.commit()  # Commit the transaction
        print("Data stored successfully!")
    except psycopg2.Error as e:
        print(f"Error storing data in the database: {e}")
    finally:
        # Close the database connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@app.route('/api/shodan/<ip_address>', methods=['GET'])
def shodan_integration(ip_address):
    """
    Endpoint to fetch and store Shodan data for a given IP address.
    """
    shodan_data = fetch_shodan_data(ip_address)
    if shodan_data:
        store_threat_data(ip_address, shodan_data)
        return jsonify({"status": "success", "data": shodan_data}), 200
    else:
        return jsonify({"status": "error", "message": "Failed to fetch Shodan data"}), 500

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app in debug mode