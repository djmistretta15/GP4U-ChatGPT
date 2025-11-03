"""
Fairness service for GPU owner ranking.

This service computes a simple fairness score for each GPU owner
based on the average review ratings of their bookings and the ratio of
disputes to bookings.  Owners with high ratings and low dispute rates
receive higher scores.  The scoring algorithm can be refined as the
business rules evolve.
"""

from __future__ import annotations

from typing import List, Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.gpu import GPU
from backend.models.user import User
from backend.models.booking import Booking
from backend.models.review import Review
from backend.models.dispute import Dispute


class FairnessService:
    """Service to compute fairness scores for GPU owners."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def compute_scores(self) -> List[Dict[str, object]]:
        """Return fairness scores for all users who own GPUs.

        The returned list of dictionaries contains the owner ID,
        email and computed fairness score.  Scores are sorted
        descending, so higher scores appear first.
        """
        results: List[Dict[str, object]] = []
        # Find all users with at least one GPU
        owners = (
            self.db.query(User)
            .join(GPU, User.id == GPU.owner_id)
            .distinct(User.id)
            .all()
        )
        for owner in owners:
            # Gather bookings for this owner's GPUs
            bookings = (
                self.db.query(Booking)
                .join(GPU, Booking.gpu_id == GPU.id)
                .filter(GPU.owner_id == owner.id)
                .all()
            )
            total_bookings = len(bookings)
            # Count disputes across these bookings
            disputes_count = 0
            reviews_ratings = []
            for booking in bookings:
                disputes_count += len(booking.disputes)
                for review in booking.reviews:
                    reviews_ratings.append(review.rating)
            avg_rating = sum(reviews_ratings) / len(reviews_ratings) if reviews_ratings else 0.0
            dispute_rate = disputes_count / total_bookings if total_bookings > 0 else 0.0
            # Compute score: base on rating (0‑5) minus dispute penalty scaled to the same range
            score = avg_rating - dispute_rate * 5.0
            results.append({
                "owner_id": owner.id,
                "email": owner.email,
                "score": round(score, 2),
                "avg_rating": round(avg_rating, 2),
                "dispute_rate": round(dispute_rate, 2),
            })
        # Sort owners by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results