"""
Pydantic schemas for GPUs.

Used to validate GPU creation and represent GPUs in API responses.
"""

from pydantic import BaseModel, conint, confloat


class GPUBase(BaseModel):
    name: str
    manufacturer: str
    memory_gb: conint(ge=0)
    price_per_hour: confloat(ge=0)


class GPUCreate(GPUBase):
    pass


class GPURead(GPUBase):
    id: int
    is_available: bool

    class Config:
        from_attributes = True