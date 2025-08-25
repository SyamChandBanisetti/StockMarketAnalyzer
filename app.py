import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.gemini_api import get_stock_data_gemini, get_gemini_verdict
from utils.kpi_utils import calculate_kpis, compare_stocks

# --- Page Setup ---
st.set_page_config(page_title="Stock Analyzer (Gemini)", layout="wide")
st.markdown("""
<style>
.big-font {font-size:32px !important; font-weight:bold;}
.section-header {font-size:24px; color: #1F77B4; font-weight:bold; margin-top:20px;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-font">📊 Stock Analyzer Dashboard (Gemini)</p>', unsafe_allow_html=True)

# --- 1️⃣ Stock Input ---
st.markdown('<p class="section-header">1️⃣ Enter Stock Symbol</p>', unsafe_allow_html=True)
stock_input = st.text_input("Stock Symbol (e.g., AAPL, MSFT):", "AAPL")

# --- 2️⃣ Compare Stocks ---
st.markdown('<p class="section-header">2️⃣ Compare with Reputed Stocks</p>', unsafe_allow_html=True)
reputed_stocks = ['AAPL','MSFT','GOOGL','AMZN','TSLA','FB','NVDA','JPM','V','DIS',
                  'MA','PYPL','NFLX','ADBE','INTC','CSCO','CRM','ORCL','NKE','KO',
                  'PFE','MRK','ABBV','PEP','XOM','CVX','WMT','T','UNH','HD']
selected_stocks = st.multiselect("Select comparison stocks:", reputed_stocks, default=['AAPL','MSFT'])

# --- Fetch Main Stock Data from Gemini ---
main_stock_df = get_stock_data_gemini(stock_input)

if main_stock_df is None or main_stock_df.empty:
    st.error("No valid stock data found for this symbol via Gemini API.")
else:
    # --- KPIs ---
    latest, avg, high, low = calculate_kpis(main_stock_df)
    latest, avg, high, low = map(lambda x: int(round(x)), [latest, avg, high, low])
    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Latest Price", f"${latest}")
    k2.metric("Average Price (1Y)", f"${avg}")
    k3.metric("1-Year High", f"${high}")
    k4.metric("1-Year Low", f"${low}")

    # --- Price Trend (Candlestick + MA) ---
    st.markdown('<p class="section-header">4️⃣ Price Trend & 20-Day MA</p>', unsafe_allow_html=True)
    main_stock_df['MA20'] = main_stock_df['Close'].rolling(20).mean()

    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=main_stock_df['Date'],
        open=main_stock_df['Open'],
        high=main_stock_df['High'],
        low=main_stock_df['Low'],
        close=main_stock_df['Close'],
        name='Candlestick'
    ))
    fig.add_trace(go.Scatter(
        x=main_stock_df['Date'],
        y=main_stock_df['MA20'],
        mode='lines',
        line=dict(color='blue', width=2),
        name='20-Day MA'
    ))
    fig.update_layout(title=f"{stock_input} Candlestick & MA", xaxis_title="Date", yaxis_title="Price (USD)", xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    # --- Gemini Verdict ---
    st.markdown('<p class="section-header">5️⃣ Buy/Sell/Hold Verdict</p>', unsafe_allow_html=True)
    verdict, confidence = get_gemini_verdict(stock_input, main_stock_df['Close'].tolist())
    color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"
    st.markdown(f"<h3 style='color:{color};'>💡 Verdict: {verdict} (Confidence: {int(confidence*100)}%)</h3>", unsafe_allow_html=True)

    # --- Comparison with selected stocks ---
    st.markdown('<p class="section-header">6️⃣ Comparison with Selected Stocks</p>', unsafe_allow_html=True)
    comparison_data = {}
    for symbol in selected_stocks:
        df = get_stock_data_gemini(symbol)
        if df is not None:
            comparison_data[symbol] = int(round(df['Close'].iloc[-1]))
    if comparison_data:
        comp_df = pd.DataFrame(list(comparison_data.items()), columns=['Stock','Latest Close'])
        st.table(comp_df.sort_values('Latest Close', ascending=False))
    else:
        st.info("No data available for selected comparison stocks.")

    # --- Top Performing Stocks ---
    st.markdown('<p class="section-header">7️⃣ Top Performing Stocks</p>', unsafe_allow_html=True)
    better = compare_stocks(comparison_data, latest)
    if better: st.success(f"Stocks outperforming {stock_input}: {', '.join(better)}")
    else: st.info(f"No selected stocks outperform {stock_input}.")
