from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

_is_postgres = settings.DATABASE_URL.startswith("postgresql")
_engine_kwargs = {"pool_pre_ping": True}
if _is_postgres:
    _engine_kwargs.update(
        pool_size=20,
        max_overflow=30,
        pool_recycle=3600,
        connect_args={"connect_timeout": 10},
    )

engine = create_engine(settings.DATABASE_URL, **_engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
