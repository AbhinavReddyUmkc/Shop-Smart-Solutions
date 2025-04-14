"""
AI-Powered Threat Hunting Module
Implements AI-driven anomaly detection for proactive threat hunting.
"""
import json
import logging
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='ai_threat_hunting.log'
)
logger = logging.getLogger(__name__)

class AIThreatHunting:
    def __init__(self, config_file="config/threat_hunting_config.json"):
        self.config = self._load_config(config_file)
        self.llm_api_key = self.config.get("llm_api_key", "")
        self.llm_model = self.config.get("llm_model", "gpt-4")
        
    def _load_config(self, config_file):
        """Load configuration from file."""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_file} not found. Using defaults.")
            return {}
    
    def predict_threat_behavior(self, threat_description):
        """
        Use LLM to analyze security threats and predict possible attack vectors.
        """
        try:
            if self.llm_api_key:
                # If using OpenAI
                if "gpt" in self.llm_model.lower():
                    headers = {
                        "Authorization": f"Bearer {self.llm_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    data = {
                        "model": self.llm_model,
                        "messages": [
                            {"role": "system", "content": "You are a cybersecurity expert analyzing threats."},
                            {"role": "user", "content": f"Analyze this security threat and predict possible next attack vectors: {threat_description}"}
                        ]
                    }
                    
                    response = requests.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers=headers,
                        json=data
                    )
                    
                    if response.status_code == 200:
                        return response.json()["choices"][0]["message"]["content"]
                    else:
                        logger.error(f"LLM API error: {response.status_code} - {response.text}")
                        return "Error in threat analysis API call."
                else:
                    # Fallback to basic analysis
                    return self._basic_threat_analysis(threat_description)
            else:
                # Local analysis when no API key is available
                return self._basic_threat_analysis(threat_description)
                
        except Exception as e:
            logger.error(f"Failed to predict threat behavior: {str(e)}")
            return "Failed to analyze threat due to an error."
    
    def _basic_threat_analysis(self, threat_description):
        """Provide basic threat analysis when LLM is not available."""
        threat_types = {
            "sql injection": "Attacker may attempt to exfiltrate database contents or gain admin access.",
            "xss": "Attacker may try to steal cookies or session tokens from users.",
            "phishing": "Attacker may target additional users or escalate to spear phishing against executives.",
            "brute force": "Attacker may switch to credential stuffing or target other services with the same credentials.",
            "ddos": "Attacker may be using this as a distraction for other infiltration attempts."
        }
        
        threat_description = threat_description.lower()
        
        for threat_type, analysis in threat_types.items():
            if threat_type in threat_description:
                return f"Detected {threat_type}. {analysis}"
        
        return "Unknown threat pattern. Recommend increased monitoring and isolation of affected systems."

# Example usage
if __name__ == "__main__":
    threat_hunter = AIThreatHunting()
    
    # Example: Predict threat behavior
    prediction = threat_hunter.predict_threat_behavior("SQL Injection detected on login page")
    print(f"Predicted Next Steps: {prediction}")