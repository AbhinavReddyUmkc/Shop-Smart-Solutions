import requests
import json
import os
from tenacity import retry, stop_after_attempt, wait_fixed
from services.database import get_db_cursor
from services.nvd_service import log_api_call

# AlienVault OTX API configuration
OTX_API_URL = "https://otx.alienvault.com/api/v1"
OTX_API_KEY = os.environ.get('OTX_API_KEY', 'd2435e058f11fbd4c49ae3a8dd9dd8cc709088727a1a9c13774544281074180f')

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def search_threats_by_ip(ip_address):
    """Search for threats associated with an IP address"""
    headers = {'X-OTX-API-KEY': OTX_API_KEY}
    endpoint = f"{OTX_API_URL}/indicators/IPv4/{ip_address}/general"
    
    try:
        # Make the request
        response = requests.get(endpoint, headers=headers)
        
        # Log the API call
        log_api_call('AlienVault OTX', endpoint, {}, response.status_code, 
                    response.json() if response.status_code == 200 else {})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"AlienVault API Error: {response.status_code} - {response.text}")
            return {"error": f"AlienVault API Error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {"error": str(e)}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def search_threats_by_hostname(hostname):
    """Search for threats associated with a hostname/domain"""
    headers = {'X-OTX-API-KEY': OTX_API_KEY}
    endpoint = f"{OTX_API_URL}/indicators/hostname/{hostname}/general"
    
    try:
        # Make the request
        response = requests.get(endpoint, headers=headers)
        
        # Log the API call
        log_api_call('AlienVault OTX', endpoint, {}, response.status_code, 
                    response.json() if response.status_code == 200 else {})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"AlienVault API Error: {response.status_code} - {response.text}")
            return {"error": f"AlienVault API Error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {"error": str(e)}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def get_pulses_by_ip(ip_address):
    """Get OTX pulses (threat intelligence) for an IP address"""
    headers = {'X-OTX-API-KEY': OTX_API_KEY}
    endpoint = f"{OTX_API_URL}/indicators/IPv4/{ip_address}/pulse_info"
    
    try:
        # Make the request
        response = requests.get(endpoint, headers=headers)
        
        # Log the API call
        log_api_call('AlienVault OTX', endpoint, {}, response.status_code, 
                    response.json() if response.status_code == 200 else {})
        
        if response.status_code == 200:
            return response.json()
        else:
            print(f"AlienVault API Error: {response.status_code} - {response.text}")
            return {"error": f"AlienVault API Error: {response.status_code}"}
    
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {"error": str(e)}

def process_otx_data(data, asset):
    """Process OTX data and format for database storage"""
    threats = []
    
    # Process general info
    if 'pulse_info' in data:
        pulses = data['pulse_info'].get('pulses', [])
        for pulse in pulses:
            threat = {
                'cve_id': None,  # OTX pulses may not have CVE IDs
                'source': 'AlienVault OTX',
                'name': pulse.get('name', 'Unknown Threat'),
                'description': pulse.get('description', ''),
                'affected_asset_types': asset['type'],
                'cvss_score': 5.0,  # Default score, will be refined by LLM
                'cvss_severity': 'MEDIUM',
                'cvss_vector': '',
                'published_date': pulse.get('created', None),
                'reference_url': pulse.get('references', [''])[0] if pulse.get('references') else ''
            }
            
            # Look for CVE references in tags
            for tag in pulse.get('tags', []):
                if tag.startswith('CVE-'):
                    threat['cve_id'] = tag
                    break
            
            threats.append(threat)
    
    return threats