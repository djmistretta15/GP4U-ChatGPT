"""
Service layer for payment operations.

Creates payment records for bookings.  In a real system, this service
would integrate with a payment processor (e.g. Stripe) to capture
payments, update status based on processor responses and handle
refunds.
"""

from sqlalchemy.orm import Session

from backend.models.payment import Payment
from backend.models.booking import Booking


class PaymentService:
    """Service for processing payments."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_payment(self, *, booking_id: int, amount: float) -> Payment:
        # Ensure booking exists
        booking = self.db.query(Booking).get(booking_id)
        if not booking:
            raise ValueError("Invalid booking id")
        payment = Payment(booking_id=booking_id, amount=amount, status="completed")
        self.db.add(payment)
        self.db.commit()
        self.db.refresh(payment)
        return payment