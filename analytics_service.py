"""
Analytics service.

This module defines a simple analytics service that aggregates key
metrics about the GP4U platform. The service queries the database to
compute the total number of GPUs and bookings as well as the total
revenue generated from payments. Additional metrics such as average
utilisation and booking durations can be added as needed.
"""

from __future__ import annotations

from typing import Dict, Any

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.gpu import GPU
from backend.models.booking import Booking
from backend.models.payment import Payment


class AnalyticsService:
    """Compute aggregate statistics for the GP4U platform."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_metrics(self) -> Dict[str, Any]:
        """Return a dictionary of high‑level platform metrics."""
        total_gpus = self.db.query(func.count(GPU.id)).scalar() or 0
        total_bookings = self.db.query(func.count(Booking.id)).scalar() or 0
        total_revenue = (
            self.db.query(func.coalesce(func.sum(Payment.amount), 0)).scalar() or 0.0
        )

        # Compute average utilisation as the average fraction of time a GPU
        # is booked over a hypothetical period. For now this is a stub
        # returning 0.0; in a full implementation you would compute the
        # total booked time divided by total available time.
        average_utilisation = 0.0
        return {
            "total_gpus": int(total_gpus),
            "total_bookings": int(total_bookings),
            "total_revenue": float(total_revenue),
            "average_utilisation": float(average_utilisation),
        }

