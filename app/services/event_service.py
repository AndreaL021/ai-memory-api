from sqlalchemy.orm import Session

from app.models.event_model import EventModel
from app.models.memory_candidate_model import MemoryCandidateModel
from app.schemas.event_schema import EventCreateSchema
from app.services.security_service import validate_normal_memory_content


def create_event(db: Session, payload: EventCreateSchema):
    # Store a raw captured event after applying secret redaction and classification.
    security_result = validate_normal_memory_content(
        content=payload.content,
    )

    event = EventModel(
        id_user=payload.id_user,
        id_project=payload.id_project,
        source_type=payload.source_type,
        source_ref=payload.source_ref,
        content=security_result["content"],
        metadata_json={
            **(payload.metadata_json or {}),
            "secret_count": security_result["secret_count"],
            "can_store_as_memory": security_result["can_store"],
        },
        security_level=security_result["security_level"],
        processing_status="captured",
    )

    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def get_event(db: Session, event_id: int):
    # Return a captured event by id, or None when it does not exist.
    return db.query(EventModel).filter(EventModel.id == event_id).first()


def list_event_candidates(db: Session, event_id: int):
    # Return memory candidates generated from a specific event.
    return (
        db.query(MemoryCandidateModel)
        .filter(MemoryCandidateModel.id_event == event_id)
        .order_by(MemoryCandidateModel.id)
        .all()
    )
