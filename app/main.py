import os
import time
import pathlib
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import Base, engine
from app.db import models
from app.api.v1 import endpoints
from app.core.config import settings

app = FastAPI(
    title="Parental Control API",
    description="API for monitoring and controlling child devices.",
    version="0.1.0"
)

CORS_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
static_dir = BASE_DIR / "static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

app.include_router(endpoints.router, prefix="/api/v1")

@app.on_event("startup")
def startup_db():
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            from sqlalchemy import text
            with engine.begin() as conn:
                try:
                    conn.execute(text("ALTER TABLE commands ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE commands ADD COLUMN IF NOT EXISTS result VARCHAR"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE media_files ADD COLUMN IF NOT EXISTS category VARCHAR"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE media_files ADD COLUMN IF NOT EXISTS file_path VARCHAR"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE media_files ADD COLUMN IF NOT EXISTS size INTEGER DEFAULT 0"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE media_files ADD COLUMN IF NOT EXISTS thumbnail_key VARCHAR"))
                except Exception:
                    pass
                try:
                    conn.execute(text("ALTER TABLE media_files ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)"))
                except Exception:
                    pass
            print(f"Database ready (attempt {attempt})")
            break
        except Exception as e:
            print(f"Database connection failed (attempt {attempt}/{max_retries}): {e}")
            if attempt < max_retries:
                time.sleep(5)
            else:
                print("WARNING: Could not connect to database after retries, API endpoints requiring DB will return 500")

@app.get("/")
def read_root():
    return {"status": "API is running"}
