from sqlalchemy.orm import Session

from app.models.event_model import EventModel
from app.models.memory_candidate_model import MemoryCandidateModel
from app.schemas.event_schema import EventCreateSchema
from app.services.security.security_service import validate_normal_memory_content


def create_event(db: Session, payload: EventCreateSchema):
    # Store raw input as an event after redacting secrets and assigning security metadata.
    security_result = validate_normal_memory_content(
        content=payload.content,
    )

    event = EventModel(
        id_user=payload.id_user,
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
    # Return one captured event by id, or None when it does not exist.
    return db.query(EventModel).filter(EventModel.id == event_id).first()


def list_event_candidates(db: Session, event_id: int):
    # Return all memory candidates generated from a specific event.
    return (
        db.query(MemoryCandidateModel)
        .filter(MemoryCandidateModel.id_event == event_id)
        .order_by(MemoryCandidateModel.id)
        .all()
    )
