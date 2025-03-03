# Git Documentation for API Integrations

## Shodan API Integration (Find Open Ports on a Server)

```python
import requests

API_KEY = "your_shodan_api_key"
IP = "8.8.8.8"
URL = f"https://api.shodan.io/shodan/host/{IP}?key={API_KEY}"

response = requests.get(URL)
print(response.json())
```

## Have I Been Pwned API Integration (Check for Leaked Credentials)

```bash
curl -H "hibp-api-key: YOUR_API_KEY" \  
"https://haveibeenpwned.com/api/v3/breachedaccount/test@example.com"
```

## VirusTotal API Integration (Check File Hash for Malware)

```python
import requests

API_KEY = "your_virustotal_api_key"
FILE_HASH = "hash_of_the_file"
URL = f"https://www.virustotal.com/api/v3/files/{FILE_HASH}"

headers = {
    "x-apikey": API_KEY
}

response = requests.get(URL, headers=headers)
print(response.json())
```

## Documentation on API Authentication and Usage

### Shodan API
- **Authentication:** API key is required and passed as a query parameter.
- **Request Method:** GET
- **Endpoint:** `https://api.shodan.io/shodan/host/{IP}?key={API_KEY}`

### Have I Been Pwned API
- **Authentication:** API key is required and passed in the header.
- **Request Method:** GET
- **Endpoint:** `https://haveibeenpwned.com/api/v3/breachedaccount/{email}`

### VirusTotal API
- **Authentication:** API key is required and passed in the header.
- **Request Method:** GET
- **Endpoint:** `https://www.virustotal.com/api/v3/files/{FILE_HASH}`
