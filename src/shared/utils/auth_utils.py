from datetime import datetime, timedelta
from jose import jwt
from src.core.config.config import settings

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.auth.jwt_secret,
        algorithm=settings.auth.jwt_algorithm
    )
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = None) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=30) 
    data.update({"exp": expire, "type": "refresh"})
    return jwt.encode(data, settings.auth.jwt_secret, algorithm=settings.auth.jwt_algorithm)