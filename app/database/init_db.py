from app.database.database import Base, engine
from app.models import (
    EventModel,
    MemoryCandidateModel,
    MemoryLogModel,
    MemoryModel,
    SecretReferenceModel,
    UserModel,
)


def init_database():
    # Create all database tables declared by the SQLAlchemy models.
    Base.metadata.create_all(bind=engine)
