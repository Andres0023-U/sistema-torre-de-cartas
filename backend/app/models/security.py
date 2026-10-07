from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, TIMESTAMP, func, true
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "role"
    __table_args__ = {"schema": "security"}

    role_id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True)

class User(Base):
    __tablename__ = "user"
    __table_args__ = {"schema": "security"}

    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("security.role.role_id"), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True, server_default=true())
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    role = relationship("Role")