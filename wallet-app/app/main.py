from fastapi import FastAPI, HTTPException
from app.models.models import Transaction, Budget, User
from app.routers import transactions, user, budget, predictions
from pydantic import BaseModel
import os
import subprocess 
from datetime import datetime, timedelta

current_directory = os.path.dirname(__file__)
today_date_str = datetime.today().strftime('%Y-%m-%d')
JSON_FILENAME = os.path.join(current_directory,"..", f'profitable_stocks_{today_date_str}.json')

app = FastAPI()

app.include_router(transactions.router)
app.include_router(user.router)
app.include_router(budget.router)
app.include_router(predictions.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the financial management API"}

@app.on_event("startup")
async def startup_event():
    try:      
        if not os.path.exists(JSON_FILENAME):
            script_path = os.path.join(current_directory, '..', 'data.py')
            subprocess.run(['python', script_path], check=True)
            print("Data generation script executed on startup.")
        else:
            print(f"File {JSON_FILENAME} already exists. Skipping data generation.")

    except Exception as e:
        print(f"Error running data generation script: {str(e)}")


class PredictionIncomeResponse(BaseModel):
    profitable_stocks: list