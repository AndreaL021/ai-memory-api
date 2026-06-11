from app.database.database import SessionLocal


def get_db():
    # Provide one database session for a request and always close it afterwards.
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
