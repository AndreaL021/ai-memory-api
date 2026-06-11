from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class MemoryCandidateModel(Base):
    __tablename__ = "memory_candidates"

    id = Column(Integer, primary_key=True, index=True)
    id_event = Column(Integer, ForeignKey("events.id"), nullable=False, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    id_memory = Column(Integer, ForeignKey("memories.id"), nullable=True, index=True)
    memory_type = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    confidence = Column(Integer, nullable=False, default=50)
    reason = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="pending", index=True)
    signals = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
