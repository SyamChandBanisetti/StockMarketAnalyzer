def calculate_kpis(df):
    """Return latest, average, high, low prices safely as floats."""
    if df is None or df.empty or 'Close' not in df.columns:
        return 0.0, 0.0, 0.0, 0.0

    latest = df['Close'].iloc[-1] if not df['Close'].empty else 0.0
    avg = df['Close'].mean() if not df['Close'].empty else 0.0
    high = df['Close'].max() if not df['Close'].empty else 0.0
    low = df['Close'].min() if not df['Close'].empty else 0.0

    return float(latest), float(avg), float(high), float(low)

def compare_stocks(stock_dict, base_price):
    """Return list of stocks performing better than base_price."""
    better = []
    for s, price in stock_dict.items():
        try:
            if float(price) > float(base_price):
                better.append(s)
        except:
            continue
    return better
