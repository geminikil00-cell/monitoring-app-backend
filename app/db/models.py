from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
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

class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    device_token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String)
    model = Column(String)
    os_version = Column(String)
    battery_level = Column(Integer, default=100)
    last_seen = Column(DateTime(timezone=True), onupdate=func.now(), default=func.now())
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="devices")
    call_logs = relationship("CallLog", back_populates="device")
    sms_messages = relationship("SmsMessage", back_populates="device")
    app_usage = relationship("AppUsage", back_populates="device")
    web_activity = relationship("WebActivity", back_populates="device")
    locations = relationship("Location", back_populates="device")

class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(String, index=True)
    type = Column(Integer)
    date = Column(Integer)
    duration = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="call_logs")
    device = relationship("Device", back_populates="call_logs")

class SmsMessage(Base):
    __tablename__ = "sms_messages"

    id = Column(Integer, primary_key=True, index=True)
    address = Column(String, index=True)
    body = Column(String)
    date = Column(Integer)
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
    date = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="app_usage")
    device = relationship("Device", back_populates="app_usage")

class WebActivity(Base):
    __tablename__ = "web_activity"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    title = Column(String)
    visit_time = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="web_activity")
    device = relationship("Device", back_populates="web_activity")

class InstalledApp(Base):
    __tablename__ = "installed_apps"

    id = Column(Integer, primary_key=True, index=True)
    app_name = Column(String, index=True)
    package_name = Column(String)
    install_date = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User")
    device = relationship("Device")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    package_name = Column(String, index=True)
    title = Column(String)
    text = Column(String)
    post_time = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User")
    device = relationship("Device")

class Location(Base):
    __tablename__ = "locations"

    id = Column(Integer, primary_key=True, index=True)
    latitude = Column(String)
    longitude = Column(String)
    timestamp = Column(Integer)
    owner_id = Column(Integer, ForeignKey("users.id"))
    device_id = Column(Integer, ForeignKey("devices.id"))

    owner = relationship("User", back_populates="locations")
    device = relationship("Device", back_populates="locations")
