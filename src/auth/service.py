from sqlalchemy.ext.asyncio import AsyncSession
from src.core.config.config import settings
from src.auth.schema import Token
from src.users.service import UserService
from src.users.schema import UserCreate, UserInDB, UserYandexCreate
from src.shared.utils.auth_utils import create_access_token, create_refresh_token
from src.shared.utils.password_utils import verify_password
from datetime import timedelta
from fastapi import HTTPException, status
from src.shared.clients.yandex import YandexAuthClient
from jose import jwt, JWTError


class AuthService:
    def __init__(self, session: AsyncSession = None):
        self.session = session
        self.user_service = UserService(session) if session else None

    def generate_yandex_auth_url(self) -> str:
        return YandexAuthClient.get_auth_url()

    async def process_yandex_callback(self, code: str) -> Token:
        yandex_token = await YandexAuthClient.get_token(code)
        user_info = await YandexAuthClient.get_user_info(yandex_token)
        user = await self._sync_user_with_database(user_info)
        return self._issue_jwt_token(user)

    async def register_user(self, user_data: UserCreate) -> Token:
        existing_user = await self.user_service.get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        db_user = await self.user_service.create_user(user_data)
        return self._issue_jwt_token(db_user)

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.user_service.get_user_by_email_with_password(email)
        
        if not user or user.hashed_password is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Password authentication not available for this user"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password"
            )
        
        return self._issue_jwt_token(user)

    async def get_current_user_for_auth(self, email: str) -> UserInDB:
        user = await self.user_service.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    def _issue_jwt_token(self, user) -> Token:
        return Token(
            access_token=create_access_token(data={"sub": user.email}),
            refresh_token=create_refresh_token(data={"sub": user.email})
        )

    async def _sync_user_with_database(self, user_info: dict):
        user_data = UserYandexCreate(
            email=user_info['default_email'],
            name=user_info.get('real_name', user_info['login']),
            yandex_id=str(user_info['id'])
        )

        existing_user = await self.user_service.get_by_yandex_id(user_data.yandex_id)
        if existing_user:
            return existing_user

        return await self.user_service.create_user(user_data)

    async def refresh_token(self, refresh_token: str) -> Token:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        try:
            payload = jwt.decode(
                refresh_token,
                settings.auth.jwt_secret,
                algorithms=[settings.auth.jwt_algorithm]
            )
            if payload.get("type") != "refresh":
                raise credentials_exception
                
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = await self.user_service.get_user_by_email(email)
        if user is None:
            raise credentials_exception
            
        return self._issue_jwt_token(user)
