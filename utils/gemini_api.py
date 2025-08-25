import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_gemini_verdict(symbol, historical_prices):
    """Call Gemini API to get Buy/Sell/Hold verdict; fallback if API fails."""
    prompt_text = (
        f"Analyze the following stock prices for {symbol} over 1 year and give a Buy, Sell, or Hold verdict "
        f"with confidence score. Prices: {historical_prices[-30:]}"  # last 30 days as summary
    )

    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "prompt": {"text": prompt_text},
        "temperature": 0.2,
        "maxOutputTokens": 150
    }

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        result = response.json()
        # Extract verdict and confidence from Gemini response safely
        text_output = result.get("candidates", [{}])[0].get("output", {}).get("content", [{}])[0].get("text", "")
        verdict = "HOLD"
        confidence = 0.5
        if "buy" in text_output.lower():
            verdict = "BUY"
        elif "sell" in text_output.lower():
            verdict = "SELL"
        # Optional: extract confidence if provided, else 0.5
        return verdict, confidence
    except Exception as e:
        print("Gemini API failed, using fallback logic:", e)
        # Fallback: simple mean-based logic
        last_price = historical_prices[-1]
        mean_price = sum(historical_prices)/len(historical_prices)
        if last_price < mean_price*0.95: verdict = "BUY"
        elif last_price > mean_price*1.05: verdict = "SELL"
        else: verdict = "HOLD"
        confidence = 0.5
        return verdict, confidence
