from typing import List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import joblib
from app.db.database import database
import dill
import yfinance as yf
import pandas as pd
import os
import json

router = APIRouter(
    prefix="/predictions",
    tags=["predictions"]
)

class ModelRecommendInvest:
    def __init__(self):
        self.model = self.load()

    @staticmethod
    def load():
        modelLoad = joblib.load('app/mlmodels/model_min_invest.joblib')
        return modelLoad

    def predictMinInvest(self, data: List[float]) -> float:
        prediction = self.model.predict([data])
        return prediction[0]
    
modelRecommendInvest = ModelRecommendInvest()

async def get_transactions(database, email):
    start_date = datetime.now() - timedelta(days=30)
    start_date_iso = start_date.isoformat()
    end_date_iso = datetime.now().isoformat()
    transactions_cursor = database.transactions.find({
        "email": email,
        "date": {"$gte": start_date_iso, "$lt": end_date_iso}
    })
    category_sums = {
        "Total Income": 0.0,
        "Total Expenses": 0.0,
        "Food": 0.0,
        "Hospitality": 0.0,
        "Alcohol": 0.0,
        "Tobacco": 0.0,
        "Clothing": 0.0,
        "Public Utilities": 0.0,
        "Medical": 0.0,
        "Transport": 0.0,
        "Communication": 0.0,
        "Education": 0.0,
        "Others": 0.0,
        "Special": 0.0,
        "Gardening": 0.0,
        "Saving": 0.0
    }
    async for transaction in transactions_cursor:
        amount = transaction.get("amount", 0.0)
        category = transaction.get("category", "Others")
        
        if transaction["type"] == "Income":
            category_sums["Total Income"] += amount
        elif transaction["type"] == "Expanse":
            category_sums["Total Expenses"] += amount
        elif transaction["type"] == "Saving":
            category_sums["Saving"] += amount
        if category in category_sums:
            category_sums[category] += amount
        else:
            category_sums["Others"] += amount
    
    prepared_data = [
        category_sums["Total Income"],
        category_sums["Total Expenses"],
        category_sums["Food"],
        category_sums["Hospitality"],
        category_sums["Alcohol"],
        category_sums["Tobacco"],
        category_sums["Clothing"],
        category_sums["Public Utilities"],
        category_sums["Medical"],
        category_sums["Transport"],
        category_sums["Communication"],
        category_sums["Education"],
        category_sums["Others"],
        category_sums["Special"],
        category_sums["Gardening"],
        category_sums["Saving"]
    ]
    return prepared_data

class PredictionRequest(BaseModel):
    email: str

class PredictionResponse(BaseModel):
    prediction: float

@router.post("/predict-recommend-invest", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    try:
        data = await get_transactions(database, request.email)
        predictionMinInvest = modelRecommendInvest.predictMinInvest(data)
        return PredictionResponse(prediction=predictionMinInvest)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

class PredictionIncomeResponse(BaseModel):
    profitable_stocks: list

@router.get("/predict-profitable-stocks", response_model=PredictionIncomeResponse)
async def predict_profitable_stocks():
    current_directory = os.path.dirname(__file__)
    today_date_str = datetime.today().strftime('%Y-%m-%d')
    JSON_FILENAME = os.path.join(current_directory,"..","..", f'profitable_stocks_{today_date_str}.json')
    try:
        if not os.path.exists(JSON_FILENAME):
            raise HTTPException(status_code=500, detail="JSON file with predictions not found.")
        
        with open(JSON_FILENAME, 'r') as f:
            profitable_stocks_list = [json.loads(line) for line in f]
            
        top_5_profitable_stocks = profitable_stocks_list[:5]
        
        return PredictionIncomeResponse(profitable_stocks=top_5_profitable_stocks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))