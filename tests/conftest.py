import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ["SECRET_KEY"] = "test-secret-key-not-for-prod"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["CORS_ORIGINS"] = "http://test"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.db import models
from app.main import app
from app.api.v1 import schemas
from app.db import crud


engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db):
    def _override():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = _override
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture
def user_a(db):
    return crud.create_user(db, schemas.UserCreate(email="a@test.com", password="pw-a"))


@pytest.fixture
def user_b(db):
    return crud.create_user(db, schemas.UserCreate(email="b@test.com", password="pw-b"))


@pytest.fixture
def device_a(db, user_a):
    return crud.create_device(db, schemas.DeviceCreate(name="Phone A", model="SM-A"), user_id=user_a.id)


@pytest.fixture
def device_b(db, user_b):
    return crud.create_device(db, schemas.DeviceCreate(name="Phone B", model="SM-B"), user_id=user_b.id)


def token_for(client: TestClient, email: str, password: str) -> str:
    r = client.post("/api/v1/token", data={"username": email, "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


@pytest.fixture
def headers_a(client, user_a):
    t = token_for(client, "a@test.com", "pw-a")
    return {"Authorization": f"Bearer {t}"}


@pytest.fixture
def headers_b(client, user_b):
    t = token_for(client, "b@test.com", "pw-b")
    return {"Authorization": f"Bearer {t}"}


def add_media(db, device, *, file_name="pic.jpg", file_type="image/jpeg"):
    return crud.create_media_file(
        db,
        schemas.MediaFileCreate(
            s3_key=f"{device.id}/{file_name}",
            file_type=file_type,
            file_name=file_name,
            thumbnail_key=f"{device.id}/thumbs/{file_name}",
            device_id=device.id,
        ),
        user_id=device.owner_id,
    )
