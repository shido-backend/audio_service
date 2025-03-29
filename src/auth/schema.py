from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional
from uuid import UUID

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[EmailStr] = None

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class YandexAuthResponse(BaseModel):
    code: str
    state: Optional[str] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True