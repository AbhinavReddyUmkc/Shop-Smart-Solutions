# services/llm_service.py

import os, logging, requests, re
from requests.exceptions import HTTPError
from typing import Dict

logger  = logging.getLogger(__name__)
HF_KEY  = os.getenv("HUGGINGFACE_API_KEY")
HF_URL  = "https://api-inference.huggingface.co/models/gpt2"

def generate_risk_score(asset: Dict, threat_data: Dict) -> float:
    """
    Returns a risk score 0–100. Tries to parse HF output for a number,
    else falls back to basic severity-count calculation.
    """
    # 1) Count-based fallback
    def basic_score():
        w = {"Critical":25,"High":15,"Medium":10,"Low":5}
        vs = sum(w.get(v.get("severity","Low"),5) for v in threat_data.get("nvd",[]))
        ts = sum(w.get(t.get("severity","Low"),5) for t in threat_data.get("otx",[])+threat_data.get("virustotal",[]))
        total = vs + ts
        import math
        return min(100, round(25 * math.log10(1 + total),1))

    if not HF_KEY:
        logger.info("HuggingFace key missing → basic_score")
        return basic_score()

    # 2) Build minimal prompt
    counts = {k: len(v) for k,v in threat_data.items()}
    prompt = (
        f"NVDs:{counts.get('nvd',0)} "
        f"OTXs:{counts.get('otx',0)} "
        f"VTs:{counts.get('virustotal',0)}\n"
        "Return *only* a single number from 0 to 100."
    )
    headers = {"Authorization": f"Bearer {HF_KEY}", "Content-Type": "application/json"}

    try:
        resp = requests.post(HF_URL, headers=headers,
                             json={"inputs": prompt}, timeout=20)
        resp.raise_for_status()
        gen = resp.json()[0].get("generated_text","")
        # 3) Extract the first float-looking group
        m = re.search(r"(\d+(?:\.\d+)?)", gen)
        if m:
            num = float(m.group(1))
            return max(0.0, min(100.0, num))
        else:
            logger.info(f"LLM returned no number → basic_score")
            return basic_score()

    except HTTPError as e:
        code = e.response.status_code if e.response else "?"
        logger.info(f"LLM HTTP {code} → basic_score")
        return basic_score()
    except Exception as e:
        logger.error(f"LLM unexpected error: {e}")
        return basic_score()
