import random
import time
from app.db import crud, models
from app.db.database import SessionLocal
from app.api.v1 import schemas

def seed():
    db = SessionLocal()
    
    # Get or create admin user
    email = "admin@example.com"
    user = crud.get_user_by_email(db, email=email)
    if not user:
        user_in = schemas.UserCreate(email=email, password="password123")
        user = crud.create_user(db=db, user=user_in)
        print(f"Created user: {email}")
    
    user_id = user.id

    # Seed Call Logs
    numbers = ["+15550101", "+15550202", "+15550303", "+15550404"]
    for i in range(10):
        call_log = schemas.CallLogCreate(
            number=random.choice(numbers),
            type=random.randint(1, 3),
            date=int((time.time() - random.randint(0, 86400 * 7)) * 1000),
            duration=random.randint(10, 300)
        )
        crud.create_user_call_log(db, call_log, user_id)
    
    # Seed SMS
    messages = [
        "Hey, are you home yet?",
        "Don't forget to finish your homework.",
        "Can we get pizza for dinner?",
        "I'll be a bit late, wait for me.",
        "Check out this cool game!"
    ]
    for i in range(8):
        sms = schemas.SmsMessageCreate(
            address=random.choice(numbers),
            body=random.choice(messages),
            date=int((time.time() - random.randint(0, 86400 * 3)) * 1000)
        )
        crud.create_user_sms_message(db, sms, user_id)

    # Seed App Usage
    apps = [
        ("Instagram", "com.instagram.android"),
        ("TikTok", "com.zhiliaoapp.musically"),
        ("WhatsApp", "com.whatsapp"),
        ("YouTube", "com.google.android.youtube"),
        ("Snapchat", "com.snapchat.android")
    ]
    for app_name, pkg in apps:
        usage = schemas.AppUsageCreate(
            app_name=app_name,
            package_name=pkg,
            duration=random.randint(600, 7200),
            date=int(time.time() * 1000)
        )
        crud.create_user_app_usage(db, usage, user_id)

    # Seed Web Activity
    sites = [
        ("Google", "https://www.google.com"),
        ("Wikipedia", "https://en.wikipedia.org"),
        ("Reddit", "https://www.reddit.com"),
        ("GitHub", "https://github.com"),
        ("Stack Overflow", "https://stackoverflow.com")
    ]
    for title, url in sites:
        web = schemas.WebActivityCreate(
            url=url,
            title=title,
            visit_time=int((time.time() - random.randint(0, 86400)) * 1000)
        )
        crud.create_user_web_activity(db, web, user_id)

    # Seed Locations
    for i in range(5):
        loc = schemas.LocationCreate(
            latitude=str(37.7749 + random.uniform(-0.01, 0.01)),
            longitude=str(-122.4194 + random.uniform(-0.01, 0.01)),
            timestamp=int((time.time() - (i * 3600)) * 1000)
        )
        crud.create_user_location(db, loc, user_id)

    print("Successfully seeded database with fancy data!")
    db.close()

if __name__ == "__main__":
    seed()
