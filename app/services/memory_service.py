from datetime import datetime

from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.memory_audit_log_model import MemoryAuditLogModel
from app.models.memory_model import MemoryModel
from app.models.memory_observation_model import MemoryObservationModel
from app.models.memory_usage_model import MemoryUsageModel
from app.schemas.memory_schema import (
    MemoryCreateSchema,
    MemoryUpdateSchema,
    MemoryUsageCreateSchema,
)
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
        importance=payload.importance,
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


def update_memory(db: Session, memory: MemoryModel, payload: MemoryUpdateSchema):
    # Update a memory while preserving audit and observability history.
    old_value = {
        "memory_type": memory.memory_type,
        "content": memory.content,
        "confidence": memory.confidence,
        "importance": memory.importance,
        "status": memory.status,
        "security_level": memory.security_level,
        "id_superseded_by": memory.id_superseded_by,
    }

    next_content = payload.content if payload.content is not None else memory.content
    next_memory_type = payload.memory_type.value if payload.memory_type else memory.memory_type
    security_result = validate_normal_memory_content(
        content=next_content,
        memory_type=next_memory_type,
    )

    if not security_result["can_store"]:
        create_memory_observation(
            db=db,
            id_user=memory.id_user,
            id_project=memory.id_project,
            id_event=memory.id_source_event,
            id_memory=memory.id,
            observation_type="memory_update_rejected",
            reason="Raw secret material cannot be stored as normal memory text.",
            decision="rejected",
            metrics={
                "secret_count": security_result["secret_count"],
            },
        )
        db.commit()
        return None

    memory.memory_type = next_memory_type
    memory.content = security_result["content"]
    memory.security_level = security_result["security_level"]

    if payload.confidence is not None:
        memory.confidence = payload.confidence

    if payload.importance is not None:
        memory.importance = payload.importance

    if payload.status is not None:
        memory.status = payload.status

    if payload.id_superseded_by is not None:
        memory.id_superseded_by = payload.id_superseded_by
        memory.status = "outdated"

    memory.updated_at = datetime.utcnow()
    new_value = {
        "memory_type": memory.memory_type,
        "content": memory.content,
        "confidence": memory.confidence,
        "importance": memory.importance,
        "status": memory.status,
        "security_level": memory.security_level,
        "id_superseded_by": memory.id_superseded_by,
    }

    create_memory_audit_log(
        db=db,
        id_user=memory.id_user,
        id_memory=memory.id,
        action="memory_updated",
        old_value=old_value,
        new_value=new_value,
        reason=payload.reason or "Memory updated from explicit API request.",
    )
    create_memory_observation(
        db=db,
        id_user=memory.id_user,
        id_project=memory.id_project,
        id_event=memory.id_source_event,
        id_memory=memory.id,
        observation_type="memory_updated",
        reason=payload.reason or "The memory was updated by explicit API request.",
        decision="updated",
        metrics={
            "secret_count": security_result["secret_count"],
        },
    )
    db.commit()
    db.refresh(memory)
    return memory


def delete_memory(db: Session, memory: MemoryModel, reason: str | None = None):
    # Mark a memory as deleted without removing its audit trail.
    old_status = memory.status
    memory.status = "deleted"
    memory.updated_at = datetime.utcnow()

    create_memory_audit_log(
        db=db,
        id_user=memory.id_user,
        id_memory=memory.id,
        action="memory_deleted",
        old_value={
            "status": old_status,
        },
        new_value={
            "status": memory.status,
        },
        reason=reason or "Memory deleted from explicit API request.",
    )
    create_memory_observation(
        db=db,
        id_user=memory.id_user,
        id_project=memory.id_project,
        id_event=memory.id_source_event,
        id_memory=memory.id,
        observation_type="memory_deleted",
        reason=reason or "The memory was marked as deleted by explicit API request.",
        decision="deleted",
    )
    db.commit()
    db.refresh(memory)
    return memory


def get_memory_observability(db: Session, memory: MemoryModel):
    # Return audit and observation records explaining memory decisions.
    audit_logs = (
        db.query(MemoryAuditLogModel)
        .filter(MemoryAuditLogModel.id_memory == memory.id)
        .order_by(desc(MemoryAuditLogModel.created_at), desc(MemoryAuditLogModel.id))
        .all()
    )
    observations = (
        db.query(MemoryObservationModel)
        .filter(MemoryObservationModel.id_memory == memory.id)
        .order_by(desc(MemoryObservationModel.created_at), desc(MemoryObservationModel.id))
        .all()
    )

    return {
        "memory": memory,
        "audit_logs": audit_logs,
        "observations": observations,
    }


def record_memory_usage(
    db: Session,
    memory: MemoryModel,
    payload: MemoryUsageCreateSchema,
):
    # Track when a memory was used and update lightweight usefulness counters.
    usage = MemoryUsageModel(
        id_memory=memory.id,
        id_user=payload.id_user,
        id_project=payload.id_project,
        id_event=payload.id_event,
        consumer=payload.consumer,
        use_case=payload.use_case,
        used_successfully=payload.used_successfully,
        usefulness_score=payload.usefulness_score,
        outcome_summary=payload.outcome_summary,
        metrics=payload.metrics,
    )
    db.add(usage)

    memory.use_count += 1
    memory.last_used_at = datetime.utcnow()

    if payload.used_successfully is True:
        memory.success_count += 1

    if payload.used_successfully is False:
        memory.failure_count += 1

    if payload.usefulness_score is not None:
        memory.usefulness_score = payload.usefulness_score
    elif payload.used_successfully is True:
        memory.usefulness_score = min(100, memory.usefulness_score + 5)
    elif payload.used_successfully is False:
        memory.usefulness_score = max(0, memory.usefulness_score - 10)

    memory.updated_at = datetime.utcnow()
    create_memory_observation(
        db=db,
        id_user=memory.id_user,
        id_project=memory.id_project,
        id_event=payload.id_event,
        id_memory=memory.id,
        observation_type="memory_used",
        reason=payload.outcome_summary or "Memory usage recorded from API request.",
        decision="used",
        metrics={
            "consumer": payload.consumer,
            "use_case": payload.use_case,
            "used_successfully": payload.used_successfully,
            "usefulness_score": memory.usefulness_score,
            "use_count": memory.use_count,
        },
    )
    db.commit()
    db.refresh(memory)
    return usage
