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

# --- 1️⃣ Stock Input ---
st.markdown('<p class="section-header">Enter Stock Symbol</p>', unsafe_allow_html=True)
stock_input = st.text_input("Stock Symbol (e.g., AAPL, MSFT):", "AAPL")

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

            # --- Final Verdict ---
            st.markdown('<p class="section-header">💡 Final Verdict</p>', unsafe_allow_html=True)
            verdict, confidence = get_gemini_verdict(stock_input, df['Close'].tolist())
            color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"
            st.markdown(f"<h3 style='color:{color};'>Verdict: {verdict} (Confidence: {int(confidence*100)}%)</h3>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error fetching stock data: {e}")
