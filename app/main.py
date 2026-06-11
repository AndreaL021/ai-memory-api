from fastapi import FastAPI

from app.api.events import router as events_router
from app.api.memory_flow import router as memory_flow_router
from app.api.memory_candidates import router as memory_candidates_router
from app.api.memories import router as memories_router
from app.database.init_db import drop_database, init_database


app = FastAPI(
    title="AI Memory API",
)


@app.on_event("startup")
def startup():
    # Initialize database tables when the FastAPI application starts.
    drop_database()
    init_database()


app.include_router(events_router)
app.include_router(memory_flow_router)
app.include_router(memory_candidates_router)
app.include_router(memories_router)


@app.get("/")
def root():
    # Return a simple message confirming that the API is running.
    return {
        "message": "AI Memory API running",
    }


@app.get("/health")
def health():
    # Return a lightweight health check response for manual or automated checks.
    return {
        "status": "ok",
    }
