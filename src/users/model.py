from sqlalchemy import Boolean, Column, Integer, String
from src.base.models.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    name = Column(String, nullable=True)
    
    def __repr__(self):
        return f"<User {self.email}>"