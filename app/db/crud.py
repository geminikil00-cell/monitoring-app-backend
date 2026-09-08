from sqlalchemy.orm import Session
from . import models
from app.api.v1 import schemas
from app.core import security
import uuid
from sqlalchemy.sql import func

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = security.get_password_hash(user.password)
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

def get_device_by_id_and_owner(db: Session, device_id: int, owner_id: int):
    return db.query(models.Device).filter(models.Device.id == device_id, models.Device.owner_id == owner_id).first()

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
    return db.query(models.CallLog).filter(models.CallLog.owner_id == user_id).order_by(models.CallLog.date.desc()).offset(skip).limit(limit).all()

def get_call_logs_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.CallLog).filter(models.CallLog.device_id == device_id).order_by(models.CallLog.date.desc()).offset(skip).limit(limit).all()

def create_user_sms_message(db: Session, sms_message: schemas.SmsMessageCreate, user_id: int):
    db_sms_message = models.SmsMessage(**sms_message.dict(), owner_id=user_id)
    db.add(db_sms_message)
    db.commit()
    db.refresh(db_sms_message)
    return db_sms_message

def get_sms_messages_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SmsMessage).filter(models.SmsMessage.owner_id == user_id).order_by(models.SmsMessage.date.desc()).offset(skip).limit(limit).all()

def get_sms_messages_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.SmsMessage).filter(models.SmsMessage.device_id == device_id).order_by(models.SmsMessage.date.desc()).offset(skip).limit(limit).all()

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
    return db.query(models.AppUsage).filter(models.AppUsage.owner_id == user_id).order_by(models.AppUsage.date.desc()).offset(skip).limit(limit).all()

def get_app_usage_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.AppUsage).filter(models.AppUsage.device_id == device_id).order_by(models.AppUsage.date.desc()).offset(skip).limit(limit).all()

def create_user_web_activity(db: Session, web_activity: schemas.WebActivityCreate, user_id: int):
    db_web_activity = models.WebActivity(**web_activity.dict(), owner_id=user_id)
    db.add(db_web_activity)
    db.commit()
    db.refresh(db_web_activity)
    return db_web_activity

def get_web_activity_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WebActivity).filter(models.WebActivity.owner_id == user_id).order_by(models.WebActivity.visit_time.desc()).offset(skip).limit(limit).all()

def get_web_activity_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.WebActivity).filter(models.WebActivity.device_id == device_id).order_by(models.WebActivity.visit_time.desc()).offset(skip).limit(limit).all()

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
    return db.query(models.InstalledApp).filter(models.InstalledApp.owner_id == user_id).order_by(models.InstalledApp.install_date.desc()).offset(skip).limit(limit).all()

def get_installed_apps_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.InstalledApp).filter(models.InstalledApp.device_id == device_id).order_by(models.InstalledApp.install_date.desc()).offset(skip).limit(limit).all()

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

def create_command(db: Session, command: schemas.CommandCreate, user_id: int):
    db_command = models.Command(**command.dict(), owner_id=user_id)
    db.add(db_command)
    db.commit()
    db.refresh(db_command)
    return db_command

def get_pending_commands_by_device(db: Session, device_id: int):
    return db.query(models.Command).filter(models.Command.device_id == device_id, models.Command.status == "pending").all()

def update_command_status(db: Session, command_id: int, update: schemas.CommandStatusUpdate):
    db_cmd = db.query(models.Command).filter(models.Command.id == command_id).first()
    if db_cmd:
        db_cmd.status = update.status
        if update.result: db_cmd.result = update.result
        db.commit()
        db.refresh(db_cmd)
    return db_cmd

def create_media_file(db: Session, media: schemas.MediaFileCreate, user_id: int):
    db_media = models.MediaFile(**media.dict(), owner_id=user_id)
    db.add(db_media)
    db.commit()
    db.refresh(db_media)
    return db_media

def get_media_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 100, category: str = None, start_date: int = None, end_date: int = None):
    query = db.query(models.MediaFile).filter(models.MediaFile.device_id == device_id)
    if category:
        query = query.filter(models.MediaFile.category == category)
    if start_date is not None:
        query = query.filter(models.MediaFile.captured_at >= start_date)
    if end_date is not None:
        query = query.filter(models.MediaFile.captured_at <= end_date)
    return query.order_by(models.MediaFile.id.desc()).offset(skip).limit(limit).all()

def get_media_files_by_ids(db: Session, ids: list):
    return db.query(models.MediaFile).filter(models.MediaFile.id.in_(ids)).all()

def delete_media_files_by_ids(db: Session, ids: list) -> int:
    if not ids:
        return 0
    deleted = db.query(models.MediaFile).filter(models.MediaFile.id.in_(ids)).delete(synchronize_session=False)
    db.commit()
    return deleted

def get_media_ids_in_range(db: Session, device_id: int, start_date: int, end_date: int) -> list:
    files = db.query(models.MediaFile).filter(
        models.MediaFile.device_id == device_id,
        models.MediaFile.captured_at >= start_date,
        models.MediaFile.captured_at <= end_date
    ).all()
    return [{'id': f.id, 's3_key': f.s3_key} for f in files]

def get_unindexed_media(db: Session, owner_id: int, limit: int = 20):
    return (
        db.query(models.MediaFile)
        .filter(
            models.MediaFile.owner_id == owner_id,
            models.MediaFile.indexed_at.is_(None),
            models.MediaFile.index_attempts < 3,
            models.MediaFile.file_type.ilike("image/%"),
        )
        .order_by(models.MediaFile.id.asc())
        .limit(limit)
        .all()
    )


def rebuild_search_text(db: Session, media: models.MediaFile) -> str:
    parts = [media.caption_en or "", media.caption_ar or ""]
    tags = db.query(models.MediaTag).filter(models.MediaTag.media_id == media.id).all()
    for t in tags:
        if t.tag_en:
            parts.append(t.tag_en)
        if t.tag_ar:
            parts.append(t.tag_ar)
    person_ids = [
        row[0]
        for row in db.query(models.Face.person_id)
        .filter(models.Face.media_id == media.id, models.Face.person_id.isnot(None))
        .distinct()
        .all()
    ]
    if person_ids:
        for person in db.query(models.Person).filter(models.Person.id.in_(person_ids)).all():
            if person.name:
                parts.append(person.name)
    media.search_text = " ".join(p for p in parts if p)
    return media.search_text


def search_media(db: Session, device_id: int, q: str = None, person_id: int = None, skip: int = 0, limit: int = 100):
    query = db.query(models.MediaFile).filter(
        models.MediaFile.device_id == device_id,
        models.MediaFile.indexed_at.isnot(None),
    )
    if person_id is not None:
        query = query.join(models.Face, models.Face.media_id == models.MediaFile.id).filter(
            models.Face.person_id == person_id
        )
    if q and q.strip():
        for word in q.strip().split():
            query = query.filter(models.MediaFile.search_text.ilike(f"%{word}%"))
    return (
        query.distinct()
        .order_by(models.MediaFile.captured_at.desc(), models.MediaFile.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_people_for_device(db: Session, device_id: int):
    return db.query(models.Person).filter(models.Person.device_id == device_id).order_by(models.Person.id.asc()).all()


def person_photo_count(db: Session, person_id: int) -> int:
    return (
        db.query(models.Face.media_id)
        .filter(models.Face.person_id == person_id)
        .distinct()
        .count()
    )


def get_person_cover_media(db: Session, person: models.Person):
    face = None
    if person.cover_face_id:
        face = db.query(models.Face).filter(models.Face.id == person.cover_face_id).first()
    if face is None:
        face = db.query(models.Face).filter(models.Face.person_id == person.id).first()
    if face is None:
        return None
    return db.query(models.MediaFile).filter(models.MediaFile.id == face.media_id).first()


def get_face_embeddings_for_device(db: Session, device_id: int):
    return (
        db.query(models.Face)
        .join(models.Person, models.Face.person_id == models.Person.id)
        .filter(models.Person.device_id == device_id, models.Face.embedding.isnot(None))
        .all()
    )


def rename_person(db: Session, person: models.Person, name: str):
    person.name = name
    media_ids = [
        row[0]
        for row in db.query(models.Face.media_id).filter(models.Face.person_id == person.id).distinct().all()
    ]
    for media in db.query(models.MediaFile).filter(models.MediaFile.id.in_(media_ids)).all() if media_ids else []:
        rebuild_search_text(db, media)
    db.commit()
    db.refresh(person)
    return person


def apply_media_index(db: Session, media: models.MediaFile, payload: schemas.MediaIndexRequest):
    if payload.error:
        media.index_attempts = (media.index_attempts or 0) + 1
        media.index_error = payload.error
        db.commit()
        db.refresh(media)
        return media

    db.query(models.MediaTag).filter(models.MediaTag.media_id == media.id).delete(synchronize_session=False)
    db.query(models.Face).filter(models.Face.media_id == media.id).delete(synchronize_session=False)

    media.caption_en = payload.caption_en or ""
    media.caption_ar = payload.caption_ar or ""
    media.index_error = None
    media.indexed_at = func.now()

    for tag in payload.tags:
        db.add(
            models.MediaTag(
                media_id=media.id,
                tag_en=tag.tag_en,
                tag_ar=tag.tag_ar or "",
                score=tag.score or 0,
            )
        )

    cluster_people = {}
    import base64

    for face in payload.faces:
        person = None
        if face.person_id:
            person = (
                db.query(models.Person)
                .filter(
                    models.Person.id == face.person_id,
                    models.Person.device_id == media.device_id,
                    models.Person.owner_id == media.owner_id,
                )
                .first()
            )
        if person is None and face.cluster_key:
            person = cluster_people.get(face.cluster_key)
        if person is None:
            person = models.Person(device_id=media.device_id, owner_id=media.owner_id, name=None)
            db.add(person)
            db.flush()
            if face.cluster_key:
                cluster_people[face.cluster_key] = person
        embedding = None
        if face.embedding_b64:
            embedding = base64.b64decode(face.embedding_b64)
        row = models.Face(
            media_id=media.id,
            person_id=person.id,
            bbox_x=face.bbox_x,
            bbox_y=face.bbox_y,
            bbox_w=face.bbox_w,
            bbox_h=face.bbox_h,
            embedding=embedding,
            quality=face.quality or 0,
        )
        db.add(row)
        db.flush()
        if person.cover_face_id is None:
            person.cover_face_id = row.id

    db.flush()
    rebuild_search_text(db, media)
    db.commit()
    db.refresh(media)
    return media


def delete_media_files_in_range(db: Session, device_id: int, start_date: int, end_date: int) -> int:
    deleted = db.query(models.MediaFile).filter(
        models.MediaFile.device_id == device_id,
        models.MediaFile.captured_at >= start_date,
        models.MediaFile.captured_at <= end_date
    ).delete(synchronize_session=False)
    db.commit()
    return deleted

def create_user_keylog(db: Session, keylog: schemas.KeylogCreate, user_id: int):
    db_item = models.Keylog(**keylog.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_keylogs_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 1000, start_date: int = None, end_date: int = None):
    q = db.query(models.Keylog).filter(models.Keylog.device_id == device_id)
    if start_date is not None:
        q = q.filter(models.Keylog.timestamp >= start_date)
    if end_date is not None:
        q = q.filter(models.Keylog.timestamp <= end_date)
    return q.order_by(models.Keylog.timestamp.desc()).offset(skip).limit(limit).all()

def get_keylogs_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 1000, start_date: int = None, end_date: int = None):
    q = db.query(models.Keylog).filter(models.Keylog.owner_id == user_id)
    if start_date is not None:
        q = q.filter(models.Keylog.timestamp >= start_date)
    if end_date is not None:
        q = q.filter(models.Keylog.timestamp <= end_date)
    return q.order_by(models.Keylog.timestamp.desc()).offset(skip).limit(limit).all()

def create_chat_message(db: Session, chat_message: schemas.ChatMessageCreate, user_id: int):
    db_item = models.ChatMessage(**chat_message.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def get_chat_messages_by_device(db: Session, device_id: int, skip: int = 0, limit: int = 1000, start_date: int = None, end_date: int = None, package_name: str = None):
    q = db.query(models.ChatMessage).filter(models.ChatMessage.device_id == device_id)
    if start_date is not None:
        q = q.filter(models.ChatMessage.timestamp >= start_date)
    if end_date is not None:
        q = q.filter(models.ChatMessage.timestamp <= end_date)
    if package_name:
        q = q.filter(models.ChatMessage.package_name == package_name)
    return q.order_by(models.ChatMessage.timestamp.desc()).offset(skip).limit(limit).all()

def get_chat_messages_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 1000, start_date: int = None, end_date: int = None, package_name: str = None):
    q = db.query(models.ChatMessage).filter(models.ChatMessage.owner_id == user_id)
    if start_date is not None:
        q = q.filter(models.ChatMessage.timestamp >= start_date)
    if end_date is not None:
        q = q.filter(models.ChatMessage.timestamp <= end_date)
    if package_name:
        q = q.filter(models.ChatMessage.package_name == package_name)
    return q.order_by(models.ChatMessage.timestamp.desc()).offset(skip).limit(limit).all()

