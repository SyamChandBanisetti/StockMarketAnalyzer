import os
import requests
from dotenv import load_dotenv
import json

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_gemini_verdict(company_name: str):
    """
    Returns: (verdict: str, confidence: float, insights: str)
    """
    # Construct prompt
    prompt_text = (
        f"Analyze the company '{company_name}' and provide:\n"
        "- A simple stock recommendation: BUY, SELL, or HOLD\n"
        "- A confidence level (0-1)\n"
        "- A short actionable insight for investors\n"
        "Return in JSON format: {'verdict':'', 'confidence':0.0, 'insights':''}"
    )

    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }

    response = requests.post(GEMINI_API_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()

    try:
        # Extract generated text
        text_output = result["candidates"][0]["content"][0]["text"]

        # Parse JSON returned from LLM
        parsed = json.loads(text_output)
        verdict = parsed.get("verdict", "HOLD")
        confidence = float(parsed.get("confidence", 0.7))
        insights = parsed.get("insights", "")
        return verdict.upper(), confidence, insights
    except Exception:
        # Fallback if parsing fails
        return "HOLD", 0.7, "No insights available at this time."
