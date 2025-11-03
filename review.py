"""
Pydantic schemas for reviews.
"""

from pydantic import BaseModel, conint


class ReviewBase(BaseModel):
    booking_id: int
    rating: conint(ge=1, le=5)
    comment: str | None = None


class ReviewCreate(ReviewBase):
    pass


class ReviewRead(ReviewBase):
    id: int

    class Config:
        from_attributes = True