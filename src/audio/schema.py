from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AudioBase(BaseModel):
    title: str
    is_public: bool = False

class AudioCreate(AudioBase):
    pass

class AudioInDB(AudioBase):
    id: UUID
    user_id: UUID
    duration: int
    size: int
    format: str
    file_path: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True