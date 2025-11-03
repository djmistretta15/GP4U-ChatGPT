"""
Service layer for sending notifications.

Creates notification records in the database.  This service can be
extended to integrate with email, push or SMS providers.
"""

from sqlalchemy.orm import Session

from backend.models.notification import Notification
from backend.models.user import User


class NotificationService:
    """Service for user notifications."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def send_notification(self, *, user_id: int, message: str, type: str = "in_app") -> Notification:
        # Validate user
        user = self.db.query(User).get(user_id)
        if not user:
            raise ValueError("Invalid user id")
        notification = Notification(user_id=user_id, message=message, type=type, read=False)
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        return notification

    def list_notifications(self, user_id: int) -> list[Notification]:
        """List notifications for a user."""
        return self.db.query(Notification).filter(Notification.user_id == user_id).all()

    def mark_as_read(self, notification_id: int) -> Notification:
        """Mark a notification as read."""
        notification = self.db.query(Notification).get(notification_id)
        if not notification:
            raise ValueError("Invalid notification id")
        notification.read = True
        self.db.commit()
        self.db.refresh(notification)
        return notification