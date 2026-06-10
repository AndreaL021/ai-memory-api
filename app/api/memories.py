from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.memory_schema import (
    ContextResponseSchema,
    MemoryCreateSchema,
    MemoryResponseSchema,
)
from app.services.memory_service import create_memory, get_memory, list_memories


router = APIRouter(
    tags=["memories"],
)


@router.post("/memories", response_model=MemoryResponseSchema)
def post_memory(payload: MemoryCreateSchema, db: Session = Depends(get_db)):
    memory = create_memory(
        db=db,
        payload=payload,
    )

    if not memory:
        raise HTTPException(
            status_code=422,
            detail="Memory rejected because it contains raw secret material.",
        )

    return memory


@router.get("/memories", response_model=list[MemoryResponseSchema])
def get_memories(
    id_user: int,
    id_project: int | None = None,
    memory_type: str | None = None,
    limit: int = Query(default=50, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_memories(
        db=db,
        id_user=id_user,
        id_project=id_project,
        memory_type=memory_type,
        limit=limit,
    )


@router.get("/memories/{memory_id}", response_model=MemoryResponseSchema)
def get_memory_by_id(memory_id: int, db: Session = Depends(get_db)):
    memory = get_memory(
        db=db,
        memory_id=memory_id,
    )

    if not memory:
        raise HTTPException(
            status_code=404,
            detail="Memory not found",
        )

    return memory


@router.get("/context", response_model=ContextResponseSchema)
def get_context(
    id_user: int,
    id_project: int | None = None,
    limit: int = Query(default=20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return {
        "memories": list_memories(
            db=db,
            id_user=id_user,
            id_project=id_project,
            limit=limit,
        )
    }
