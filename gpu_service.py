"""
Service layer for GPU operations.

Provides functions to create, list and update GPUs.  Services encapsulate
business logic and can be tested in isolation from API routes.
"""

from sqlalchemy.orm import Session

from backend.models.gpu import GPU


class GPUService:
    """Service for GPU operations."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_gpus(self) -> list[GPU]:
        return self.db.query(GPU).all()

    def create_gpu(self, *, name: str, manufacturer: str, memory_gb: int, price_per_hour: float) -> GPU:
        gpu = GPU(
            name=name,
            manufacturer=manufacturer,
            memory_gb=memory_gb,
            price_per_hour=price_per_hour,
            is_available=True,
        )
        self.db.add(gpu)
        self.db.commit()
        self.db.refresh(gpu)
        return gpu