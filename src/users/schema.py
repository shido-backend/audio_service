from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from uuid import UUID

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = Field(None, description="Не требуется для OAuth")

class UserYandexCreate(UserBase):
    yandex_id: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    is_superuser: Optional[bool] = False
    email: Optional[str] = None

class UserInDB(BaseModel):
    email: str
    name: str | None
    id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime | None = None
    updated_at: datetime | None = None

class UserInDBwithPassword(UserBase):
    id: UUID 
    hashed_password: str
    
    class Config:
        from_attributes = True