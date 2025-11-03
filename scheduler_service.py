"""
Scheduling service for GPU bookings.

This module encapsulates logic for checking GPU availability within a given
time window.  It interacts with the bookings table to determine whether
requested time slots overlap with existing reservations.  Separating this
logic into a service layer keeps the API endpoints thin and allows
re-use from other parts of the application, such as a potential
calendar UI or automated scheduling agent.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from backend.models.booking import Booking


class SchedulerService:
    """Service for determining GPU availability.

    The scheduler checks for overlapping bookings to decide whether a
    requested time slot is free.  In the future this service could be
    extended to suggest alternative times or handle recurring bookings.
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    def is_available(self, gpu_id: int, start: datetime, end: datetime) -> bool:
        """Return True if the GPU is free between ``start`` and ``end``.

        A GPU is considered available if there are no existing bookings
        whose time range overlaps with the requested window.  Overlap
        occurs when an existing booking starts before the requested end
        time and ends after the requested start time.

        Parameters
        ----------
        gpu_id: int
            The identifier of the GPU to check.
        start: datetime
            Start of the desired booking window.
        end: datetime
            End of the desired booking window.

        Returns
        -------
        bool
            ``True`` if the GPU is available; otherwise ``False``.
        """
        # Guard against inverted time ranges
        if end <= start:
            return False

        conflict_count = (
            self.db.query(Booking)
            .filter(Booking.gpu_id == gpu_id)
            .filter(Booking.start_time < end, Booking.end_time > start)
            .count()
        )
        return conflict_count == 0