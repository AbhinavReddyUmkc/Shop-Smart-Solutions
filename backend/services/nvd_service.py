# services/nvd_service.py
import os, logging, requests
from typing import Dict, List

logger           = logging.getLogger(__name__)
NVD_API_KEY      = os.getenv("NVD_API_KEY")
NVD_API_BASE_URL = "https://services.nvd.nist.gov/rest/json/cves/2.0"

def get_vulnerabilities(asset: Dict) -> List[Dict]:
    cpe = asset.get("cpe_identifier")
    if not cpe:
        return []

    headers = {"apiKey": NVD_API_KEY} if NVD_API_KEY else {}
    params  = {
        "cpeName":        cpe,
        "startIndex":     0,
        "resultsPerPage": 20
    }

    try:
        resp = requests.get(NVD_API_BASE_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.error(f"NVD Error: {e}")
        return []

    vuls = []
    for entry in data.get("vulnerabilities", []):
        cve = entry.get("cve", {})
        meta = entry.get("cve", {}).get("CVE_data_meta", {}) or {}
        vid  = meta.get("ID") or cve.get("id") or cve.get("ID")
        desc = (cve.get("descriptions") or [{}])[0].get("value", "")
        # pick v3 if available, else v2
        metrics = entry.get("metrics", {})
        if "cvssMetricV31" in metrics:
            m = metrics["cvssMetricV31"][0]["cvssData"]
        elif "cvssMetricV2" in metrics:
            m = metrics["cvssMetricV2"][0]["cvssData"]
        else:
            continue
        score    = m.get("baseScore", 0.0)
        severity = m.get("baseSeverity", "UNKNOWN").lower()

        vuls.append({
            "id":          vid,
            "name":        vid,
            "description": desc,
            "severity":    severity,
            "score":       score * 10,    # scale to 0–100
            "source":      "nvd"
        })

    return vuls
