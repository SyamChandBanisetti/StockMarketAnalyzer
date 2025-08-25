import yfinance as yf
from datetime import datetime, timedelta

def get_stock_data(symbol):
    """Fetch last 1 year stock data from Yahoo Finance."""
    try:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)
        df = yf.download(symbol, start=start_date, end=end_date)
        df.reset_index(inplace=True)
        if df.empty or 'Close' not in df.columns:
            return None
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
