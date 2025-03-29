from typing import List, Optional, Union
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.shared.utils.password_utils import get_password_hash
from src.users.schema import UserCreate, UserInDBwithPassword, UserUpdate, UserInDB, UserYandexCreate
from src.shared.repositories.base import BaseRepository
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
    
    async def create_user(self, user_data: Union[UserCreate, UserYandexCreate]) -> User:
        # Prepare the data for User creation
        user_kwargs = {
            'email': user_data.email,
            'name': user_data.name,
            'hashed_password': None
        }
        
        # Handle password if it exists
        if isinstance(user_data, UserCreate) and user_data.password:
            user_kwargs['hashed_password'] = get_password_hash(user_data.password)
        
        # Handle yandex_id if it exists
        if isinstance(user_data, UserYandexCreate):
            user_kwargs['yandex_id'] = user_data.yandex_id
        
        # Create the User instance
        db_user = User(**user_kwargs)
        
        # Save to database using repository
        return await self.repository.create(db_user)

    async def get_by_yandex_id(self, yandex_id: str) -> Optional[User]:
        user = await self.repository.get_by_field("yandex_id", yandex_id)
        return user
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> Optional[UserInDB]:
        user = await self.repository.update(user_id, user_data)
        return UserInDB.model_validate(user) if user else None
    
    async def delete_user(self, user_id: int) -> bool:
        return await self.repository.delete(user_id)