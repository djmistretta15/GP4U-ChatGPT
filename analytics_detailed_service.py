"""
Detailed analytics service.

Provides advanced statistics such as the most booked GPUs and the
highest spending users.  The methods in this service return lists of
dictionaries that can be consumed by API endpoints.  If more complex
visualisation is needed, consider building a dedicated reporting
service or exporting the data to a BI tool.
"""

from __future__ import annotations

from typing import List, Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.gpu import GPU
from backend.models.booking import Booking
from backend.models.payment import Payment
from backend.models.user import User


class AnalyticsDetailedService:
    """Service providing detailed analytics queries."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def top_gpus_by_bookings(self, limit: int = 5) -> List[Dict[str, object]]:
        """Return GPUs sorted by the number of bookings in descending order.

        Parameters
        ----------
        limit: int
            Maximum number of records to return.

        Returns
        -------
        List[Dict[str, object]]
            A list of dicts containing GPU ID, name and booking count.
        """
        result = (
            self.db.query(
                GPU.id.label("gpu_id"),
                GPU.name.label("name"),
                func.count(Booking.id).label("bookings_count"),
            )
            .join(Booking, Booking.gpu_id == GPU.id)
            .group_by(GPU.id)
            .order_by(func.count(Booking.id).desc())
            .limit(limit)
            .all()
        )
        return [dict(r._mapping) for r in result]

    def top_users_by_spending(self, limit: int = 5) -> List[Dict[str, object]]:
        """Return users sorted by total payment amount in descending order.

        Parameters
        ----------
        limit: int
            Maximum number of records to return.

        Returns
        -------
        List[Dict[str, object]]
            A list of dicts containing user ID, email and total spent.
        """
        result = (
            self.db.query(
                User.id.label("user_id"),
                User.email.label("email"),
                func.sum(Payment.amount).label("total_spent"),
            )
            .join(Payment, Payment.user_id == User.id)
            .group_by(User.id)
            .order_by(func.sum(Payment.amount).desc())
            .limit(limit)
            .all()
        )
        return [dict(r._mapping) for r in result]