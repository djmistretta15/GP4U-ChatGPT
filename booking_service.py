"""
Service layer for booking operations.

Handles creation and retrieval of bookings, including basic
availability checks.  Additional logic such as payment processing and
cancellation could be added here.
"""

from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from backend.models.booking import Booking
from backend.models.gpu import GPU
from backend.models.user import User


class BookingService:
    """Service for booking GPUs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_bookings(self) -> list[Booking]:
        return self.db.query(Booking).all()

    def create_booking(self, *, user_id: int, gpu_id: int, start_time: datetime, end_time: datetime) -> Booking:
        # Check that user and GPU exist
        user = self.db.query(User).get(user_id)
        gpu = self.db.query(GPU).get(gpu_id)
        if not user or not gpu:
            raise ValueError("Invalid user or GPU")
        # Check GPU availability in the specified time frame
        overlapping = (
            self.db.query(Booking)
            .filter(
                Booking.gpu_id == gpu_id,
                and_(
                    Booking.start_time < end_time,
                    Booking.end_time > start_time,
                ),
            )
            .first()
        )
        if overlapping:
            raise ValueError("GPU is already booked for the specified time range")
        # Create booking
        booking = Booking(
            user_id=user_id,
            gpu_id=gpu_id,
            start_time=start_time,
            end_time=end_time,
        )
        self.db.add(booking)
        self.db.commit()
        self.db.refresh(booking)
        return booking