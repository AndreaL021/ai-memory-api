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


class MemoryUpdateSchema(BaseModel):
    memory_type: MemoryType | None = None
    content: str | None = Field(default=None, min_length=1)
    confidence: int | None = Field(default=None, ge=0, le=100)
    status: str | None = None
    reason: str | None = None


class ContextResponseSchema(BaseModel):
    memories: list[MemoryResponseSchema]


class MemoryAuditLogResponseSchema(BaseModel):
    id: int
    id_memory: int | None
    id_user: int
    action: str
    old_value: dict | None
    new_value: dict | None
    reason: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MemoryObservationResponseSchema(BaseModel):
    id: int
    id_memory: int | None
    id_user: int
    id_project: int | None
    id_event: int | None
    observation_type: str
    reason: str
    trigger_source: str | None
    trigger_summary: str | None
    decision: str | None
    metrics: dict | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MemoryObservabilityResponseSchema(BaseModel):
    memory: MemoryResponseSchema
    audit_logs: list[MemoryAuditLogResponseSchema]
    observations: list[MemoryObservationResponseSchema]
