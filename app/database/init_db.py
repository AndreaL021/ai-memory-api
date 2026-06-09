from app.database.database import Base, engine
from app.models import (
    EventModel,
    MemoryAuditLogModel,
    MemoryModel,
    MemoryObservationModel,
    MemoryUsageModel,
    ProjectModel,
    SecretReferenceModel,
    UserModel,
)


def init_database():
    Base.metadata.create_all(bind=engine)
