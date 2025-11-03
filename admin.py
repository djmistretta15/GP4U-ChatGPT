"""
Pydantic schemas for admin users.
"""

from pydantic import BaseModel, constr


class AdminBase(BaseModel):
    username: str


class AdminCreate(AdminBase):
    password: constr(min_length=8)
    is_superadmin: bool | None = False


class AdminRead(AdminBase):
    id: int
    is_superadmin: bool

    class Config:
        from_attributes = True