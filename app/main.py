import os
import time
import pathlib
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
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

frontend_dir = static_dir / "frontend"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir / "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(request: Request, full_path: str):
        if request.url.path.startswith("/api/"):
            return JSONResponse({"detail": "Not Found"}, status_code=404)
        file_path = frontend_dir / full_path
        if full_path and file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path), headers={"Cache-Control": "no-transform"})
        return FileResponse(str(frontend_dir / "index.html"), headers={"Cache-Control": "no-transform"})
else:
    @app.get("/")
    def read_root():
        return {"status": "API is running"}

@app.on_event("startup")
def startup_db():
    max_retries = 5
    for attempt in range(1, max_retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            from sqlalchemy import text
            with engine.begin() as conn:
                migrations = [
                    "ALTER TABLE commands ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)",
                    "ALTER TABLE commands ADD COLUMN IF NOT EXISTS result VARCHAR",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS category VARCHAR",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS file_path VARCHAR",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS size INTEGER DEFAULT 0",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS thumbnail_key VARCHAR",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS owner_id INTEGER REFERENCES users(id)",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS created_at TIMESTAMPTZ DEFAULT NOW()",
                    "ALTER TABLE media_files ADD COLUMN IF NOT EXISTS captured_at BIGINT DEFAULT 0",
                ]
                for m in migrations:
                    try:
                        conn.execute(text(m))
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
