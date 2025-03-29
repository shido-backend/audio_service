import httpx
from fastapi import HTTPException
from src.core.config.config import settings

class YandexAuthClient:
    @staticmethod
    def get_auth_url() -> str:
        return (
            f"https://oauth.yandex.ru/authorize?"
            f"response_type=code&"
            f"client_id={settings.auth.yandex_client_id}&"
            f"redirect_uri={settings.auth.yandex_redirect_url}"
        )

    @staticmethod
    async def get_token(code: str) -> str:
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

    @staticmethod
    async def get_user_info(access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://login.yandex.ru/info",
                headers={"Authorization": f"OAuth {access_token}"},
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail="Failed to fetch user profile"
                )
            
            return response.json()