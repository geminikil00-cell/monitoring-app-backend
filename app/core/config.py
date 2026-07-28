from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Settings (Supabase PostgreSQL — use pooler port 6543 for Docker/IPv4 compat)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:6543/postgres"

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # CORS Settings
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,https://monitoring-app-frontend.geminikil00.workers.dev,https://monitoring.joclass.com"

    # S3 Storage Settings (e.g., Cloudflare R2 or AWS S3)
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "auto"
    S3_ENDPOINT: Optional[str] = None

    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "parental-media"
    R2_ENDPOINT_URL: str = ""

    model_config = {"env_file": ".env", "case_sensitive": True}

settings = Settings()
