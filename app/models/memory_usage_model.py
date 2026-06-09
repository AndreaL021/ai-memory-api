from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class MemoryUsageModel(Base):
    __tablename__ = "memory_usage"

    id = Column(Integer, primary_key=True, index=True)
    id_memory = Column(Integer, ForeignKey("memories.id"), nullable=False, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    id_project = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    id_event = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    consumer = Column(String, nullable=False, index=True)
    use_case = Column(String, nullable=False, index=True)
    used_successfully = Column(Boolean, nullable=True)
    usefulness_score = Column(Integer, nullable=True)
    outcome_summary = Column(Text, nullable=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
