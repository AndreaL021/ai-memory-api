from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.memory_types import MemoryType


class MemoryCreateSchema(BaseModel):
    id_user: int
    id_event: int | None = None
    memory_type: MemoryType
    content: str = Field(min_length=1)
    confidence: int = Field(default=50, ge=0, le=100)
    importance: int = Field(default=50, ge=0, le=100)


class MemoryResponseSchema(BaseModel):
    id: int
    id_user: int
    id_event: int | None
    id_superseded_by: int | None
    memory_type: str
    content: str
    confidence: int
    importance: int
    usefulness_score: int
    use_count: int
    success_count: int
    failure_count: int
    status: str
    security_level: str
    last_used_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MemoryUpdateSchema(BaseModel):
    memory_type: MemoryType | None = None
    content: str | None = Field(default=None, min_length=1)
    confidence: int | None = Field(default=None, ge=0, le=100)
    importance: int | None = Field(default=None, ge=0, le=100)
    status: str | None = None
    id_superseded_by: int | None = None
    reason: str | None = None


class MemoryUsageCreateSchema(BaseModel):
    id_user: int
    id_event: int | None = None
    consumer: str
    use_case: str
    used_successfully: bool | None = None
    usefulness_score: int | None = Field(default=None, ge=0, le=100)
    outcome_summary: str | None = None
    metrics: dict | None = None


class ContextResponseSchema(BaseModel):
    memories: list[MemoryResponseSchema]


class MemoryLogResponseSchema(BaseModel):
    id: int
    id_memory: int | None
    id_user: int
    id_event: int | None
    action: str
    decision: str | None
    trigger_source: str | None
    trigger_summary: str | None
    old_value: dict | None
    new_value: dict | None
    reason: str | None
    consumer: str | None
    use_case: str | None
    used_successfully: bool | None
    usefulness_score: int | None
    outcome_summary: str | None
    metrics: dict | None
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }


class MemoryObservabilityResponseSchema(BaseModel):
    memory: MemoryResponseSchema
    logs: list[MemoryLogResponseSchema]
