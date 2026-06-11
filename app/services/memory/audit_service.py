from sqlalchemy.orm import Session

from app.models.memory_log_model import MemoryLogModel


def create_memory_log(
    db: Session,
    id_user: int,
    action: str,
    id_memory: int | None = None,
    id_event: int | None = None,
    decision: str | None = None,
    trigger_source: str | None = None,
    trigger_summary: str | None = None,
    old_value: dict | None = None,
    new_value: dict | None = None,
    reason: str | None = None,
    consumer: str | None = None,
    use_case: str | None = None,
    used_successfully: bool | None = None,
    usefulness_score: int | None = None,
    outcome_summary: str | None = None,
    metrics: dict | None = None,
):
    # Create one chronological log entry for memory audit, observability, or usage.
    log = MemoryLogModel(
        id_memory=id_memory,
        id_user=id_user,
        id_event=id_event,
        action=action,
        decision=decision,
        trigger_source=trigger_source,
        trigger_summary=trigger_summary,
        old_value=old_value,
        new_value=new_value,
        reason=reason,
        consumer=consumer,
        use_case=use_case,
        used_successfully=used_successfully,
        usefulness_score=usefulness_score,
        outcome_summary=outcome_summary,
        metrics=metrics,
    )

    db.add(log)
    return log


def log_secret_access(
    db: Session,
    id_user: int,
    secret_reference_id: int,
    reason: str,
    action: str = "secret_access",
):
    # Audit secret-reference access without storing or returning the raw secret value.
    return create_memory_log(
        db=db,
        id_user=id_user,
        action=action,
        old_value=None,
        new_value={
            "secret_reference_id": secret_reference_id,
        },
        reason=reason,
    )
