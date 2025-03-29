from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.schema import UserCreate, UserUpdate, UserInDB
from src.users.service import UserService
from src.core.database import get_db

UserRouter = APIRouter(tags=["Users"])

@UserRouter.get("/{user_id}", response_model=UserInDB)
async def read_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@UserRouter.get("/", response_model=List[UserInDB])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = UserService(db)
    return await service.get_all_users(skip, limit)

@UserRouter.put("/{user_id}", response_model=UserInDB)
async def update_user(user_id: UUID, user_data: UserUpdate, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return await service.update_user(user_id, user_data)

@UserRouter.delete("/{user_id}")
async def delete_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    service = UserService(db)
    user = await service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    await service.delete_user(user_id)
    return {"message": "User deleted successfully"}