from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.memory_model import MemoryModel
from app.schemas.memory_schema import MemoryCreateSchema
from app.services.audit_service import create_memory_audit_log, create_memory_observation
from app.services.security_service import validate_normal_memory_content


def create_memory(db: Session, payload: MemoryCreateSchema):
    # Create a normal memory record, or reject it if it contains raw secret material.
    security_result = validate_normal_memory_content(
        content=payload.content,
        memory_type=payload.memory_type.value,
    )

    if not security_result["can_store"]:
        # Rejected memory attempts are still observable, so failures can be
        # explained and measured later.
        create_memory_observation(
            db=db,
            id_user=payload.id_user,
            id_project=payload.id_project,
            id_event=payload.id_source_event,
            observation_type="memory_rejected",
            reason="Raw secret material cannot be stored as normal memory text.",
            decision="rejected",
            metrics={
                "secret_count": security_result["secret_count"],
            },
        )
        db.commit()
        return None

    memory = MemoryModel(
        id_user=payload.id_user,
        id_project=payload.id_project,
        id_source_event=payload.id_source_event,
        memory_type=payload.memory_type.value,
        content=security_result["content"],
        confidence=payload.confidence,
        status="active",
        security_level=security_result["security_level"],
    )

    db.add(memory)
    db.flush()
    create_memory_audit_log(
        db=db,
        id_user=payload.id_user,
        id_memory=memory.id,
        action="memory_created",
        new_value={
            "memory_type": memory.memory_type,
            "security_level": memory.security_level,
            "importance": payload.importance,
        },
        reason="Memory created from explicit API request.",
    )
    create_memory_observation(
        db=db,
        id_user=payload.id_user,
        id_project=payload.id_project,
        id_event=payload.id_source_event,
        id_memory=memory.id,
        observation_type="memory_created",
        reason="The provided content was allowed as normal memory text.",
        decision="created",
        metrics={
            "confidence": payload.confidence,
            "importance": payload.importance,
            "secret_count": security_result["secret_count"],
        },
    )
    db.commit()
    db.refresh(memory)
    return memory


def list_memories(
    db: Session,
    id_user: int,
    id_project: int | None = None,
    memory_type: str | None = None,
    limit: int = 50,
):
    # Return active memories for a user, optionally scoped by project and type.
    query = db.query(MemoryModel).filter(
        MemoryModel.id_user == id_user,
        MemoryModel.status == "active",
    )

    if id_project is not None:
        query = query.filter(MemoryModel.id_project == id_project)

    if memory_type:
        query = query.filter(MemoryModel.memory_type == memory_type)

    return (
        query
        .order_by(desc(MemoryModel.updated_at), desc(MemoryModel.id))
        .limit(limit)
        .all()
    )


def get_memory(db: Session, memory_id: int):
    # Return a single memory by id, or None when it does not exist.
    return db.query(MemoryModel).filter(MemoryModel.id == memory_id).first()
