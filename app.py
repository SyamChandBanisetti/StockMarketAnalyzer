import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetch import get_stock_data
from utils.gemini_api import get_gemini_verdict
from utils.kpi_utils import calculate_kpis, compare_stocks
import math

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Stock Analyzer", layout="wide")
st.markdown("""
<style>
.big-font {font-size:32px !important; font-weight:bold;}
.section-header {font-size:24px; color: #1F77B4; font-weight:bold; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 Stock Market Analyzer Dashboard</p>', unsafe_allow_html=True)

# --- 1️⃣ Stock Input ---
st.markdown('<p class="section-header">1️⃣ Enter Stock Symbol</p>', unsafe_allow_html=True)
stock_input = st.text_input("Stock Symbol (e.g., AAPL, MSFT):", "AAPL")

# --- 2️⃣ Compare Stocks ---
st.markdown('<p class="section-header">2️⃣ Compare with Reputed Stocks</p>', unsafe_allow_html=True)
reputed_stocks = ['AAPL','MSFT','GOOGL','AMZN','TSLA','FB','NVDA','JPM','V','DIS',
                  'MA','PYPL','NFLX','ADBE','INTC','CSCO','CRM','ORCL','NKE','KO',
                  'PFE','MRK','ABBV','PEP','XOM','CVX','WMT','T','UNH','HD']
selected_stocks = st.multiselect("Select comparison stocks:", reputed_stocks, default=['AAPL','MSFT'])

# --- Fetch Main Stock Data ---
main_stock_df = get_stock_data(stock_input)

if main_stock_df is None or main_stock_df.empty or 'Close' not in main_stock_df.columns:
    st.error("No valid stock data found. Check the symbol.")
else:
    # --- 3️⃣ KPIs ---
    st.markdown('<p class="section-header">3️⃣ Stock KPIs</p>', unsafe_allow_html=True)

    def safe_number(val):
        try:
            num = float(val)
            if math.isnan(num):
                return 0.0
            return num
        except:
            return 0.0

    latest, avg, high, low = calculate_kpis(main_stock_df)
    latest = safe_number(latest)
    avg = safe_number(avg)
    high = safe_number(high)
    low = safe_number(low)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Latest Price", f"${latest:.2f}")
    kpi2.metric("Average Price (1Y)", f"${avg:.2f}")
    kpi3.metric("1-Year High", f"${high:.2f}")
    kpi4.metric("1-Year Low", f"${low:.2f}")

    # --- 4️⃣ Price Trend ---
    st.markdown('<p class="section-header">4️⃣ Price Trend</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=main_stock_df['Date'], y=main_stock_df['Close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f"{stock_input} Price Trend (1Y)", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

    # --- 5️⃣ Gemini Verdict ---
    st.markdown('<p class="section-header">5️⃣ Buy/Sell/Hold Verdict</p>', unsafe_allow_html=True)
    verdict, confidence = get_gemini_verdict(stock_input, main_stock_df['Close'].tolist())
    color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"
    st.markdown(f"<h3 style='color:{color};'>💡 Verdict: {verdict} (Confidence: {confidence*100:.1f}%)</h3>", unsafe_allow_html=True)

    # --- 6️⃣ Comparison Table ---
    st.markdown('<p class="section-header">6️⃣ Comparison with Selected Stocks</p>', unsafe_allow_html=True)
    comparison_data = {}
    for symbol in selected_stocks:
        df = get_stock_data(symbol)
        if df is not None and not df.empty and 'Close' in df.columns:
            comparison_data[symbol] = safe_number(df['Close'].iloc[-1])

    if comparison_data:
        comp_df = pd.DataFrame(list(comparison_data.items()), columns=['Stock','Latest Close'])
        st.table(comp_df.sort_values(by='Latest Close', ascending=False))
    else:
        st.info("No data available for selected comparison stocks.")

    # --- 7️⃣ Top Performing Stocks ---
    st.markdown('<p class="section-header">7️⃣ Top Performing Stocks</p>', unsafe_allow_html=True)
    if comparison_data:
        better_stocks = compare_stocks(comparison_data, latest)
        if better_stocks:
            st.success(f"Stocks outperforming {stock_input}: {', '.join(better_stocks)}")
        else:
            st.info(f"No selected stocks outperform {stock_input}.")
