from sqlalchemy.orm import Session
from . import models
from app.api.v1 import schemas
from passlib.context import CryptContext
import uuid
from sqlalchemy.sql import func

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Device CRUD
def create_device(db: Session, device: schemas.DeviceCreate, user_id: int):
    device_token = str(uuid.uuid4())
    db_device = models.Device(**device.dict(), device_token=device_token, owner_id=user_id)
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def get_device_by_token(db: Session, token: str):
    return db.query(models.Device).filter(models.Device.device_token == token).first()

def get_devices_by_user(db: Session, user_id: int):
    return db.query(models.Device).filter(models.Device.owner_id == user_id).all()

def update_device_heartbeat(db: Session, device_id: int, battery_level: int):
    db_device = db.query(models.Device).filter(models.Device.id == device_id).first()
    if db_device:
        db_device.battery_level = battery_level
        db_device.last_seen = func.now()
        db.commit()
        db.refresh(db_device)
    return db_device

def create_user_call_log(db: Session, call_log: schemas.CallLogCreate, user_id: int):
    db_call_log = models.CallLog(**call_log.dict(), owner_id=user_id)
    db.add(db_call_log)
    db.commit()
    db.refresh(db_call_log)
    return db_call_log

def get_call_logs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.CallLog).filter(models.CallLog.owner_id == user_id).offset(skip).limit(limit).all()

def get_call_logs_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.CallLog).filter(models.CallLog.device_id == device_id).offset(skip).limit(limit).all()

def create_user_sms_message(db: Session, sms_message: schemas.SmsMessageCreate, user_id: int):
    db_sms_message = models.SmsMessage(**sms_message.dict(), owner_id=user_id)
    db.add(db_sms_message)
    db.commit()
    db.refresh(db_sms_message)
    return db_sms_message

def get_sms_messages_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SmsMessage).filter(models.SmsMessage.owner_id == user_id).offset(skip).limit(limit).all()

def get_sms_messages_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SmsMessage).filter(models.SmsMessage.device_id == device_id).offset(skip).limit(limit).all()

def create_user_app_usage(db: Session, app_usage: schemas.AppUsageCreate, user_id: int):
    midnight = (app_usage.date // 86400000) * 86400000

    db_app_usage = db.query(models.AppUsage).filter(
        models.AppUsage.owner_id == user_id,
        models.AppUsage.device_id == app_usage.device_id,
        models.AppUsage.package_name == app_usage.package_name,
        models.AppUsage.date >= midnight,
        models.AppUsage.date < midnight + 86400000
    ).first()

    if db_app_usage:
        if app_usage.duration > db_app_usage.duration:
            db_app_usage.duration = app_usage.duration
            db_app_usage.date = app_usage.date
    else:
        db_app_usage = models.AppUsage(**app_usage.dict(), owner_id=user_id)
        db.add(db_app_usage)

    db.commit()
    db.refresh(db_app_usage)
    return db_app_usage

def get_app_usage_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AppUsage).filter(models.AppUsage.owner_id == user_id).offset(skip).limit(limit).all()

def get_app_usage_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AppUsage).filter(models.AppUsage.device_id == device_id).offset(skip).limit(limit).all()

def create_user_web_activity(db: Session, web_activity: schemas.WebActivityCreate, user_id: int):
    db_web_activity = models.WebActivity(**web_activity.dict(), owner_id=user_id)
    db.add(db_web_activity)
    db.commit()
    db.refresh(db_web_activity)
    return db_web_activity

def get_web_activity_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WebActivity).filter(models.WebActivity.owner_id == user_id).offset(skip).limit(limit).all()

def get_web_activity_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WebActivity).filter(models.WebActivity.device_id == device_id).offset(skip).limit(limit).all()

def create_user_installed_app(db: Session, installed_app: schemas.InstalledAppCreate, user_id: int):
    db_installed_app = db.query(models.InstalledApp).filter(
        models.InstalledApp.owner_id == user_id,
        models.InstalledApp.device_id == installed_app.device_id,
        models.InstalledApp.package_name == installed_app.package_name
    ).first()

    if db_installed_app:
        db_installed_app.app_name = installed_app.app_name
        db_installed_app.install_date = installed_app.install_date
    else:
        db_installed_app = models.InstalledApp(**installed_app.dict(), owner_id=user_id)
        db.add(db_installed_app)

    db.commit()
    db.refresh(db_installed_app)
    return db_installed_app

def get_installed_apps_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.InstalledApp).filter(models.InstalledApp.owner_id == user_id).offset(skip).limit(limit).all()

def get_installed_apps_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.InstalledApp).filter(models.InstalledApp.device_id == device_id).offset(skip).limit(limit).all()

def create_user_notification(db: Session, notification: schemas.NotificationCreate, user_id: int):
    db_notification = models.Notification(**notification.dict(), owner_id=user_id)
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def get_notifications_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).filter(models.Notification.owner_id == user_id).order_by(models.Notification.post_time.desc()).offset(skip).limit(limit).all()

def get_notifications_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).filter(models.Notification.device_id == device_id).order_by(models.Notification.post_time.desc()).offset(skip).limit(limit).all()

def create_user_location(db: Session, location: schemas.LocationCreate, user_id: int):
    db_location = models.Location(**location.dict(), owner_id=user_id)
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

def get_locations_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Location).filter(models.Location.owner_id == user_id).order_by(models.Location.timestamp.desc()).offset(skip).limit(limit).all()

def get_locations_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Location).filter(models.Location.device_id == device_id).order_by(models.Location.timestamp.desc()).offset(skip).limit(limit).all()
