"""
Monitoring service for platform metrics.

This module aggregates statistics about GPUs, bookings and payments to
provide operational insights.  Metrics include total counts, average
booking duration, total revenue, and basic utilisation estimates.
The service can be extended to compute additional KPIs or feed data
into an external monitoring system.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.models.gpu import GPU
from backend.models.booking import Booking
from backend.models.payment import Payment


class MonitoringService:
    """Service to compute aggregated metrics for the platform."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def compute_metrics(self) -> Dict[str, float | int]:
        """Return a dictionary of high‑level usage metrics.

        The metrics reported include:

        - total_gpus: number of GPUs registered
        - total_bookings: number of bookings made
        - average_booking_hours: average duration of a booking in hours
        - total_revenue: sum of all payment amounts

        Additional metrics such as utilisation rate and average price per
        hour could be added later.
        """
        total_gpus = self.db.query(func.count(GPU.id)).scalar() or 0
        total_bookings = self.db.query(func.count(Booking.id)).scalar() or 0

        # Compute average booking duration in hours
        avg_duration_hours = 0.0
        if total_bookings > 0:
            durations = (
                self.db.query(
                    func.avg(
                        func.strftime("%s", Booking.end_time) - func.strftime("%s", Booking.start_time)
                    )
                ).scalar()
            )
            if durations is not None:
                avg_duration_hours = durations / 3600.0

        # Compute total revenue from payments
        total_revenue = self.db.query(func.sum(Payment.amount)).scalar() or 0.0

        return {
            "total_gpus": total_gpus,
            "total_bookings": total_bookings,
            "average_booking_hours": round(avg_duration_hours, 2),
            "total_revenue": float(total_revenue),
        }