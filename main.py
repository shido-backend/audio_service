from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.core.database import init_db, shutdown_db
from src.routes import api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await shutdown_db()

app = FastAPI(
    lifespan=lifespan,
    title="Audio Service",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url=None
)

app.include_router(api_router, prefix="/api/v1")