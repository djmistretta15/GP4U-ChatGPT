"""
Service layer for handling disputes.

Allows users to create disputes for bookings and lists existing disputes.
In a real implementation additional logic to restrict who can create
disputes and to handle dispute resolution would be included.
"""

from sqlalchemy.orm import Session

from backend.models.dispute import Dispute
from backend.models.booking import Booking


class DisputeService:
    """Service for disputes."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_disputes(self) -> list[Dispute]:
        return self.db.query(Dispute).all()

    def create_dispute(self, *, booking_id: int, description: str) -> Dispute:
        # Validate booking
        booking = self.db.query(Booking).get(booking_id)
        if not booking:
            raise ValueError("Invalid booking id")
        dispute = Dispute(booking_id=booking_id, description=description, status="open")
        self.db.add(dispute)
        self.db.commit()
        self.db.refresh(dispute)
        return dispute