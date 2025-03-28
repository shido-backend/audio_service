from fastapi import APIRouter
from src.users.router import UserRouter
from src.auth.router import AuthRouter

api_router = APIRouter()

api_router.include_router(
    UserRouter,
    prefix="/users",
)
api_router.include_router(
    AuthRouter,
    prefix="/auth",
)