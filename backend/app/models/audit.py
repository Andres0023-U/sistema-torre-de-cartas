from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    __table_args__ = {"schema": "audit"}

    audit_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("security.user.user_id"))
    action = Column(String(50), nullable=False)
    table_name = Column(String(100), nullable=False)
    record_id = Column(Text, nullable=False)
    old_values = Column(Text)
    new_values = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())