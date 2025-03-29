from fastapi import Depends
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from passlib.context import CryptContext
from src.core.database import get_db
from src.core.config.config import settings
from src.auth.schema import TokenData
from src.users.service import UserService
from src.users.model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid authentication credentials"
    )
    try:
        payload = jwt.decode(token, settings.auth.jwt_secret, algorithms=[settings.auth.jwt_algorithm])
        if payload.get("type") == "refresh": 
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = await UserService(db).get_user_by_email(email)
    if user is None:
        raise credentials_exception
    return user