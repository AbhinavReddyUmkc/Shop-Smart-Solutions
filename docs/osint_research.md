# OSINT Research Report

## Introduction
This report outlines our research on Open Source Intelligence (OSINT) tools that can be integrated into our Real-Time Threat Intelligence (RTTI) system. The goal is to identify tools that provide actionable threat intelligence and can be accessed via APIs. Below, we evaluate selected tools, their integration methods, and their relevance to the project.

---

## Selected OSINT Tools

### 1. **Shodan**
- **Purpose**: Detects exposed services and devices on the internet.
- **API Access**: [Shodan API Docs](https://developer.shodan.io/)
- **Integration**:
  - Use the API to scan for vulnerable devices and services.
  - Fetch data in JSON format for real-time threat analysis.
- **Feasibility**: Easy to integrate, provides comprehensive data on exposed services.

### 2. **Have I Been Pwned**
- **Purpose**: Checks if email addresses or passwords have been compromised in data breaches.
- **API Access**: [Have I Been Pwned API Docs](https://haveibeenpwned.com/API/v3)
- **Integration**:
  - Integrate the API to check for breached credentials.
  - Use the data to alert users about compromised accounts.
- **Feasibility**: Free tier available, easy to implement for credential monitoring.

### 3. **VirusTotal**
- **Purpose**: Analyzes files and URLs for malware and domain reputation.
- **API Access**: [VirusTotal API Docs](https://developers.virustotal.com/reference/overview)
- **Integration**:
  - Use the API to scan files and URLs for malicious content.
  - Fetch reputation scores for domains and IPs.
- **Feasibility**: Free tier has limitations, but useful for basic malware analysis.

### 4. **Censys**
- **Purpose**: Provides internet-wide scan data for exposed devices and services.
- **API Access**: [Censys API Docs](https://search.censys.io/api)
- **Integration**:
  - Use the API to gather data on exposed devices and services.
  - Integrate with the RTTI dashboard for real-time monitoring.
- **Feasibility**: Provides detailed data, but API access may require a subscription.

### 5. **theHarvester**
- **Purpose**: Gathers emails, subdomains, hosts, and open ports.
- **API Access**: [theHarvester GitHub](https://github.com/laramies/theHarvester)
- **Integration**:
  - Use the tool to collect OSINT data from public sources.
  - Integrate the output into the RTTI system for analysis.
- **Feasibility**: Open-source and easy to use, but requires manual integration.

---

## API Access Methods
- **Shodan**: API key required. Fetch data using HTTP GET requests.
- **Have I Been Pwned**: API key required. Use HTTP GET requests to check breached credentials.
- **VirusTotal**: API key required. Submit files/URLs for analysis and fetch results.
- **Censys**: API key required. Query the database for exposed devices and services.
- **theHarvester**: No API. Run the tool locally and parse the output for integration.

---

## Integration into the Web App
1. **Back-End Integration**:
   - Use Python libraries (e.g., `requests`) to interact with the APIs.
   - Fetch data from the APIs and store it in the database.
2. **Front-End Display**:
   - Display real-time threat intelligence on the dashboard.
   - Use charts and tables to visualize data (e.g., exposed services, breached credentials).
3. **Automation**:
   - Schedule periodic API calls to keep the data updated.
   - Implement alerts for critical threats (e.g., compromised credentials, malware detection).

---

## Conclusion
Based on our research, we have selected **Shodan**, **Have I Been Pwned**, **VirusTotal**, **Censys**, and **theHarvester** for integration into our RTTI system. These tools provide comprehensive threat intelligence and are feasible to integrate via their APIs or local execution. Their combined capabilities will enhance the functionality of our web app, enabling real-time threat detection and analysis.

---

## References
- [Shodan API Documentation](https://developer.shodan.io/)
- [Have I Been Pwned API Documentation](https://haveibeenpwned.com/API/v3)
- [VirusTotal API Documentation](https://developers.virustotal.com/reference/overview)
- [Censys API Documentation](https://search.censys.io/api)
- [theHarvester GitHub Repository](https://github.com/laramies/theHarvester)
