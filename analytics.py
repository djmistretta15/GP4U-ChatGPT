"""
Analytics response schemas.

Models used for returning aggregate metrics and statistics.
"""

from pydantic import BaseModel


class AnalyticsMetrics(BaseModel):
    """Aggregate platform metrics."""
    total_gpus: int
    total_bookings: int
    total_revenue: float
    average_utilization: float

