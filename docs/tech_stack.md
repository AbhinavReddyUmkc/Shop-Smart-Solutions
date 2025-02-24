# Tech Stack used for building this project
The technological stack selected for ShopSmart Solutions Real-Time Threat Intelligence and Risk Management Framework is described in this document. Real-time threat detection, risk analysis, and security automation are made possible by the chosen technology.

# Technology Stack Selection

Below is the selected technology stack for the **Real-Time Threat Intelligence (RTTI) System**:

| **Component**            | **Selected Technology**       | **Description**                                                                 |
|--------------------------|-------------------------------|---------------------------------------------------------------------------------|
| **Back-End**             | Flask (Python)                | A lightweight and flexible Python web framework for building APIs and handling server-side logic. |
| **Front-End**            | React.js                      | A popular JavaScript library for building dynamic and responsive user interfaces. |
| **Database**             | MongoDB (NoSQL)               | A NoSQL database that stores data in JSON-like documents, ideal for scalable and flexible data storage. |
| **OSINT API**            | Shodan, Have I Been Pwned, VirusTotal | APIs for gathering threat intelligence, including exposed services, breached credentials, and malware analysis. |
| **LLM Model for Risk Scoring** | OpenAI GPT-4 API         | A state-of-the-art language model for analyzing and scoring cybersecurity risks based on threat data. |

---

## Detailed Descriptions

### 1. **Back-End: Flask (Python)**
- Flask is a lightweight and modular Python web framework.
- It is ideal for building RESTful APIs and handling server-side logic.
- Flask’s simplicity and flexibility make it a great choice for rapid development.

### 2. **Front-End: React.js**
- React.js is a JavaScript library for building user interfaces.
- It allows for the creation of reusable UI components and efficient rendering.
- React’s virtual DOM ensures high performance and a smooth user experience.

### 3. **Database: MongoDB (NoSQL)**
- MongoDB is a NoSQL database that stores data in JSON-like documents.
- It is highly scalable and flexible, making it suitable for unstructured or semi-structured data.
- MongoDB’s querying capabilities and horizontal scaling are ideal for real-time applications.

### 4. **OSINT APIs: Shodan, Have I Been Pwned, VirusTotal**
- **Shodan**: Provides data on exposed services and devices connected to the internet.
- **Have I Been Pwned**: Checks if user credentials have been compromised in data breaches.
- **VirusTotal**: Analyzes files and URLs for malware and provides reputation scores.

### 5. **LLM Model for Risk Scoring: OpenAI GPT-4 API**
- OpenAI GPT-4 is a state-of-the-art language model capable of understanding and generating human-like text.
- It will be used to analyze threat data and generate risk scores based on contextual understanding.
- GPT-4’s advanced natural language processing (NLP) capabilities make it ideal for cybersecurity risk assessment.

---

## Why This Stack?
- **Flask** and **React.js** provide a lightweight yet powerful combination for building a responsive and scalable web application.
- **MongoDB** offers flexibility in handling diverse and unstructured threat data.
- The selected **OSINT APIs** provide comprehensive threat intelligence, while **OpenAI GPT-4** adds advanced risk analysis capabilities.
