from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Settings (Supabase / PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # JWT Settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200

    # S3 Storage Settings (e.g., Cloudflare R2 or AWS S3)
    S3_BUCKET: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_REGION: str = "auto"
    S3_ENDPOINT: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
