# /src/risk_prioritization.py

def prioritize_risks(threats):
    """
    Sort threats by risk_score in descending order to prioritize the most severe.
    
    Args:
        threats (list of dict): Each dict contains 'name' and 'risk_score'
    
    Returns:
        list: Sorted list of threats by risk_score
    """
    return sorted(threats, key=lambda x: x["risk_score"], reverse=True)

# Example usage
if __name__ == "__main__":
    threats = [
        {"name": "SQL Injection", "risk_score": 20},
        {"name": "Phishing", "risk_score": 30},
        {"name": "DDoS", "risk_score": 25}
    ]

    top_threats = prioritize_risks(threats)
    for threat in top_threats:
        print(f"Threat: {threat['name']}, Risk Score: {threat['risk_score']}")
