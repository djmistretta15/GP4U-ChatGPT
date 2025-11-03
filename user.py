"""
Pydantic schemas for users.

Defines user representations for API input and output.
"""

from datetime import datetime
from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: constr(min_length=8)


class UserRead(UserBase):
    id: int
    is_active: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True