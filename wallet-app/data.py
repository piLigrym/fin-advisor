import dill
import pandas as pd  
import yfinance as yf
from datetime import datetime, timedelta
import os
today_date_str = datetime.today().strftime('%Y-%m-%d')
JSON_FILENAME = os.path.join(os.path.dirname(__file__), f'profitable_stocks_{today_date_str}.json')
model_filename = 'app/mlmodels/stock_profit_predictor.pkl'
with open(model_filename, 'rb') as f:
    loaded_predictor = dill.load(f)

today_date = datetime.today().strftime('%Y-%m-%d')
profitable_stocks_df = loaded_predictor.predict_on_date(today_date)
profitable_stocks_df.to_json(JSON_FILENAME, orient='records', lines=True)