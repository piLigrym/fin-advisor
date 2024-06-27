from fastapi import APIRouter, HTTPException, Path, status
from pydantic import BaseModel
from app.models.models import Transaction, TransactionRequest
from app.db.database import database
from datetime import datetime
from bson import json_util

router = APIRouter(
    prefix="/transaction",
    tags=["transaction"]
)

@router.post("/create")
async def create_transaction(transaction: Transaction):
    transaction_dict = transaction.model_dump()
    transaction_dict['date'] = transaction.date.isoformat()
    try:
        result = await database.transactions.insert_one(transaction_dict)
        return {"id": str(result.inserted_id)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

class TransactionRequest(BaseModel):
    email: str
    month: int
    year: int

@router.post("/get")
async def get_transactions(request: TransactionRequest):
    start_date = datetime(request.year, request.month, 1)
    if request.month == 12:
        end_date = datetime(request.year + 1, 1, 1)
    else:
        end_date = datetime(request.year, request.month + 1, 1)
    start_date_iso = start_date.isoformat()
    end_date_iso = end_date.isoformat()
    transactions = await database.transactions.find({
        "email": request.email,
        "date": {
            "$gte": start_date_iso,
            "$lt": end_date_iso
        }
    }).to_list(None)
    transactions = json_util.dumps(transactions)
    return transactions

@router.post("/delete/{id}")
async def delete_transaction(id: str = Path(..., title="Transaction ID")):
    result = await database.transactions.delete_one({"_id": id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Transaction with id {id} not found")
    return {"message": f"Transaction with id {id} deleted"}