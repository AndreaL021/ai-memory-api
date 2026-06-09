from sqlalchemy.orm import Session

from app.models.memory_audit_log_model import MemoryAuditLogModel
from app.models.memory_observation_model import MemoryObservationModel


def create_memory_audit_log(
    db: Session,
    id_user: int,
    action: str,
    id_memory: int | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    reason: str | None = None,
):
    audit_log = MemoryAuditLogModel(
        id_memory=id_memory,
        id_user=id_user,
        action=action,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
    )

    db.add(audit_log)
    return audit_log


def create_memory_observation(
    db: Session,
    id_user: int,
    observation_type: str,
    reason: str,
    id_memory: int | None = None,
    id_project: int | None = None,
    id_event: int | None = None,
    trigger_source: str | None = None,
    trigger_summary: str | None = None,
    decision: str | None = None,
    metrics: dict | None = None,
):
    observation = MemoryObservationModel(
        id_memory=id_memory,
        id_user=id_user,
        id_project=id_project,
        id_event=id_event,
        observation_type=observation_type,
        reason=reason,
        trigger_source=trigger_source,
        trigger_summary=trigger_summary,
        decision=decision,
        metrics=metrics,
    )

    db.add(observation)
    return observation


def log_secret_access(
    db: Session,
    id_user: int,
    secret_reference_id: int,
    reason: str,
    action: str = "secret_access",
):
    return create_memory_audit_log(
        db=db,
        id_user=id_user,
        action=action,
        old_value=None,
        new_value={
            "secret_reference_id": secret_reference_id,
        },
        reason=reason,
    )
