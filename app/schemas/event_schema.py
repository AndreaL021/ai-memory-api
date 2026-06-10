from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class EventCreateSchema(BaseModel):
    id_user: int
    id_project: int | None = None
    source_type: str
    source_ref: str | None = None
    content: str = Field(min_length=1)
    metadata_json: dict[str, Any] | None = None


class EventResponseSchema(BaseModel):
    id: int
    id_user: int
    id_project: int | None
    source_type: str
    source_ref: str | None
    content: str
    metadata_json: dict[str, Any] | None
    security_level: str
    processing_status: str
    created_at: datetime

    model_config = {
        "from_attributes": True,
    }
