from fastapi import FastAPI

from app.database.init_db import init_database


app = FastAPI(
    title="AI Memory API",
)


@app.on_event("startup")
def startup():
    init_database()


@app.get("/")
def root():
    return {
        "message": "AI Memory API running",
    }


@app.get("/health")
def health():
    return {
        "status": "ok",
    }
