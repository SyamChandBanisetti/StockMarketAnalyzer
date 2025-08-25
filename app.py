import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv
import os
from io import StringIO
import json

# --- Load Gemini API key ---
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.markdown("""
<style>
.big-font {font-size:32px !important; font-weight:bold;}
.section-header {font-size:24px; color: #1F77B4; font-weight:bold; margin-top:20px;}
.verdict {font-size:36px; font-weight:bold; margin-top:20px;}
.insights {font-size:20px; margin-top:10px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 Stock Market Analyzer Dashboard</p>', unsafe_allow_html=True)

# --- 1️⃣ Stock Input ---
st.markdown('<p class="section-header">1️⃣ Enter Stock Symbol</p>', unsafe_allow_html=True)
stock_input = st.text_input("Stock Symbol (e.g., AAPL, MSFT):", "AAPL")

# --- Helper Functions ---
def get_stock_data_gemini(symbol):
    prompt = f"""
    Provide daily stock data for the symbol {symbol} for the last 1 year in CSV format
    with columns: Date, Open, High, Low, Close. Only return CSV, no explanations.
    """
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": {"text": prompt}, "temperature": 0, "maxOutputTokens": 2000}
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=data)
        resp_json = resp.json()
        csv_text = resp_json.get("candidates", [{}])[0].get("output", {}).get("content", [{}])[0].get("text", "")
        df = pd.read_csv(StringIO(csv_text))
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        return df
    except:
        return None

def calculate_kpis(df):
    latest = df['Close'].iloc[-1]
    avg = df['Close'].mean()
    high = df['Close'].max()
    low = df['Close'].min()
    return int(round(latest)), int(round(avg)), int(round(high)), int(round(low))

def get_gemini_verdict(symbol, historical_prices):
    prompt_text = f"""
    Analyze the last 1-year daily closing prices of {symbol} and provide:
    1. Verdict: Buy, Sell, or Hold
    2. Confidence (0-1)
    3. Insights and recommendations in clear sentences
    Return JSON: {{"verdict": "BUY/SELL/HOLD", "confidence": 0-1, "insights": "text"}}
    Prices (last 30 days): {historical_prices[-30:]}
    """
    headers = {"Authorization": f"Bearer {GEMINI_API_KEY}", "Content-Type": "application/json"}
    data = {"prompt": {"text": prompt_text}, "temperature": 0.2, "maxOutputTokens": 300}
    try:
        resp = requests.post(GEMINI_API_URL, headers=headers, json=data)
        resp_json = resp.json()
        text_output = resp_json.get("candidates", [{}])[0].get("output", {}).get("content", [{}])[0].get("text", "{}")
        parsed = json.loads(text_output)
        verdict = parsed.get("verdict", "HOLD")
        confidence = float(parsed.get("confidence", 0.5))
        insights = parsed.get("insights", "No insights available.")
        return verdict, confidence, insights
    except:
        last = historical_prices[-1]
        mean = sum(historical_prices)/len(historical_prices)
        verdict = "BUY" if last < mean*0.95 else "SELL" if last > mean*1.05 else "HOLD"
        confidence = 0.5
        insights = "Unable to fetch detailed insights."
        return verdict, confidence, insights

# --- Fetch Stock Data ---
stock_df = get_stock_data_gemini(stock_input)

if stock_df is None or stock_df.empty:
    st.error("No valid stock data found for this symbol.")
else:
    # --- 2️⃣ KPIs ---
    st.markdown('<p class="section-header">2️⃣ Stock KPIs (Last 1 Year)</p>', unsafe_allow_html=True)
    latest, avg, high, low = calculate_kpis(stock_df)
    
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Latest Price", f"${latest}")
    k2.metric("Average Price (1Y)", f"${avg}")
    k3.metric("1-Year High", f"${high}")
    k4.metric("1-Year Low", f"${low}")

    # --- 3️⃣ Price Trend ---
    st.markdown('<p class="section-header">3️⃣ Price Trend & 20-Day Moving Average</p>', unsafe_allow_html=True)
    stock_df['MA20'] = stock_df['Close'].rolling(20).mean()
    
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=stock_df['Date'],
        open=stock_df['Open'],
        high=stock_df['High'],
        low=stock_df['Low'],
        close=stock_df['Close'],
        name='Candlestick'
    ))
    fig.add_trace(go.Scatter(
        x=stock_df['Date'],
        y=stock_df['MA20'],
        mode='lines',
        line=dict(color='blue', width=2),
        name='20-Day MA'
    ))
    fig.update_layout(
        title=f"{stock_input} Candlestick & 20-Day MA (1Y)",
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        xaxis_rangeslider_visible=False
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- 4️⃣ Final Verdict & Insights ---
    st.markdown('<p class="section-header">4️⃣ Verdict & Insights</p>', unsafe_allow_html=True)
    verdict, confidence, insights = get_gemini_verdict(stock_input, stock_df['Close'].tolist())
    
    color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"
    st.markdown(f"<p class='verdict' style='color:{color};'>💡 {verdict} (Confidence: {int(confidence*100)}%)</p>", unsafe_allow_html=True)
    st.markdown(f"<p class='insights'>{insights}</p>", unsafe_allow_html=True)
