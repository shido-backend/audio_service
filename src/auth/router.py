from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from src.base.utils.get_current_user import get_current_user
from src.base.database import get_db
from src.auth.service import AuthService
from src.auth.schema import (Token, UserCreate, UserLogin, 
                            YandexAuthResponse, UserResponse)
from src.users.model import User

AuthRouter = APIRouter(tags=["Authentication"])

@AuthRouter.get("/yandex-login")
async def initiate_yandex_login():
    auth_service = AuthService()
    return JSONResponse({
        "auth_url": auth_service.generate_yandex_auth_url(),
        "instructions": "Redirect user to this URL for Yandex authentication"
    })

@AuthRouter.get("/yandex-callback")
async def handle_yandex_callback(
    request: Request,
    code: str = None,
    error: str = None,
    error_description: str = None,
    db: AsyncSession = Depends(get_db)
):
    if error:
        raise HTTPException(
            status_code=400,
            detail=f"Yandex auth error: {error_description or error}"
        )
    
    if not code:
        raise HTTPException(
            status_code=400,
            detail="Authorization code not provided"
        )
    
    try:
        token = await AuthService(db).process_yandex_callback(code)
        return JSONResponse({
            "access_token": token.access_token,
            "token_type": token.token_type
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="Internal server error during authentication"
        )

@AuthRouter.post("/register", response_model=Token)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService(db).register_user(user_data)

@AuthRouter.post("/login", response_model=Token)
async def login_user(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    return await AuthService(db).authenticate_user(
        email=login_data.email,
        password=login_data.password
    )

@AuthRouter.get("/me", response_model=UserResponse)
async def get_current_user_info(user: User = Depends(get_current_user)):
    return user