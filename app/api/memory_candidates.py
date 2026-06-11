from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.event_schema import MemoryCandidatePromotionResponseSchema
from app.services.memory.memory_capture_service import (
    get_memory_candidate,
    promote_memory_candidate,
)


router = APIRouter(
    prefix="/memory-candidates",
    tags=["memory-candidates"],
)


@router.post("/{candidate_id}/promote", response_model=MemoryCandidatePromotionResponseSchema)
def promote_candidate(candidate_id: int, db: Session = Depends(get_db)):
    # Manually promote a memory candidate into a persistent memory.
    candidate = get_memory_candidate(
        db=db,
        candidate_id=candidate_id,
    )

    if not candidate:
        raise HTTPException(
            status_code=404,
            detail="Memory candidate not found",
        )

    memory = promote_memory_candidate(
        db=db,
        candidate=candidate,
    )

    if not memory:
        raise HTTPException(
            status_code=422,
            detail="Memory candidate could not be promoted.",
        )

    return {
        "candidate": candidate,
        "memory": memory,
    }
