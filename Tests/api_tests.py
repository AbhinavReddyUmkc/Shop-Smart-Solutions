import pytest
import requests

# Test Shodan API Integration
def test_shodan_api():
    IP = "8.8.8.8"
    API_KEY = "your_shodan_api_key"
    URL = f"https://api.shodan.io/shodan/host/{IP}?key={API_KEY}"

    response = requests.get(URL)
    data = response.json()

    assert response.status_code == 200, "Shodan API request failed"
    assert "ports" in data, "Shodan API response does not contain 'ports'"
    assert isinstance(data["ports"], list), "Ports data should be a list"

# Test Risk Assessment API
def test_risk_assessment():
    URL = "http://localhost:5000/risk_score/4/5"
    response = requests.get(URL)
    data = response.json()

    assert response.status_code == 200, "Risk assessment API request failed"
    assert "risk_score" in data, "API response missing 'risk_score'"
    assert data["risk_score"] == 20, "Incorrect risk score calculation"

# Run tests
if __name__ == "__main__":
    pytest.main()
