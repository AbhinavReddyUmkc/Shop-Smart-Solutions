import os, logging, requests
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed
from typing import Dict, List

logger     = logging.getLogger(__name__)
VT_API_URL = "https://www.virustotal.com/api/v3"
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(15))
def _vt_get(endpoint: str) -> Dict:
    headers = {"x-apikey": VT_API_KEY}
    resp = requests.get(f"{VT_API_URL}{endpoint}", headers=headers, timeout=15)
    resp.raise_for_status()
    return resp.json()

def get_virustotal_report(asset: Dict) -> List[Dict]:
    if not VT_API_KEY:
        logger.warning("VIRUSTOTAL_API_KEY not set → skipping VT")
        return []

    if asset.get("ip_address"):
        ep = f"/ip_addresses/{asset['ip_address']}"
    elif asset.get("domain"):
        ep = f"/domains/{asset['domain']}"
    else:
        return []

    try:
        data = _vt_get(ep).get("data", {}).get("attributes", {})
    except Exception:
        return []

    stats = data.get("last_analysis_stats", {})
    mal   = stats.get("malicious", 0)
    if mal == 0:
        return []

    severity = "high" if mal > 5 else "medium"
    score    = mal * 10
    return [{
        "id":          f"vt-{datetime.now().timestamp()}",
        "name":        "VirusTotal Detection",
        "description": f"{mal} engines flagged this asset",
        "severity":    severity,
        "score":       score,
        "source":      "virustotal"
    }]
