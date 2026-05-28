from app.db import crud, models
from app.db.database import SessionLocal, engine
from app.api.v1 import schemas

# Create tables
models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
user_in = schemas.UserCreate(email="admin@example.com", password="password123")
db_user = crud.get_user_by_email(db, email=user_in.email)
if not db_user:
    crud.create_user(db=db, user=user_in)
    print("User created: admin@example.com / password123")
else:
    print("User already exists")
db.close()
