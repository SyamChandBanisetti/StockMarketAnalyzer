import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetch import get_stock_data
from utils.gemini_api import get_gemini_verdict
from utils.kpi_utils import calculate_kpis, compare_stocks
import math

# --- Streamlit Page Config ---
st.set_page_config(page_title="Stock Market Analyzer", layout="wide")
st.markdown("""
<style>
.big-font {font-size:32px !important; font-weight:bold;}
.section-header {font-size:24px; color: #1F77B4; font-weight:bold; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 Stock Market Analyzer Dashboard</p>', unsafe_allow_html=True)

# --- User Input ---
st.markdown('<p class="section-header">1️⃣ Select Stock</p>', unsafe_allow_html=True)
stock_input = st.text_input("Enter Stock Symbol:", "AAPL")

st.markdown('<p class="section-header">2️⃣ Compare Reputed Stocks</p>', unsafe_allow_html=True)
reputed_stocks = ['AAPL','MSFT','GOOGL','AMZN','TSLA','FB','NVDA','JPM','V','DIS',
                  'MA','PYPL','NFLX','ADBE','INTC','CSCO','CRM','ORCL','NKE','KO',
                  'PFE','MRK','ABBV','PEP','XOM','CVX','WMT','T','UNH','HD']
selected_stocks = st.multiselect("Select Stocks for Comparison:", reputed_stocks, default=['AAPL','MSFT'])

# --- Fetch Main Stock Data ---
main_stock_df = get_stock_data(stock_input)

if main_stock_df is None or main_stock_df.empty:
    st.error("No data available for this stock. Please check the symbol and try again.")
else:
    # --- KPIs ---
    st.markdown('<p class="section-header">3️⃣ Stock KPIs</p>', unsafe_allow_html=True)
    latest, avg, high, low = calculate_kpis(main_stock_df)

    # Ensure values are numeric
    latest = latest if latest is not None and not math.isnan(latest) else 0
    avg = avg if avg is not None and not math.isnan(avg) else 0
    high = high if high is not None and not math.isnan(high) else 0
    low = low if low is not None and not math.isnan(low) else 0

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Latest Price", f"${latest:.2f}")
    kpi2.metric("Average Price (1Y)", f"${avg:.2f}")
    kpi3.metric("1-Year High", f"${high:.2f}")
    kpi4.metric("1-Year Low", f"${low:.2f}")

    # --- Price Chart ---
    st.markdown('<p class="section-header">4️⃣ Price Trend</p>', unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=main_stock_df['Date'], y=main_stock_df['Close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f"{stock_input} Price Trend", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

    # --- Gemini Verdict ---
    st.markdown('<p class="section-header">5️⃣ Buy/Sell/Hold Verdict</p>', unsafe_allow_html=True)
    verdict, confidence = get_gemini_verdict(stock_input, main_stock_df['Close'].tolist())
    color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"
    st.markdown(f"<h3 style='color:{color};'>💡 Verdict: {verdict} (Confidence: {confidence*100:.1f}%)</h3>", unsafe_allow_html=True)

    # --- Comparison with Selected Stocks ---
    st.markdown('<p class="section-header">6️⃣ Stock Comparison</p>', unsafe_allow_html=True)
    comparison_data = {}
    for symbol in selected_stocks:
        df = get_stock_data(symbol)
        if df is not None and not df.empty:
            comparison_data[symbol] = df['Close'].iloc[-1]

    if comparison_data:
        comp_df = pd.DataFrame(list(comparison_data.items()), columns=['Stock','Latest Close'])
        st.table(comp_df.sort_values(by='Latest Close', ascending=False))
    else:
        st.info("No data available for selected comparison stocks.")

    # --- Top Better Stocks Suggestion ---
    st.markdown('<p class="section-header">7️⃣ Top Performing Stocks</p>', unsafe_allow_html=True)
    if comparison_data:
        better_stocks = compare_stocks(comparison_data, latest)
        if better_stocks:
            st.success(f"Stocks performing better than {stock_input}: {', '.join(better_stocks)}")
        else:
            st.info(f"No selected stocks are outperforming {stock_input}.")
