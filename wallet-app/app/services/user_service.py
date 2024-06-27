from app.db.database import database
from app.models.models import UserCreate, User
from app.config import pwd_context

async def create_user(user: UserCreate) -> User:
    user_dict = user.model_dump()
    user_dict["hashed_password"] = User.hash_password(user_dict.pop("password"))
    new_user = await database["users"].insert_one(user_dict)
    created_user = await database["users"].find_one({"_id": new_user.inserted_id})
    return User(**created_user)

async def get_user_by_email(email: str):
    user = await database["users"].find_one({"email": email})
    return user