import os
import requests
from dotenv import load_dotenv
import pandas as pd

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

def get_stock_data_gemini(symbol):
    """
    Get last 1-year stock data (Open, High, Low, Close) from Gemini API.
    Returns a DataFrame with columns: Date, Open, High, Low, Close
    """
    prompt = f"""
    Provide daily stock data for the symbol {symbol} for the last 1 year in CSV format
    with columns: Date, Open, High, Low, Close. Only provide raw CSV data without explanation.
    """
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": {"text": prompt}, "temperature": 0, "maxOutputTokens": 2000}

    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=data)
        resp_json = resp.json()
        csv_text = resp_json.get("candidates", [{}])[0].get("output", {}).get("content", [{}])[0].get("text", "")
        # Convert CSV text to DataFrame
        from io import StringIO
        df = pd.read_csv(StringIO(csv_text))
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        print(f"Gemini API error for {symbol}: {e}")
        return None

def get_gemini_verdict(symbol, historical_prices):
    """
    Get Buy/Sell/Hold verdict from Gemini API
    """
    prompt_text = f"""
    Analyze the following 1-year daily closing prices of {symbol} and give a Buy, Sell, or Hold verdict.
    Return as JSON: {{"verdict": "BUY/SELL/HOLD", "confidence": 0-1}}.
    Prices: {historical_prices[-30:]}
    """
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": {"text": prompt_text}, "temperature": 0.2, "maxOutputTokens": 150}

    try:
        response = requests.post(GEMINI_API_URL, headers=headers, json=data)
        result = response.json()
        text_output = result.get("candidates", [{}])[0].get("output", {}).get("content", [{}])[0].get("text", "")
        import json
        verdict_data = json.loads(text_output)
        return verdict_data.get("verdict","HOLD"), float(verdict_data.get("confidence",0.5))
    except:
        # fallback
        last = historical_prices[-1]
        mean = sum(historical_prices)/len(historical_prices)
        verdict = "BUY" if last < mean*0.95 else "SELL" if last > mean*1.05 else "HOLD"
        return verdict, 0.5
