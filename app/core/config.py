from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Settings (Supabase / PostgreSQL)
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    # JWT Settings
    SECRET_KEY: str = "164388c2ecedd0c69d0b60682bc6c59558e5dc15fe47b8066e624a35a532d373"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

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
