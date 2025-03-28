from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.database import init_db, database

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await init_db()
        yield
    finally:
        await database.disconnect()

app = FastAPI(lifespan=lifespan)