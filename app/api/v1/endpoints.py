from fastapi import APIRouter, Depends, HTTPException
from typing import List
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import schemas
from app.db import crud, models
from app.db.database import get_db
from app.core import security
from app.core.auth import get_current_user, get_current_device
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/users/me", response_model=schemas.User)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

# Device Endpoints
@router.post("/devices/register", response_model=schemas.Device)
def register_device(
    device: schemas.DeviceCreate, 
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Check if a device with the same name/model already exists for this user
    existing_devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
    for d in existing_devices:
        if d.name == device.name and d.model == device.model:
            return d
    
    return crud.create_device(db=db, device=device, user_id=current_user.id)

@router.get("/devices/", response_model=List[schemas.Device])
def read_devices(
    db: Session = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    return crud.get_devices_by_user(db=db, user_id=current_user.id)

@router.patch("/devices/heartbeat", response_model=schemas.Device)
def device_heartbeat(
    battery_level: int, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    return crud.update_device_heartbeat(db=db, device_id=current_device.id, battery_level=battery_level)

@router.post("/users/me/call_logs/", response_model=schemas.CallLog)
def create_call_log_for_user(
    call_log: schemas.CallLogCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_call_log(db=db, call_log=call_log, user_id=current_user.id)

@router.get("/users/me/call_logs/", response_model=List[schemas.CallLog])
def read_call_logs_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    call_logs = crud.get_call_logs_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return call_logs

@router.post("/users/me/sms_messages/", response_model=schemas.SmsMessage)
def create_sms_message_for_user(
    sms_message: schemas.SmsMessageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_sms_message(db=db, sms_message=sms_message, user_id=current_user.id)

@router.get("/users/me/sms_messages/", response_model=List[schemas.SmsMessage])
def read_sms_messages_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    sms_messages = crud.get_sms_messages_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)
    return sms_messages

@router.post("/users/me/app_usage/", response_model=schemas.AppUsage)
def create_app_usage_for_user(
    app_usage: schemas.AppUsageCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_app_usage(db=db, app_usage=app_usage, user_id=current_user.id)

@router.get("/users/me/app_usage/", response_model=List[schemas.AppUsage])
def read_app_usage_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_app_usage_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/users/me/web_activity/", response_model=schemas.WebActivity)
def create_web_activity_for_user(
    web_activity: schemas.WebActivityCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_web_activity(db=db, web_activity=web_activity, user_id=current_user.id)

@router.get("/users/me/web_activity/", response_model=List[schemas.WebActivity])
def read_web_activity_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_web_activity_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/users/me/installed_apps/", response_model=schemas.InstalledApp)
def create_installed_app_for_user(
    installed_app: schemas.InstalledAppCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_installed_app(db=db, installed_app=installed_app, user_id=current_user.id)

@router.get("/users/me/installed_apps/", response_model=List[schemas.InstalledApp])
def read_installed_apps_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_installed_apps_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/users/me/notifications/", response_model=schemas.Notification)
def create_notification_for_user(
    notification: schemas.NotificationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_notification(db=db, notification=notification, user_id=current_user.id)

@router.get("/users/me/notifications/", response_model=List[schemas.Notification])
def read_notifications_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_notifications_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.post("/users/me/locations/", response_model=schemas.Location)
def create_location_for_user(
    location: schemas.LocationCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.create_user_location(db=db, location=location, user_id=current_user.id)

@router.get("/users/me/locations/", response_model=List[schemas.Location])
def read_locations_for_user(
    skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    return crud.get_locations_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

# Command Endpoints
@router.post("/devices/{device_id}/commands/", response_model=schemas.Command)
def create_command(
    device_id: int,
    command: schemas.CommandCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Verify device belongs to user
    devices = crud.get_devices_by_user(db, current_user.id)
    if not any(d.id == device_id for d in devices):
        raise HTTPException(status_code=403, detail="Device not found or access denied")
    return crud.create_device_command(db=db, command=command, device_id=device_id)

@router.get("/devices/me/commands/", response_model=List[schemas.Command])
def get_commands_for_device(
    db: Session = Depends(get_db),
    current_device: models.Device = Depends(get_current_device)
):
    commands = crud.get_pending_commands(db, current_device.id)
    # Mark as SENT immediately
    for cmd in commands:
        crud.update_command_status(db, cmd.id, "SENT")
    return commands

@router.patch("/commands/{command_id}/status")
def update_command_status(
    command_id: int,
    status: str,
    db: Session = Depends(get_db),
    current_device: models.Device = Depends(get_current_device)
):
    return crud.update_command_status(db, command_id, status)

# MediaFile Endpoints
@router.post("/devices/me/media/", response_model=schemas.MediaFile)
def upload_media_metadata(
    media_file: schemas.MediaFileCreate,
    db: Session = Depends(get_db),
    current_device: models.Device = Depends(get_current_device)
):
    return crud.create_device_media_file(db=db, media_file=media_file, device_id=current_device.id)

@router.get("/devices/{device_id}/media/", response_model=List[schemas.MediaFile])
def get_device_media(
    device_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    devices = crud.get_devices_by_user(db, current_user.id)
    if not any(d.id == device_id for d in devices):
        raise HTTPException(status_code=403, detail="Device not found or access denied")
    return crud.get_media_files_by_device(db, device_id, skip, limit)

# Device Telemetry Endpoints
@router.post("/devices/me/call_logs/", response_model=schemas.CallLog)
def create_call_log_for_device(
    call_log: schemas.CallLogCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    call_log.device_id = current_device.id
    return crud.create_user_call_log(db=db, call_log=call_log, user_id=current_device.owner_id)

@router.post("/devices/me/sms_messages/", response_model=schemas.SmsMessage)
def create_sms_message_for_device(
    sms_message: schemas.SmsMessageCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    sms_message.device_id = current_device.id
    return crud.create_user_sms_message(db=db, sms_message=sms_message, user_id=current_device.owner_id)

@router.post("/devices/me/app_usage/", response_model=schemas.AppUsage)
def create_app_usage_for_device(
    app_usage: schemas.AppUsageCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    app_usage.device_id = current_device.id
    return crud.create_user_app_usage(db=db, app_usage=app_usage, user_id=current_device.owner_id)

@router.post("/devices/me/web_activity/", response_model=schemas.WebActivity)
def create_web_activity_for_device(
    web_activity: schemas.WebActivityCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    web_activity.device_id = current_device.id
    return crud.create_user_web_activity(db=db, web_activity=web_activity, user_id=current_device.owner_id)

@router.post("/devices/me/installed_apps/", response_model=schemas.InstalledApp)
def create_installed_app_for_device(
    installed_app: schemas.InstalledAppCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    installed_app.device_id = current_device.id
    return crud.create_user_installed_app(db=db, installed_app=installed_app, user_id=current_device.owner_id)

@router.post("/devices/me/notifications/", response_model=schemas.Notification)
def create_notification_for_device(
    notification: schemas.NotificationCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    notification.device_id = current_device.id
    return crud.create_user_notification(db=db, notification=notification, user_id=current_device.owner_id)

@router.post("/devices/me/locations/", response_model=schemas.Location)
def create_location_for_device(
    location: schemas.LocationCreate, 
    db: Session = Depends(get_db), 
    current_device: models.Device = Depends(get_current_device)
):
    location.device_id = current_device.id
    return crud.create_user_location(db=db, location=location, user_id=current_device.owner_id)
