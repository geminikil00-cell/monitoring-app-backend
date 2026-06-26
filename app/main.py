import os
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.db import models
from app.api.v1 import endpoints
from app.core.config import settings

# Note: In production, migrations should be handled by Alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parental Control API",
    description="API for monitoring and controlling child devices.",
    version="0.1.0"
)

# CORS configuration
origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API is running"}
