from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class MemoryAuditLogModel(Base):
    __tablename__ = "memory_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    id_memory = Column(Integer, ForeignKey("memories.id"), nullable=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    action = Column(String, nullable=False, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
