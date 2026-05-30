from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: str
class Token(BaseModel):
    access_token: str
    token_type: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class DeviceBase(BaseModel):
    name: Optional[str] = None
    model: Optional[str] = None
    os_version: Optional[str] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(BaseModel):
    battery_level: Optional[int] = None

class Device(DeviceBase):
    id: int
    device_token: str
    battery_level: int
    last_seen: datetime
    owner_id: int

    class Config:
        from_attributes = True

class CallLogBase(BaseModel):
    number: str
    type: int
    date: int
    duration: int
    name: Optional[str] = None

class CallLogCreate(CallLogBase):
    device_id: Optional[int] = None

class CallLog(CallLogBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True

class SmsMessageBase(BaseModel):
    address: str
    body: str
    date: int

class SmsMessageCreate(SmsMessageBase):
    device_id: Optional[int] = None

class SmsMessage(SmsMessageBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True

class AppUsageBase(BaseModel):
    app_name: str
    package_name: str
    duration: int
    date: int

class AppUsageCreate(AppUsageBase):
    device_id: Optional[int] = None

class AppUsage(AppUsageBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True

class WebActivityBase(BaseModel):
    url: str
    title: str
    visit_time: int

class WebActivityCreate(WebActivityBase):
    device_id: Optional[int] = None

class WebActivity(WebActivityBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True

class InstalledAppBase(BaseModel):
    app_name: str
    package_name: str
    install_date: int

class InstalledAppCreate(InstalledAppBase):
    device_id: Optional[int] = None

class InstalledApp(InstalledAppBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    package_name: str
    title: str
    text: str
    post_time: int

class NotificationCreate(NotificationBase):
    device_id: Optional[int] = None

class Notification(NotificationBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True

class LocationBase(BaseModel):
    latitude: str
    longitude: str
    timestamp: int

class LocationCreate(LocationBase):
    device_id: Optional[int] = None

class Location(LocationBase):
    id: int
    owner_id: int
    device_id: Optional[int] = None

    class Config:
        from_attributes = True
