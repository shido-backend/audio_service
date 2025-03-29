import uuid
from sqlalchemy import UUID, Boolean, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.shared.models.base import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    name = Column(String, nullable=True)
    yandex_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    audios = relationship("Audio", back_populates="user")

    def __repr__(self):
        return f"<User {self.email}>"