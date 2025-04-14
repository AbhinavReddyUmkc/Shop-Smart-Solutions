"""
Threat Mitigation Module
Provides automated remediation and countermeasures for detected threats.
"""
import os
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='threat_mitigation.log'
)
logger = logging.getLogger(__name__)

class ThreatMitigation:
    def __init__(self, config_file="config/mitigation_config.json"):
        self.config = self._load_config(config_file)
        self.remediation_history = []
        
    def _load_config(self, config_file):
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            return {}
    
    def automated_response(self, threat_type, threat_details=None):
        """
        Determine and execute appropriate automated response based on threat type.
        """
        responses = {
            "SQL Injection": "Apply Web Application Firewall (WAF) rules.",
            "XSS Attack": "Implement Content Security Policy headers.",
            "Phishing": "Enforce 2FA for all users.",
            "DDoS Attack": "Activate rate limiting and blackhole routing.",
            "Brute Force": "Implement account lockout policies.",
            "Malware": "Isolate infected systems and scan network.",
            "Data Exfiltration": "Block outbound traffic to suspicious domains.",
            "Credential Stuffing": "Force password reset for affected users.",
            "Unauthorized Access": "Revoke sessions and audit permissions.",
            "Privilege Escalation": "Lock down affected accounts and review permissions."
        }
        
        if threat_type in responses:
            logger.info(f"Initiating automated response for {threat_type}")
            action = responses[threat_type]
            
            # Record the remediation action
            self._record_remediation(threat_type, threat_details, action)
            
            return {
                "status": "success",
                "action": action,
                "message": f"Automated response initiated for {threat_type}"
            }
        else:
            logger.warning(f"No automated response available for: {threat_type}")
            return {
                "status": "warning",
                "action": "No automatic response available",
                "message": f"Unknown threat type: {threat_type}"
            }
    
    def _record_remediation(self, threat_type, threat_details, action):
        """Record remediation action in history."""
        record = {
            "timestamp": datetime.now().isoformat(),
            "threat_type": threat_type,
            "details": threat_details,
            "action": action
        }
        
        self.remediation_history.append(record)
        
        # Also save to file
        with open("logs/remediation_history.json", "a") as f:
            f.write(json.dumps(record) + "\n")
        
        logger.info(f"Recorded remediation action for {threat_type}")

# Example usage
if __name__ == "__main__":
    mitigator = ThreatMitigation()
    
    # Example: Get automated response for a phishing threat
    action = mitigator.automated_response("Phishing")
    print(f"Recommended Action: {action['action']}")