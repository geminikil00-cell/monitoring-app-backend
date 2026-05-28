import sys
import os

# Add the current directory to sys.path to allow importing from 'app'
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import crud, models, schemas
from app.core import security

def create_admin_user(email, password):
    db = SessionLocal()
    try:
        db_user = crud.get_user_by_email(db, email=email)
        if db_user:
            print(f"User {email} already exists.")
            return
        
        user_in = schemas.UserCreate(email=email, password=password, full_name="Admin User")
        crud.create_user(db=db, user=user_in)
        print(f"User {email} created successfully!")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password>")
    else:
        create_admin_user(sys.argv[1], sys.argv[2])
