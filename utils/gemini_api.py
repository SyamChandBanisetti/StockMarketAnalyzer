import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://api.gemini.ai/predict_stock"  # Replace with real URL

def get_gemini_verdict(symbol, historical_prices):
    payload = {
        "stock": symbol,
        "historical_prices": historical_prices,
        "analysis_period": "1y"
    }
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}"}
    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=payload)
        data = response.json()
        verdict = data.get("verdict", "HOLD")
        confidence = data.get("confidence", 0.5)
        return verdict, confidence
    except Exception as e:
        print("Gemini API failed, fallback logic used:", e)
        last_price = historical_prices[-1]
        mean_price = sum(historical_prices)/len(historical_prices)
        if last_price < mean_price*0.95: verdict = "BUY"
        elif last_price > mean_price*1.05: verdict = "SELL"
        else: verdict = "HOLD"
        confidence = 0.5
        return verdict, confidence
