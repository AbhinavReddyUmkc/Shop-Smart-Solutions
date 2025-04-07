import openai
import json
import time

time.sleep(2)  # Wait 2 seconds between API calls

# Replace with your OpenAI API Key
OPENAI_API_KEY = "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"
openai.api_key = OPENAI_API_KEY


def analyze_risk(shodan_data, virustotal_data, leaklookup_data):
    #  Truncate inputs to 1500 characters each to prevent long prompts
    shodan_data_str = json.dumps(shodan_data)[:1500]  # Limit to 1500 characters
    virustotal_data_str = json.dumps(virustotal_data)[:1500]
    leaklookup_data_str = json.dumps(leaklookup_data)[:1500]

    prompt = f"""
    Given the following cyber threat intelligence data, analyze the risk level:

    Shodan Data: {shodan_data_str}
    VirusTotal Data: {virustotal_data_str}
    LeakLookup Data: {leaklookup_data_str}

    Assign a risk score from 0 (low risk) to 100 (high risk).
    Provide a brief explanation in 2-3 sentences.

    Respond strictly in valid JSON format like this:
    {{
      "risk_score": <integer>,
      "explanation": "<reasoning>"
    }}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a cybersecurity expert providing risk analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300,
            temperature=0.5
        )

        raw_response = response["choices"][0]["message"]["content"].strip()
        print(f"DEBUG: Raw GPT-4 Response: {raw_response}")

        if not raw_response.endswith("}"):
            raw_response += "}"  # Attempt to fix truncated JSON

        risk_analysis = json.loads(raw_response)
        
        if "risk_score" not in risk_analysis or "explanation" not in risk_analysis:
            raise ValueError("Missing 'risk_score' or 'explanation' in response")
            
        return risk_analysis

    except Exception as e:
        print(f"Error: {e}")
        return {"error": str(e)}
