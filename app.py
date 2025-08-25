# app.py

import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import json
import time
import os # Import os for environment variables

# --- Placeholder for AI_SERVICE_API_KEY ---
# IMPORTANT: For local development, set this as an environment variable (e.g., in a .env file)
# or replace "" with your actual API key for the AI service you are using.
# For Canvas/Streamlit Cloud, ensure your environment variables are correctly configured.
AI_SERVICE_API_KEY = os.getenv("AI_SERVICE_API_KEY", "") # Load from environment or use empty string

# --- AI Service URL (generic reference) ---
# This URL points to a generative AI model endpoint.
# The model name 'gemini-2.5-flash-preview-05-20' is part of the URL,
# but we are using a generic API_SERVICE_API_KEY variable and avoiding
# mentioning "Gemini" in the UI-facing text.
AI_SERVICE_API_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- Exponential Backoff for API Calls ---
def call_api_with_backoff(url, headers, payload, max_retries=5, initial_delay=1):
    """
    Calls an API with exponential backoff.
    """
    for i in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.RequestException as e:
            if i < max_retries - 1:
                delay = initial_delay * (2 ** i)
                st.warning(f"API call failed ({e}). Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise # Re-raise the last exception if max retries reached
    return None

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
            st.error(f"No data found for symbol '{stock_input}'. Please ensure it is a valid stock ticker.")
            st.stop()
        else:
            # --- CRITICAL FIX: Explicitly convert 'Close' column to numeric, coercing errors to NaN ---
            df['Close'] = pd.to_numeric(df['Close'], errors='coerce')

            # --- CRITICAL FIX: Check if the 'Close' Series is empty or all NaN after coercion ---
            if df['Close'].empty or df['Close'].isnull().all():
                st.error(f"Error: No valid numerical 'Close' price data found for '{stock_input}' after processing. Cannot proceed with analysis. Please try a different symbol or check the market hours.")
                st.stop()
            
            # --- KPIs & Insights ---
            # All these operations should now be safe as df['Close'] is guaranteed to be a non-empty, numeric Series
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

            # --- Final Verdict & Suggestions from Analytics Model ---
            st.markdown('<p class="section-header">💡 Recommendation & Insights</p>', unsafe_allow_html=True)

            try:
                # Prepare AI service API URL with key
                api_key_param = f"key={AI_SERVICE_API_KEY}" if AI_SERVICE_API_KEY else ""
                ai_api_url = f"{AI_SERVICE_API_BASE_URL}?{api_key_param}"

                # Construct the prompt using summary statistics
                prompt_text = (
                    f"Analyze the stock {stock_input} based on the following 1-year data: "
                    f"Latest Price: ${latest}, 1-Year High: ${high_price}, 1-Year Low: ${low_price}, "
                    f"Average Price (1Y): ${avg_price}. "
                    f"Provide a stock recommendation (BUY, SELL, or HOLD) and a concise, actionable insight "
                    f"focusing on future outlook based on these key statistics and recent trends. "
                    f"Respond only in JSON format with two keys: 'verdict' (string) and 'insight' (string)."
                )

                payload = {
                    "contents": [
                        {
                            "role": "user",
                            "parts": [{"text": prompt_text}]
                        }
                    ],
                    "generationConfig": {
                        "temperature": 0.3,
                        "maxOutputTokens": 200, # Increased token limit for both verdict and insight
                        "responseMimeType": "application/json",
                        "responseSchema": {
                            "type": "OBJECT",
                            "properties": {
                                "verdict": {"type": "STRING", "enum": ["BUY", "SELL", "HOLD"]},
                                "insight": {"type": "STRING"}
                            },
                            "required": ["verdict", "insight"]
                        }
                    }
                }
                headers = {
                    "Content-Type": "application/json"
                }

                verdict = "HOLD" # Default verdict
                confidence = 0.5 # Default confidence
                insight_text = "No additional insights available from the analytics model."

                with st.spinner("Fetching analytics insights..."):
                    result = call_api_with_backoff(ai_api_url, headers, payload)

                if result and result.get("candidates") and result["candidates"][0].get("content") and result["candidates"][0]["content"].get("parts"):
                    raw_json_text = result["candidates"][0]["content"]["parts"][0].get("text", "{}")
                    try:
                        parsed_response = json.loads(raw_json_text)
                        verdict = parsed_response.get("verdict", "HOLD")
                        insight_text = parsed_response.get("insight", "No additional insights available from the analytics model.")
                        # Mock confidence based on verdict for display, as actual confidence isn't directly returned by the model in this schema
                        if verdict == "BUY":
                            confidence = 0.8
                        elif verdict == "SELL":
                            confidence = 0.8
                        else:
                            confidence = 0.6
                    except json.JSONDecodeError as json_e:
                        st.error(f"Error parsing response from analytics model: {json_e}. Received unexpected format: {raw_json_text[:500]}...")
                else:
                    st.info("No structured insights available from the analytics model, or response was empty.")

                # Map verdict to color
                color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"

                # Display main verdict
                st.markdown(f"<h3 style='color:{color};'>Recommendation: {verdict} (Confidence: {int(confidence*100)}%)</h3>", unsafe_allow_html=True)
                st.write(f"**Insight:** {insight_text.strip()}")

            except requests.exceptions.RequestException as req_e:
                st.error(f"Error communicating with the analytics model: {req_e}. Please ensure your API key is correctly configured and check your network connection.")
            except Exception as e:
                st.info(f"An unexpected error occurred while fetching analytics insights: {e}")
                # For more detailed debugging, uncomment the next line to show the full traceback in Streamlit
                # st.exception(e)

    except Exception as e:
        st.error(f"Error fetching stock data: {e}. Please ensure the stock symbol is a valid ticker (e.g., 'AAPL', 'MSFT', 'TSLA') and try again. Sometimes data may not be available during off-market hours or for less common symbols.")
        # For more detailed debugging, uncomment the next line to show the full traceback in Streamlit
        # st.exception(e)
