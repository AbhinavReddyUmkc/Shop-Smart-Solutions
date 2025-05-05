import os, logging, requests, ipaddress
from requests.exceptions import HTTPError
from typing import Dict, List

logger     = logging.getLogger(__name__)
OTX_API_KEY = os.getenv("OTX_API_KEY")
BASE_URL    = "https://otx.alienvault.com/api/v1"

def get_otx_threats(asset: Dict) -> List[Dict]:
    ip = asset.get("ip_address")
    # skip private IPs
    if ip:
        try:
            if ipaddress.ip_address(ip).is_private:
                logger.info(f"OTX: skipping private IP {ip}")
                return []
        except ValueError:
            pass

    if ip:
        url = f"{BASE_URL}/indicators/IPv4/{ip}/general"
    elif asset.get("domain"):
        url = f"{BASE_URL}/indicators/domain/{asset['domain']}/general"
    else:
        return []

    headers = {"X-OTX-API-KEY": OTX_API_KEY}
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
    except HTTPError as e:
        code = e.response.status_code if e.response else "?"
        logger.info(f"OTX: no data for {url} ({code})")
        return []
    except Exception as e:
        logger.error(f"OTX unexpected error: {e}")
        return []

    pulses = resp.json().get("pulse_info", {}).get("pulses", [])
    threats = []
    for p in pulses:
        sever = p.get("TLP","amber").lower()
        threats.append({
            "id":          p.get("id"),
            "name":        p.get("name"),
            "description": p.get("description"),
            "severity":    sever,
            "score":       70 if p.get("malware_families") else 40,
            "source":      "otx"
        })
    return threats
