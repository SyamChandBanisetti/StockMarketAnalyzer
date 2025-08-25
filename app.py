import streamlit as st
import pandas as pd
import yfinance as yf
from utils.gemini_api import get_gemini_verdict

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
stock_input = st.selectbox("Choose Stock:", reputed_stocks, index=1)  # default MSFT

if stock_input:
    # Fetch last 1 year stock data
    try:
        df = yf.download(stock_input, period="1y")
        df.reset_index(inplace=True)
        if df.empty or 'Close' not in df.columns:
            st.error("No data found for this symbol.")
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

            # Get verdict + textual suggestion (API call)
            verdict, confidence = get_gemini_verdict(stock_input, close_prices_list)

            # Map verdict to color
            color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"

            # Display main verdict
            st.markdown(f"<h3 style='color:{color};'>Recommendation: {verdict} (Confidence: {int(confidence*100)}%)</h3>", unsafe_allow_html=True)

            # --- Generate textual suggestions from API (without mentioning Gemini) ---
            try:
                # Here we can reuse the same API to get text insight
                # For simplicity, the function returns a tuple (verdict, insight)
                # We'll just display insight text
                import requests, os
                from dotenv import load_dotenv
                load_dotenv()
                GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
                GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

                prompt_text = f"Analyze the stock {stock_input} for last 1 year prices and provide a short actionable insight, without mentioning the source."
                headers = {
                    "Authorization": f"Bearer {GEMINI_API_KEY}",
                    "Content-Type": "application/json"
                }
                data = {
                    "prompt": {"text": prompt_text},
                    "temperature": 0.3,
                    "maxOutputTokens": 150
                }
                response = requests.post(GEMINI_API_URL, headers=headers, json=data)
                result = response.json()
                insight_text = result.get("candidates", [{}])[0].get("output", {}).get("content", [{}])[0].get("text", "")
                if insight_text:
                    st.write(f"**Insight:** {insight_text.strip()}")
                else:
                    st.info("No additional insights available.")
            except Exception as e:
                st.info("Unable to fetch additional insights at this time.")

    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
