import requests
import mysql.connector
import schedule
import time
from datetime import datetime

# ✅ API Keys (Replace with your real API keys)
SHODAN_API_KEY = "your_shodan_api_key"
HIBP_API_KEY = "your_hibp_api_key"
SECURITYTRAILS_API_KEY = "your_securitytrails_api_key"

# ✅ MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "your_mysql_password",
    "database": "threat_intel"
}

# ✅ Function to store threat data in MySQL
def store_threat_data(asset_id, threat_name, vulnerability_description, likelihood, impact):
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        query = """
        INSERT INTO tva_mapping (asset_id, threat_name, vulnerability_description, likelihood, impact, timestamp)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (asset_id, threat_name, vulnerability_description, likelihood, impact, datetime.now()))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Stored: {threat_name}")
    except Exception as e:
        print(f"❌ Database Error: {e}")

# ✅ Function to fetch data from Shodan API
def fetch_shodan_data(ip):
    url = f"https://api.shodan.io/shodan/host/{ip}?key={SHODAN_API_KEY}"
    response = requests.get(url).json()
    if "error" not in response:
        ports = response.get('ports', [])
        threat_name = f"Open Ports: {ports}"
        store_threat_data(1, threat_name, "Exposed services detected", 4, 5)

# ✅ Function to fetch data from Have I Been Pwned API
def fetch_hibp_data(email):
    url = f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}"
    headers = {"hibp-api-key": HIBP_API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        breaches = response.json()
        if breaches:
            for breach in breaches:
                store_threat_data(2, breach['Name'], "Compromised account found", 5, 5)

# ✅ Function to fetch data from SecurityTrails API
def fetch_securitytrails_data(domain):
    url = f"https://api.securitytrails.com/v1/domain/{domain}/subdomains"
    headers = {"APIKEY": SECURITYTRAILS_API_KEY}
    response = requests.get(url, headers=headers).json()
    if "subdomains" in response:
        subdomains = response["subdomains"]
        threat_name = f"Subdomains Found: {len(subdomains)}"
        store_threat_data(3, threat_name, "Potential attack surface detected", 3, 4)

# ✅ Function to automate the execution every 24 hours
def update_threat_data():
    print("🔍 Fetching latest threat intelligence data...")
    fetch_shodan_data("8.8.8.8")  # Example IP
    fetch_hibp_data("example@email.com")  # Example Email
    fetch_securitytrails_data("example.com")  # Example Domain
    print("✅ Threat intelligence data updated!")

# ✅ Schedule the script to run every 24 hours
schedule.every(24).hours.do(update_threat_data)

# ✅ Keep the script running
if __name__ == "__main__":
    while True:
        schedule.run_pending()
        time.sleep(3600)  # Check every hour
