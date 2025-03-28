from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from src.base.utils.password import get_password_hash
from src.users.schema import UserCreate, UserInDBwithPassword, UserUpdate, UserInDB
from src.base.repositories.base import BaseRepository
from src.users.model import User

class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = BaseRepository(User, session)
    
    async def get_user(self, user_id: int) -> Optional[UserInDB]:
        user = await self.repository.get(user_id)
        return UserInDB.model_validate(user) if user else None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        user = await self.repository.get_by_field("email", email)
        return UserInDB.model_validate(user) if user else None

    async def get_user_by_email_with_password(self, email: str) -> Optional[User]:
        user = await self.repository.get_by_field("email", email)
        return UserInDBwithPassword.model_validate(user) if user else None
    
    async def get_all_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        users = await self.repository.get_all(skip, limit)
        return [UserInDB.model_validate(user.__dict__) for user in users]
    
    async def create_user(self, user_data: UserCreate) -> User:
        hashed_password = get_password_hash(user_data.password)
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            hashed_password=hashed_password
        )
        self.repository.session.add(db_user)
        await self.repository.session.commit()
        await self.repository.session.refresh(db_user)
        return db_user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserInDB]:
        user = await self.repository.update(user_id, user_data)
        return UserInDB.model_validate(user) if user else None
    
    async def delete_user(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)