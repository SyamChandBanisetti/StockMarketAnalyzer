import yfinance as yf
from datetime import datetime, timedelta

end_date = datetime.today()
start_date = end_date - timedelta(days=365)

def get_stock_data(symbol):
    """Fetch last 1 year stock data from Yahoo Finance."""
    try:
        df = yf.download(symbol, start=start_date, end=end_date)
        df.reset_index(inplace=True)
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None
