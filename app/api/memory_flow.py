from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.memory_flow_schema import (
    ChatMemoryFlowRequestSchema,
    ChatMemoryFlowResponseSchema,
)
from app.services.memory_flow_service import run_chat_memory_flow


router = APIRouter(
    prefix="/flows",
    tags=["flows"],
)


@router.post("/chat-memory", response_model=ChatMemoryFlowResponseSchema)
def post_chat_memory_flow(
    payload: ChatMemoryFlowRequestSchema,
    db: Session = Depends(get_db),
):
    return run_chat_memory_flow(
        db=db,
        payload=payload,
    )
