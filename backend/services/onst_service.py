# services/onst_service.py

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

def get_onst_threats(asset: Dict) -> Dict[str, List]:
    """
    Stub for ONST. 
    Returns empty lists until you have a real URL & key.
    """
    logger.debug(f"ONST stub called for asset {asset.get('asset_id')}")
    return {"vulnerabilities": [], "threats": []}
