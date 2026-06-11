from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.schemas.memory_schema import MemoryResponseSchema


class EventCreateSchema(BaseModel):
    id_user: int
    content: str = Field(min_length=1)
    metadata_json: dict[str, Any] | None = None


class EventResponseSchema(BaseModel):
    id: int
    id_user: int
    content: str
    metadata_json: dict[str, Any] | None
    security_level: str
    processing_status: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MemoryCandidateResponseSchema(BaseModel):
    id: int
    id_event: int
    id_user: int
    id_memory: int | None
    memory_type: str
    content: str
    confidence: int
    reason: str
    status: str
    signals: dict[str, Any] | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class EventProcessingResponseSchema(BaseModel):
    event: EventResponseSchema
    candidates: list[MemoryCandidateResponseSchema]


class MemoryCandidatePromotionResponseSchema(BaseModel):
    candidate: MemoryCandidateResponseSchema
    memory: MemoryResponseSchema
