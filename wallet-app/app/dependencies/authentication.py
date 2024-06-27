from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):

    user = User.verify_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user.id 