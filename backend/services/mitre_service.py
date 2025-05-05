import os
import json
import logging
import requests
from typing import Dict, List

logger = logging.getLogger(__name__)

# Cache for MITRE ATT&CK data to avoid repeated API calls
MITRE_CACHE = {}

def get_mitre_threats(asset: Dict) -> List[Dict]:
    """
    Get relevant MITRE ATT&CK techniques based on asset properties.
    
    Returns a list of relevant threat techniques.
    """
    try:
        # Use cached data if available
        if MITRE_CACHE and "techniques" in MITRE_CACHE:
            logger.info("Using cached MITRE ATT&CK data")
            techniques = MITRE_CACHE["techniques"]
        else:
            # Fetch MITRE ATT&CK data
            logger.info("Fetching MITRE ATT&CK data")
            mitre_url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
            response = requests.get(mitre_url)
            
            if response.status_code != 200:
                logger.error(f"Error fetching MITRE data: {response.status_code}")
                return []
            
            # Parse the MITRE ATT&CK data
            mitre_data = response.json()
            
            # Extract techniques
            techniques = []
            for obj in mitre_data.get("objects", []):
                if obj.get("type") == "attack-pattern":
                    technique = {
                        "id": obj.get("external_references", [{}])[0].get("external_id", ""),
                        "name": obj.get("name", ""),
                        "description": obj.get("description", ""),
                        "platforms": obj.get("x_mitre_platforms", []),
                        "tactics": [phase.get("phase_name", "") for phase in obj.get("kill_chain_phases", [])]
                    }
                    techniques.append(technique)
            
            # Cache the data
            MITRE_CACHE["techniques"] = techniques
        
        # Extract asset properties for matching
        asset_type = asset.get("type", "").lower()
        os = asset.get("operating_system", "").lower()
        software = [s.lower() for s in asset.get("software_installed", "").split(";")]
        
        # Determine relevant platforms based on asset OS
        platforms = []
        if "windows" in os:
            platforms.append("windows")
        elif "linux" in os or "ubuntu" in os:
            platforms.append("linux")
        elif "macos" in os:
            platforms.append("macos")
        
        # Additional platforms based on asset type
        if asset_type in ["server", "web server", "application server", "database server"]:
            platforms.extend(["linux", "windows"])
        elif asset_type in ["firewall", "router", "switch", "network device"]:
            platforms.append("network")
        
        # Filter techniques by platform relevance
        relevant_techniques = []
        for technique in techniques:
            # Check if the technique applies to the asset's platforms
            platform_match = any(platform in technique["platforms"] for platform in platforms)
            
            # Prioritize certain tactics based on asset type
            priority_tactics = []
            if asset_type in ["server", "web server", "application server"]:
                priority_tactics = ["initial-access", "execution", "persistence", "privilege-escalation"]
            elif asset_type in ["database", "database server"]:
                priority_tactics = ["exfiltration", "collection", "credential-access"]
            elif asset_type in ["firewall", "router", "network device"]:
                priority_tactics = ["defense-evasion", "lateral-movement", "command-and-control"]
            
            tactic_match = any(tactic in technique["tactics"] for tactic in priority_tactics) if priority_tactics else True
            
            if platform_match and tactic_match:
                relevant_techniques.append(technique)
        
        # Sort techniques by relevance (placeholder logic - could be improved)
        sorted_techniques = sorted(relevant_techniques, key=lambda x: len(x["tactics"]), reverse=True)
        
        # Return the top 10 most relevant techniques
        return sorted_techniques[:10]
    
    except Exception as e:
        logger.error(f"Error getting MITRE threats: {str(e)}")
        return []