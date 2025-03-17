import schedule
import time
from shodan_integration import fetch_shodan_data, store_threat_data

# List of IP addresses to monitor (you can add more IPs as needed)
IP_ADDRESSES = ["8.8.8.8", "1.1.1.1", "192.168.1.1"]

def run_osint_updates():
    """
    Fetch OSINT threat data for all IP addresses and store it in the database.
    """
    for ip in IP_ADDRESSES:
        print(f"Fetching data for IP: {ip}")
        shodan_data = fetch_shodan_data(ip)
        if shodan_data:
            store_threat_data(ip, shodan_data)
            print(f"Data for IP {ip} stored successfully!")
        else:
            print(f"Failed to fetch data for IP {ip}")

# Schedule the OSINT updates to run every 6 hours
schedule.every(6).hours.do(run_osint_updates)

if __name__ == "__main__":
    print("Starting OSINT threat intelligence auto-update scheduler...")
    # Run the scheduler indefinitely
    while True:
        schedule.run_pending()
        time.sleep(1)  # Sleep for 1 second to avoid high CPU usage