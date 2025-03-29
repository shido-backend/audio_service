import uuid
from sqlalchemy import UUID, Boolean, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.shared.models.base import Base
from src.users.model import User 

class Audio(Base):
    __tablename__ = "audios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    title = Column(String, nullable=False)
    duration = Column(Integer)
    size = Column(Integer)
    format = Column(String(10))
    is_public = Column(Boolean, default=False)
    file_path = Column(String, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", back_populates="audios")