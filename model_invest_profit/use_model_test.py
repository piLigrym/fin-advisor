import dill
import pandas as pd  
import yfinance as yf

model_filename = 'stock_profit_predictor.pkl'
with open(model_filename, 'rb') as f:
    loaded_predictor = dill.load(f)

prediction_date = '2024-06-27'
profitable_stocks_df = loaded_predictor.predict_on_date(prediction_date)
print(profitable_stocks_df)
