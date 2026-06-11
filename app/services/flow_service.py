from sqlalchemy.orm import Session

from app.schemas.event_schema import EventCreateSchema
from app.schemas.memory_flow_schema import ChatMemoryFlowRequestSchema

from app.services.events.event_service import create_event
from app.services.memory.memory_capture_service import (
    process_event_for_memory_candidates,
    promote_memory_candidate,
)
from app.services.memory.memory_service import list_memories


def run_chat_memory_flow(db: Session, payload: ChatMemoryFlowRequestSchema):
    # Run the full chat-memory pipeline used by Postman and future integrations.
    event = create_event(
        db=db,
        payload=EventCreateSchema(
            id_user=payload.id_user,
            content=payload.content,
        ),
    )
    candidates = process_event_for_memory_candidates(
        db=db,
        event=event,
    )
    promoted_memories = []

    for candidate in candidates:
        if candidate.confidence < payload.auto_promote_min_confidence:
            continue

        memory = promote_memory_candidate(
            db=db,
            candidate=candidate,
        )

        if memory:
            promoted_memories.append(memory)

    context_memories = list_memories(
        db=db,
        id_user=payload.id_user,
        limit=20,
    )

    return {
        "event": event,
        "candidates": candidates,
        "promoted_memories": promoted_memories,
        "context_memories": context_memories,
    }
