from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class MemoryLogModel(Base):
    __tablename__ = "memory_logs"

    id = Column(Integer, primary_key=True, index=True)
    id_memory = Column(Integer, ForeignKey("memories.id"), nullable=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    id_event = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    action = Column(String, nullable=False, index=True)
    decision = Column(String, nullable=True, index=True)
    trigger_source = Column(String, nullable=True, index=True)
    trigger_summary = Column(Text, nullable=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    reason = Column(Text, nullable=True)
    consumer = Column(String, nullable=True, index=True)
    use_case = Column(String, nullable=True, index=True)
    used_successfully = Column(Boolean, nullable=True)
    usefulness_score = Column(Integer, nullable=True)
    outcome_summary = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
