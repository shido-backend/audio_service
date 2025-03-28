from typing import TypeVar, Generic, Optional, List, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.declarative import DeclarativeMeta
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=DeclarativeMeta) 
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model = model
        self.session = session

    async def get(self, id: Any) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).where(self.model.id == id))
        return result.scalars().first()

    async def get_by_field(self, field_name: str, value: Any) -> Optional[ModelType]:
        field = getattr(self.model, field_name)
        result = await self.session.execute(select(self.model).where(field == value))
        return result.scalars().first()

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump())
        self.session.add(db_obj)
        await self.session.commit()
        await self.session.refresh(db_obj)
        return db_obj

    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        await self.session.execute(
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in.model_dump(exclude_unset=True))
        )
        await self.session.commit()
        return await self.get(id)

    async def delete(self, id: Any) -> bool:
        await self.session.execute(delete(self.model).where(self.model.id == id))
        await self.session.commit()
        return True