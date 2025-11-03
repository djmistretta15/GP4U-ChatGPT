"""
Service layer for handling reviews.

Allows creation of reviews for bookings and listing reviews.  In a real
implementation, additional validation to ensure the booking belongs to
the user and that a review hasn't been submitted already would be
performed.
"""

from sqlalchemy.orm import Session

from backend.models.review import Review
from backend.models.booking import Booking


class ReviewService:
    """Service for reviews."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_reviews(self) -> list[Review]:
        return self.db.query(Review).all()

    def create_review(self, *, booking_id: int, rating: int, comment: str | None = None) -> Review:
        # Validate that the booking exists
        booking = self.db.query(Booking).get(booking_id)
        if not booking:
            raise ValueError("Invalid booking id")
        review = Review(booking_id=booking_id, rating=rating, comment=comment)
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review