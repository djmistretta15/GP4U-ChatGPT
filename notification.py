"""
Pydantic schemas for notifications.
"""

from datetime import datetime
from pydantic import BaseModel


class NotificationBase(BaseModel):
    user_id: int
    message: str
    type: str | None = None


class NotificationCreate(NotificationBase):
    pass


class NotificationRead(NotificationBase):
    id: int
    read: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True