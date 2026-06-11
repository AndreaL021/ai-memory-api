from pydantic import BaseModel, Field

from app.schemas.event_schema import EventResponseSchema, MemoryCandidateResponseSchema
from app.schemas.memory_schema import MemoryResponseSchema


class ChatMemoryFlowRequestSchema(BaseModel):
    id_user: int
    id_project: int | None = None
    source_ref: str | None = None
    content: str = Field(min_length=1)
    auto_promote_min_confidence: int = Field(default=85, ge=0, le=100)


class ChatMemoryFlowResponseSchema(BaseModel):
    event: EventResponseSchema
    candidates: list[MemoryCandidateResponseSchema]
    promoted_memories: list[MemoryResponseSchema]
    context_memories: list[MemoryResponseSchema]
