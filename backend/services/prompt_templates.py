"""
Templates for prompts sent to the LLM for risk analysis
"""

RISK_ANALYSIS_TEMPLATE = """<s>[INST] 
I need you to analyze the risk level for an IT asset that might be vulnerable to a specific threat.

ASSET DETAILS:
Asset Name: {asset_name}
Type: {asset_type}
Department: {asset_department}
Location: {asset_location}
Manufacturer: {asset_manufacturer}
Model: {asset_model}
Operating System: {asset_os} {asset_os_version}
Software: {asset_software}
Criticality: {asset_criticality}
Data Classification: {asset_data_classification}

THREAT DETAILS:
CVE ID: {threat_cve_id}
Name: {threat_name}
Description: {threat_description}
CVSS Score: {threat_cvss_score}
CVSS Severity: {threat_cvss_severity}
CVSS Vector: {threat_cvss_vector}

Based on the asset details and threat information, please:
1. Analyze the risk level and provide a risk score from 1-10 (10 being the highest risk)
2. Provide a brief analysis of the potential impact (100 words max)
3. Recommend mitigation steps
4. Provide a one-word risk level (Critical, High, Medium, or Low)

Format your response as a JSON object with the following fields:
- risk_score (number between 1-10)
- analysis (string)
- mitigation (string)
- risk_level (string: Critical, High, Medium, or Low)
[/INST]</s>
"""

THREAT_SUMMARY_TEMPLATE = """<s>[INST] 
Summarize the following vulnerability details in a clear, concise way that explains the real-world impact and risk:

VULNERABILITY DETAILS:
CVE ID: {cve_id}
Name: {name}
Description: {description}
CVSS Score: {cvss_score}
CVSS Severity: {cvss_severity}
CVSS Vector: {cvss_vector}

Provide a 2-3 sentence summary of:
1. What the vulnerability is
2. How it could be exploited
3. What the potential impact would be

Format your response as a plain text paragraph without any special formatting.
[/INST]</s>
"""

MITIGATION_RECOMMENDATION_TEMPLATE = """<s>[INST] 
Based on the following vulnerability, provide specific mitigation recommendations:

VULNERABILITY DETAILS:
CVE ID: {cve_id}
Name: {name}
Description: {description}
CVSS Score: {cvss_score}
CVSS Severity: {cvss_severity}
CVSS Vector: {cvss_vector}

Provide 3-5 specific mitigation steps that would help address this vulnerability.
Format your response as a bulleted list (use - for bullets) with clear, actionable steps.
[/INST]</s>
"""