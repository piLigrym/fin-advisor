import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import dill

class StockProfitPredictor:
    def __init__(self, tickers, start_date, end_date):
        self.tickers = tickers
        self.start_date = start_date
        self.end_date = end_date
        self.models = {}  

    def load_stock_data(self):
        stock_data = {}
        for ticker in self.tickers:
            try:
                company = yf.download(ticker, start=self.start_date, end=self.end_date)
                if not company.empty:
                    stock_data[ticker] = company
                else:
                    print(f"No data for the company {ticker}")
            except Exception as e:
                print(f"Error loading data for the company {ticker}: {str(e)}")
        return stock_data

    def train_model(self, ticker, X_train, y_train):
        model = LinearRegression()
        model.fit(X_train, y_train)
        self.models[ticker] = model  

    def calculate_profit(self, stock_data):
        results = []
        for ticker, data in stock_data.items():
            try:
                data['Next Close'] = data['Close'].shift(-30)
                data.dropna(inplace=True)
                X = data[['Close']]
                y = data['Next Close']

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)

                if ticker not in self.models:
                    self.train_model(ticker, X_train, y_train)

                current_price = X.iloc[-1]['Close']
                profit_per_share = self.models[ticker].predict([[current_price]])[0] - current_price

                results.append({
                    'Ticker': ticker,
                    'Company Name': yf.Ticker(ticker).info.get('longName', ticker),
                    'Current Price': data["Close"].iloc[-1],
                    'Profit per Share': profit_per_share
                })
            except Exception as e:
                print(f"Error when analyzing a company {ticker}: {str(e)}")
        
        return results
    
    def predict_on_date(self, prediction_date):
        stock_data = {}
        results = []
        for ticker in self.tickers:
            try:
                data = yf.download(ticker, start=prediction_date, end=prediction_date)
                if not data.empty:
                    current_price = data.iloc[0]['Close']
                    profit_per_share = self.models[ticker].predict([[current_price]])[0] - current_price
                    results.append({
                        'Ticker': ticker,
                        'Company Name': yf.Ticker(ticker).info.get('longName', ticker),
                        'Current Price': current_price,
                        'Profit per Share': profit_per_share
                    })
                else:
                    print(f"No data for company {ticker} as of date {prediction_date}")
            except Exception as e:
                print(f"Prediction error for the company {ticker} as of date {prediction_date}: {str(e)}")
        
        # Create a data frame count and sort by profitability 
        results_df = pd.DataFrame(results)
        results_df = results_df[results_df['Profit per Share'] > 0]
        results_df['Profit to Price Ratio'] = results_df['Profit per Share'] / results_df['Current Price']
        results_df = results_df.sort_values(by='Profit to Price Ratio', ascending=False) 
        return results_df

if __name__ == "__main__":
    # Data collection parameters
    sp500_df = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    tickers = sp500_df['Symbol'].tolist()
    start_date = '2023-06-24'
    end_date = '2024-06-24'
    
    # Creating an instance of a model class and retrieving data
    predictor = StockProfitPredictor(tickers, start_date, end_date)
    stock_data = predictor.load_stock_data()
    results = predictor.calculate_profit(stock_data)
    
    # Saving the model to a file
    model_filename = 'stock_profit_predictor.pkl'
    with open(model_filename, 'wb') as f:
        dill.dump(predictor, f)

    print(f"Model save in file '{model_filename}'.")
