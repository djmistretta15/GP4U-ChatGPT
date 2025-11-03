"""
Pydantic schemas for bookings.

Enforces that the end time must be after the start time.
"""

from datetime import datetime
from pydantic import BaseModel, validator


class BookingBase(BaseModel):
    user_id: int
    gpu_id: int
    start_time: datetime
    end_time: datetime

    @validator('end_time')
    def check_end_time(cls, v, values):
        start = values.get('start_time')
        if start and v <= start:
            raise ValueError('end_time must be after start_time')
        return v


class BookingCreate(BookingBase):
    pass


class BookingRead(BookingBase):
    id: int

    class Config:
        from_attributes = True