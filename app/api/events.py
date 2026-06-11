from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.event_schema import (
    EventCreateSchema,
    EventProcessingResponseSchema,
    EventResponseSchema,
    MemoryCandidateResponseSchema,
)
from app.services.events.event_service import create_event, get_event, list_event_candidates
from app.services.memory.memory_capture_service import process_event_for_memory_candidates


router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.post("", response_model=EventResponseSchema)
def post_event(payload: EventCreateSchema, db: Session = Depends(get_db)):
    # Create a raw event without running the full memory flow.
    return create_event(
        db=db,
        payload=payload,
    )


@router.post("/{event_id}/process", response_model=EventProcessingResponseSchema)
def process_event(event_id: int, db: Session = Depends(get_db)):
    # Process one existing event and generate memory candidates from it.
    event = get_event(
        db=db,
        event_id=event_id,
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    candidates = process_event_for_memory_candidates(
        db=db,
        event=event,
    )

    return {
        "event": event,
        "candidates": candidates,
    }


@router.get("/{event_id}/candidates", response_model=list[MemoryCandidateResponseSchema])
def get_event_candidates(event_id: int, db: Session = Depends(get_db)):
    # Return the candidates that were generated from one event.
    event = get_event(
        db=db,
        event_id=event_id,
    )

    if not event:
        raise HTTPException(
            status_code=404,
            detail="Event not found",
        )

    return list_event_candidates(
        db=db,
        event_id=event_id,
    )
