"""
Pydantic schemas for payments.

Represents payment records in API responses.
"""

from datetime import datetime
from pydantic import BaseModel, condecimal


class PaymentBase(BaseModel):
    booking_id: int
    amount: condecimal(max_digits=10, decimal_places=2)
    status: str | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentRead(PaymentBase):
    id: int
    created_at: datetime | None = None

    class Config:
        from_attributes = True