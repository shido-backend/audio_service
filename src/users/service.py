from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.users.schema import UserCreate, UserUpdate, UserInDB
from src.base.repositories.base import BaseRepository
from src.users.model import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = BaseRepository(User, session)
    
    async def get_user(self, user_id: int) -> Optional[UserInDB]:
        user = await self.repository.get(user_id)
        return UserInDB.model_validate(user) if user else None
    
    async def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        user = await self.repository.get_by_field("email", email)
        return UserInDB.model_validate(user) if user else None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        users = await self.repository.get_all(skip, limit)
        return [UserInDB.model_validate(user) for user in users]
    
    async def create_user(self, user_data: UserCreate) -> UserInDB:
        user = await self.repository.create(user_data)
        return UserInDB.model_validate(user)
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserInDB]:
        user = await self.repository.update(user_id, user_data)
        return UserInDB.model_validate(user) if user else None
    
    async def delete_user(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)