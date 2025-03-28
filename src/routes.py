from fastapi import APIRouter
from src.users.router import UserRouter

api_router = APIRouter()

api_router.include_router(
    UserRouter,
    prefix="/users",
    tags=["Users"]
)