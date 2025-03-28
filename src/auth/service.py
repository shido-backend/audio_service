import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from src.base.config import settings
from src.auth.schema import Token
from src.users.service import UserService
from src.users.schema import UserCreate, UserInDB
from src.base.utils.auth_utils import create_access_token
from src.base.utils.password import verify_password, get_password_hash
from datetime import timedelta
from fastapi import HTTPException, status

class AuthService:
    def __init__(self, session: AsyncSession = None):
        self.session = session
        self.user_service = UserService(session) if session else None

    def generate_yandex_auth_url(self) -> str:
        return (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&"
            f"client_id={settings.auth.yandex_client_id}&"
            f"redirect_uri={settings.auth.yandex_redirect_url}"
        )

    async def process_yandex_callback(self, code: str) -> Token:
        yandex_token = await self._exchange_code_for_token(code)
        user_info = await self._fetch_yandex_user_info(yandex_token)
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
        
        if not user or not user.hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        if not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
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
            access_token=create_access_token(
                data={"sub": user.email},
                expires_delta=timedelta(minutes=settings.auth.jwt_expire_minutes),
            ),
            token_type="bearer"
        )

    async def _exchange_code_for_token(self, code: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://oauth.yandex.ru/token",
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "client_id": settings.auth.yandex_client_id,
                    "client_secret": settings.auth.yandex_client_secret,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to exchange authorization code"
                )
            
            return response.json().get("access_token")

    async def _fetch_yandex_user_info(self, token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://login.yandex.ru/info",
                headers={"Authorization": f"OAuth {token}"},
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to fetch user profile"
                )
            
            return response.json()

    async def _sync_user_with_database(self, user_info: dict):
        email = user_info.get("default_email")
        if not email:
            raise HTTPException(
                status_code=400,
                detail="User email not available"
            )
        
        user = await self.user_service.get_user_by_email(email)
        if not user:
            user_data = UserCreate(
                email=email,
                name=user_info.get("real_name") or user_info.get("display_name"),
                yandex_id=user_info.get("id")
            )
            user = await self.user_service.create_user(user_data)
        
        return user