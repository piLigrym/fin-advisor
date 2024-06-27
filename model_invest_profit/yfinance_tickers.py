import yfinance as yf
import pandas as pd

def get_sp500_tickers():
    sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    tickers = sp500_df['Symbol'].tolist()  
    return tickers

if __name__ == "__main__":
    tickers = get_sp500_tickers()
    print(tickers)
