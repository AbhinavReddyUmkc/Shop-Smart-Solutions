"""
Blue Team Defense Module
Provides automated defensive mechanisms based on detected threats.
"""
import os
import subprocess
import logging
import json
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='blue_team_defense.log'
)
logger = logging.getLogger(__name__)

class BlueTeamDefense:
    def __init__(self, config_file="config/defense_config.json"):
        self.config = self._load_config(config_file)
        self.threat_intel_api = self.config.get("threat_intel_api", "https://api.threatintel.example.com/v1")
        self.blocked_ips = set()
        self.malicious_domains = set()
        
    def _load_config(self, config_file):
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            return {}
        
    def block_ip(self, ip, reason="Malicious activity detected"):
        """Block an IP address using iptables."""
        if ip in self.blocked_ips:
            logger.info(f"IP {ip} already blocked")
            return
        
        try:
            # Verify IP format before executing command
            if self._validate_ip(ip):
                result = subprocess.run(
                    ["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                self.blocked_ips.add(ip)
                logger.info(f"Successfully blocked IP {ip}: {reason}")
                
                # Record action in database
                self._record_action("ip_block", ip, reason)
            else:
                logger.error(f"Invalid IP format: {ip}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to block IP {ip}: {e.stderr}")
    
    def _validate_ip(self, ip):
        """Validate IP address format."""
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        
        for part in parts:
            try:
                num = int(part)
                if num < 0 or num > 255:
                    return False
            except ValueError:
                return False
        
        return True
    
    def _record_action(self, action_type, target, reason):
        """Record defensive action in the database."""
        action = {
            "type": action_type,
            "target": target,
            "reason": reason,
            "timestamp": datetime.now().isoformat()
        }
        
        # In a real implementation, this would write to a database
        with open("logs/defense_actions.json", "a") as f:
            f.write(json.dumps(action) + "\n")

# Example usage
if __name__ == "__main__":
    defense = BlueTeamDefense()
    
    # Example: Block a known malicious IP
    defense.block_ip("192.168.1.10")