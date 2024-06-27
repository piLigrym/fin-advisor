from fastapi import APIRouter, HTTPException, status
from app.models.models import Budget
from typing import List
from app.db.database import database
from bson import json_util
from pydantic import BaseModel

router = APIRouter(
    prefix="/budget",
    tags=["budget"]
)

@router.post("/create", response_model=Budget)
async def create_new_budget(budget: Budget):
    budget_dict = budget.model_dump()
    try:
        result = await database.budgets.insert_one(budget_dict)
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

class BudgetRequest(BaseModel):
    email: str
    month: int
    year: int

@router.post("/get")
async def get_user_budgets(request: BudgetRequest):
    try:
        budgets = await database.budgets.find({
            "email": request.email,
            "year": request.year,
            "month": request.month,
        }).to_list(None)
        budgets = json_util.dumps(budgets)
        return budgets
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))