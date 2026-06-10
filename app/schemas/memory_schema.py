from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.memory_types import MemoryType


class MemoryCreateSchema(BaseModel):
    id_user: int
    id_project: int | None = None
    id_source_event: int | None = None
    memory_type: MemoryType
    content: str = Field(min_length=1)
    confidence: int = Field(default=50, ge=0, le=100)
    importance: int = Field(default=50, ge=0, le=100)


class MemoryResponseSchema(BaseModel):
    id: int
    id_user: int
    id_project: int | None
    id_source_event: int | None
    memory_type: str
    content: str
    confidence: int
    status: str
    security_level: str
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class ContextResponseSchema(BaseModel):
    memories: list[MemoryResponseSchema]
