import pandas as pd

def calculate_kpis(df):
    """Return latest, average, high, low prices."""
    latest = df['Close'].iloc[-1]
    avg = df['Close'].mean()
    high = df['Close'].max()
    low = df['Close'].min()
    return latest, avg, high, low

def compare_stocks(stock_dict, base_price):
    """Return stocks performing better than base_price."""
    return [s for s, price in stock_dict.items() if price > base_price]
