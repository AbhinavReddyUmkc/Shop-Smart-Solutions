def calculate_risk(likelihood, impact):
    return likelihood * impact

threats = [
    {"threat": "SQL Injection", "likelihood": 4, "impact": 5},
    {"threat": "Phishing Attack", "likelihood": 5, "impact": 3},
]

for threat in threats:
    risk_score = calculate_risk(threat["likelihood"], threat["impact"])
    print(f"Threat: {threat['threat']}, Risk Score: {risk_score}")
