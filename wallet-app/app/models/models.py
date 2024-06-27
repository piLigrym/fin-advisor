from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from passlib.context import CryptContext
import jwt

from datetime import datetime, timedelta, date
from app.db.database import database
from fastapi import HTTPException
from app.config import pwd_context

# Параметри для JWT
SECRET_KEY = "4858d2b95176d86423583083852d641c756348a1facfadc0902e109d3e5af517"
ALGORITHM = "HS256"

class User(BaseModel):
    first_name: str 
    last_name: str
    email: EmailStr
    hashed_password: str
    
    def create_token(self):
        to_encode = {
            "id": str(self.id),
            "exp": datetime.now() + timedelta(minutes=30)  # Токен дійсний 30 хвилин
        }
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def verify_token(token: str):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("email")
            if email is None:
                raise HTTPException(status_code=401, detail="Invalid token")
            user_data = database.users.find_one({"email": email})
            if user_data is None:
                raise HTTPException(status_code=401, detail="User not found")

            return User(**user_data)
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)

    # Метод для перевірки пароля
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)
    
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str

class TokenWithUser(BaseModel):
    access_token: str
    token_type: str
    user: User

class Transaction(BaseModel):
    email: EmailStr
    type: str
    amount: float
    category: str
    date: date

class TransactionRequest(BaseModel):
    email: str
    month: int
    year: int

class Budget(BaseModel):
    email: str
    total_budget: float
    food: float
    hospitality: float
    alcohol: float
    tobacco: float
    clothing: float
    public_utilities: float
    medical: float
    transport: float
    communication: float
    education: float
    others: float
    special: float
    gardening: float
    saving: float
    month: int
    year: int