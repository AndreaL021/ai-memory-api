from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from app.database.database import Base


class MemoryModel(Base):
    __tablename__ = "memories"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    id_project = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    id_source_event = Column(Integer, ForeignKey("events.id"), nullable=True, index=True)
    id_superseded_by = Column(Integer, ForeignKey("memories.id"), nullable=True, index=True)
    memory_type = Column(String, nullable=False, index=True)
    content = Column(Text, nullable=False)
    confidence = Column(Integer, nullable=False, default=50)
    importance = Column(Integer, nullable=False, default=50)
    usefulness_score = Column(Integer, nullable=False, default=0)
    use_count = Column(Integer, nullable=False, default=0)
    success_count = Column(Integer, nullable=False, default=0)
    failure_count = Column(Integer, nullable=False, default=0)
    status = Column(String, nullable=False, default="active", index=True)
    security_level = Column(String, nullable=False, default="confidential", index=True)
    valid_from = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
