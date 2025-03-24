# /src/risk_analysis.py

import openai
from transformers import pipeline

# Configuration for GPT-4
OPENAI_API_KEY = "your_openai_api_key_here"
openai.api_key = OPENAI_API_KEY

# Configuration for Hugging Face (optional)
HUGGINGFACE_MODEL = "distilbert-base-uncased"  # Replace with your preferred model

def analyze_risk_gpt4(threat, likelihood, impact):
    """
    Analyzes the risk score using GPT-4.
    
    Args:
        threat (str): The detected threat (e.g., "SQL Injection").
        likelihood (int): Likelihood of the threat (scale of 1-5).
        impact (int): Impact of the threat (scale of 1-5).
    
    Returns:
        str: AI-generated risk analysis and score.
    """
    prompt = f"Analyze the risk score for {threat} with likelihood {likelihood} and impact {impact}. Provide a detailed risk assessment and a final risk score (scale of 1-10)."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "system", "content": prompt}]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        return f"Error analyzing risk with GPT-4: {e}"

def analyze_risk_huggingface(threat, likelihood, impact):
    """
    Analyzes the risk score using Hugging Face LLM.
    
    Args:
        threat (str): The detected threat (e.g., "SQL Injection").
        likelihood (int): Likelihood of the threat (scale of 1-5).
        impact (int): Impact of the threat (scale of 1-5).
    
    Returns:
        str: AI-generated risk analysis and score.
    """
    prompt = f"Analyze the risk score for {threat} with likelihood {likelihood} and impact {impact}. Provide a detailed risk assessment and a final risk score (scale of 1-10)."
    
    try:
        generator = pipeline("text-generation", model=HUGGINGFACE_MODEL)
        response = generator(prompt, max_length=100, num_return_sequences=1)
        return response[0]["generated_text"]
    except Exception as e:
        return f"Error analyzing risk with Hugging Face: {e}"

# Example usage
if __name__ == "__main__":
    # Analyze risk using GPT-4
    risk_score_gpt4 = analyze_risk_gpt4("SQL Injection", 4, 5)
    print(f"GPT-4 Risk Analysis:\n{risk_score_gpt4}\n")
    
    # Analyze risk using Hugging Face
    risk_score_hf = analyze_risk_huggingface("Phishing", 3, 4)
    print(f"Hugging Face Risk Analysis:\n{risk_score_hf}\n")