import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import Base, engine
from app.db import models
from app.api.v1 import endpoints

# Note: In production, migrations should be handled by Alembic
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parental Control API",
    description="API for monitoring and controlling child devices.",
    version="0.1.0"
)

# CORS configuration
raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
origins = [origin.strip() for origin in raw_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API is running"}
