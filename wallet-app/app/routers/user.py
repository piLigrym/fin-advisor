from fastapi import APIRouter, HTTPException, Request
from app.models.models import UserCreate, User, TokenWithUser
from app.services.user_service import create_user, get_user_by_email
from app.db.database import database
from app.config import pwd_context
import jwt
from app.models.models import SECRET_KEY, ALGORITHM

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/register", response_model=User)
async def register_new_user(user: UserCreate):
    existing_user = await database["users"].find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    created_user = await create_user(user)
    return created_user

@router.post("/login", response_model=TokenWithUser)
async def login_user(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=422, detail="Please provide both email and password")
    user = await database["users"].find_one({"email": email})
    if not user or not pwd_context.verify(password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    token = jwt.encode({"email": email}, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer", "user": User(**user)}

@router.get("/{email}", response_model=User)
async def get_user(email: str):
    return await get_user_by_email(email)
