import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils.data_fetch import get_stock_data
from utils.gemini_api import get_gemini_verdict
from utils.kpi_utils import calculate_kpis, compare_stocks

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Stock Market Analyzer", layout="wide")
st.markdown("## 📊 Stock Market Analyzer Dashboard")

# --- User Input ---
stock_input = st.text_input("Enter Stock Symbol:", "AAPL")
reputed_stocks = ['AAPL','MSFT','GOOGL','AMZN','TSLA','FB','NVDA','JPM','V','DIS',
                  'MA','PYPL','NFLX','ADBE','INTC','CSCO','CRM','ORCL','NKE','KO',
                  'PFE','MRK','ABBV','PEP','XOM','CVX','WMT','T','UNH','HD']
selected_stocks = st.multiselect("Select Stocks for Comparison:", reputed_stocks, default=['AAPL','MSFT'])

# --- Fetch Data ---
main_stock_df = get_stock_data(stock_input)
comparison_data = {}
for symbol in selected_stocks:
    df = get_stock_data(symbol)
    if df is not None:
        comparison_data[symbol] = df['Close'].iloc[-1]

# --- KPIs ---
if main_stock_df is not None:
    latest, avg, high, low = calculate_kpis(main_stock_df)
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Latest Price", f"${latest:.2f}")
    kpi2.metric("Average Price (1Y)", f"${avg:.2f}")
    kpi3.metric("1-Year High", f"${high:.2f}")
    kpi4.metric("1-Year Low", f"${low:.2f}")

    # --- Price Chart ---
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=main_stock_df['Date'], y=main_stock_df['Close'], mode='lines', name='Close Price'))
    fig.update_layout(title=f"{stock_input} Price Trend", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig, use_container_width=True)

    # --- Gemini Verdict ---
    verdict, confidence = get_gemini_verdict(stock_input, main_stock_df['Close'].tolist())
    color = "green" if verdict=="BUY" else "red" if verdict=="SELL" else "orange"
    st.markdown(f"<h3 style='color:{color};'>💡 Verdict: {verdict} (Confidence: {confidence*100:.1f}%)</h3>", unsafe_allow_html=True)

# --- Comparison Table ---
if comparison_data:
    comp_df = pd.DataFrame(list(comparison_data.items()), columns=['Stock','Latest Close'])
    st.table(comp_df.sort_values(by='Latest Close', ascending=False))

# --- Top Better Stocks ---
if main_stock_df is not None and comparison_data:
    better_stocks = compare_stocks(comparison_data, latest)
    if better_stocks:
        st.success(f"Stocks performing better than {stock_input}: {', '.join(better_stocks)}")
    else:
        st.info("No selected stocks are outperforming the current stock.")
