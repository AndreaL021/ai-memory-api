from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.event_schema import EventCreateSchema, EventResponseSchema
from app.services.event_service import create_event


router = APIRouter(
    prefix="/events",
    tags=["events"],
)


@router.post("", response_model=EventResponseSchema)
def post_event(payload: EventCreateSchema, db: Session = Depends(get_db)):
    return create_event(
        db=db,
        payload=payload,
    )
