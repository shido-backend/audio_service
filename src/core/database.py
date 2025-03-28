from typing import AsyncGenerator
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import AsyncAdaptedQueuePool
from src.core.config import settings

class Database:
    def __init__(self, db_url: str, *, echo: bool, pool_size: int, max_overflow: int):
        self._engine = create_async_engine(
            db_url,
            echo=echo,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_pre_ping=True,
            pool_recycle=3600,    
            pool_timeout=30,      
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        self.Base = declarative_base()

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()  
            except Exception as e:
                await session.rollback()
                raise e
            finally:
                await session.close()

    async def disconnect(self):
        await self._engine.dispose()

database = Database(
    settings.db.url,
    echo=settings.db.echo,  
    pool_size=settings.db.pool_size,
    max_overflow=settings.db.max_overflow
)
Base = database.Base
get_db = database.get_session 

async def init_db():
    pass