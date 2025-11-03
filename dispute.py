"""
Pydantic schemas for disputes.
"""

from pydantic import BaseModel


class DisputeBase(BaseModel):
    booking_id: int
    description: str
    status: str | None = None


class DisputeCreate(DisputeBase):
    pass


class DisputeRead(DisputeBase):
    id: int

    class Config:
        from_attributes = True