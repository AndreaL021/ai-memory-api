from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class MemoryObservationModel(Base):
    __tablename__ = "memory_observations"

    id = Column(Integer, primary_key=True, index=True)
    id_memory = Column(Integer, ForeignKey("memories.id"), nullable=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    id_project = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    id_event = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    observation_type = Column(String, nullable=False, index=True)
    reason = Column(Text, nullable=False)
    trigger_source = Column(String, nullable=True, index=True)
    trigger_summary = Column(Text, nullable=True)
    decision = Column(String, nullable=True, index=True)
    metrics = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
