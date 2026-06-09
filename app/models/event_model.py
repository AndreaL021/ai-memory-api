from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text

from app.database.database import Base


class EventModel(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    id_project = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    source_type = Column(String, nullable=False, index=True)
    source_ref = Column(String, nullable=True, index=True)
    content = Column(Text, nullable=False)
    metadata_json = Column(JSON, nullable=True)
    security_level = Column(String, nullable=False, default="confidential", index=True)
    processing_status = Column(String, nullable=False, default="pending", index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
