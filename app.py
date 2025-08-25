# app.py

import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json # Import json for constructing the payload

# --- Placeholder for API_KEY ---
# IMPORTANT: For local development, set this as an environment variable (e.g., in a .env file)
# or replace "" with your actual API key for the AI service you are using.
# For Canvas/Streamlit Cloud, ensure your environment variables are correctly configured.
AI_SERVICE_API_KEY = "" # Leave empty for Canvas's auto-injection or put your key here for local testing

# --- Mock get_ai_verdict function ---
# This is a placeholder as the original utils/gemini_api.py was not provided.
# If you have your actual implementation for an AI-powered verdict, replace this mock with it.
def get_ai_verdict(stock_symbol: str, close_prices: list):
    """
    Mocks a function that interacts with an AI model
    to analyze stock prices and provide a verdict.
    """
    if not close_prices:
        return "HOLD", 0.5

    latest_price = close_prices[-1]
    average_price = sum(close_prices) / len(close_prices)

    # Simple mock logic based on last price vs. average
    if latest_price > average_price * 1.05: # More than 5% above average
        verdict = "SELL"
        confidence = 0.8
    elif latest_price < average_price * 0.95: # More than 5% below average
        verdict = "BUY"
        confidence = 0.7
    else:
        verdict = "HOLD"
        confidence = 0.6
    return verdict, confidence


# --- Streamlit Setup ---
st.set_page_config(page_title="Stock Analyzer", layout="centered")
st.markdown("""
<style>
.big-font {font-size:32px !important; font-weight:bold;}
.section-header {font-size:20px; color: #1F77B4; font-weight:bold; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 Stock Analyzer Dashboard</p>', unsafe_allow_html=True)

# --- 1️⃣ Stock Input via Selectbox ---
st.markdown('<p class="section-header">Select Stock Symbol</p>', unsafe_allow_html=True)
reputed_stocks = [
    'AAPL','MSFT','GOOGL','AMZN','TSLA','FB','NVDA','JPM','V','DIS',
    'MA','PYPL','NFLX','ADBE','INTC','CSCO','CRM','ORCL','NKE','KO',
    'PFE','MRK','ABBV','PEP','XOM','CVX','WMT','T','UNH','HD'
]
stock_input = st.selectbox("Choose Stock:", reputed_stocks, index=4)  # default TSLA (index 4)

if stock_input:
    # Fetch last 1 year stock data
    try:
        df = yf.download(stock_input, period="1y", progress=False) # progress=False to suppress yfinance output
        df.reset_index(inplace=True)

        if df.empty or 'Close' not in df.columns:
            st.error("No data found for this symbol or 'Close' column is missing.")
        else:
            # --- KPIs & Insights ---
            latest = int(round(df['Close'].iloc[-1]))
            avg_price = int(round(df['Close'].mean()))
            high_price = int(round(df['Close'].max()))
            low_price = int(round(df['Close'].min()))

            st.markdown('<p class="section-header">Stock KPIs & Insights</p>', unsafe_allow_html=True)
            st.write(f"- **Latest Price:** ${latest}")
            st.write(f"- **1-Year High:** ${high_price}")
            st.write(f"- **1-Year Low:** ${low_price}")
            st.write(f"- **Average Price (1Y):** ${avg_price}")

            # Simple trend insight
            if latest > avg_price:
                trend = "The stock is trending **above its 1-year average**."
            else:
                trend = "The stock is trending **below its 1-year average**."
            st.write(f"- **Trend Insight:** {trend}")

            # --- Final Verdict & Suggestions ---
            st.markdown('<p class="section-header">💡 Recommendation & Insights</p>', unsafe_allow_html=True)

            # Convert Close prices to Python float list
            close_prices_list = df['Close'].astype(float).tolist()

            # Get verdict + textual suggestion (API call) using the mock function
            verdict, confidence = get_ai_verdict(stock_input, close_prices_list)

            # Map verdict to color
            color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"

            # Display main verdict
            st.markdown(f"<h3 style='color:{color};'>Recommendation: {verdict} (Confidence: {int(confidence*100)}%)</h3>", unsafe_allow_html=True)

            # --- Generate textual suggestions from analytics model ---
            try:
                # Using the recommended API structure for Python
                # API key is passed as a query parameter if available
                api_key_param = f"key={AI_SERVICE_API_KEY}" if AI_SERVICE_API_KEY else ""
                # Note: The model name `gemini-2.5-flash-preview-05-20` is part of the URL,
                # but we are using a generic API_SERVICE_API_KEY variable and avoiding
                # mentioning "Gemini" in the UI-facing text.
                AI_SERVICE_API_URL = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent)?{api_key_param}"


                prompt_text = f"Analyze the stock {stock_input} based on its last 1 year prices and provide a short actionable insight. Focus on future outlook based on recent trends."
                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt_text}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 150
                    }
                }
                headers = {
                    "Content-Type": "application/json"
                }

                with st.spinner("Fetching analytics insights..."):
                    response = requests.post(AI_SERVICE_API_URL, headers=headers, data=json.dumps(payload))
                    response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
                    result = response.json()

                insight_text = ""
                # Correct parsing for generateContent API response
                if result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                    insight_text = result["candidates"][0]["content"]["parts"][0].get("text", "")

                if insight_text:
                    st.write(f"**Insight:** {insight_text.strip()}")
                else:
                    st.info("No additional insights available from the analytics model.")
            except requests.exceptions.RequestException as req_e:
                st.error(f"Error communicating with the analytics model: {req_e}. Please ensure your API key is correctly configured and check your network connection.")
            except Exception as e:
                st.info(f"An unexpected error occurred while fetching analytics insights: {e}")

    except Exception as e:
        st.error(f"Error fetching stock data: {e}. Please ensure the stock symbol is valid and try again.")
        # For debugging, you can uncomment the line below to see the full traceback in Streamlit
        # st.exception(e)
