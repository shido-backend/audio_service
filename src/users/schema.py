from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    
    class Config:
        from_attributes = True