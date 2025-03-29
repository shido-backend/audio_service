from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: Optional[str] = Field(None, description="Не требуется для OAuth")

class UserYandexCreate(UserBase):
    yandex_id: str

class UserUpdate(BaseModel):
    name: Optional[str] = None

class UserInDB(UserBase):
    id: uuid.UUID  
    is_active: bool
    is_superuser: bool

class UserInDBwithPassword(UserBase):
    id: uuid.UUID 
    hashed_password: str
    
    class Config:
        from_attributes = True