"""Service for matching marketplace orders with available GPUs.

The matching algorithm implemented here is simplistic and intended
primarily for demonstration.  It iterates over open orders and
allocates the first available GPU (with ``is_available`` set to
True) that matches the requested GPU ID.  Once matched, the order
status is updated to ``matched`` and the GPU's availability is set
to False.  In a real system this service could support partial
fulfilment, prioritisation, and concurrency control.
"""

from sqlalchemy.orm import Session

from backend.models.order import Order
from backend.models.gpu import GPU


class MatchingService:
    """Service for matching open orders with available GPUs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def match_orders(self) -> list[Order]:
        """Match open orders with available GPUs.

        Returns a list of orders that were successfully matched.  Orders
        that cannot be fulfilled remain open.
        """
        matched_orders: list[Order] = []
        # Query open orders
        open_orders = (
            self.db.query(Order)
            .filter(Order.status == "open")
            .order_by(Order.id)
            .all()
        )
        for order in open_orders:
            # Find an available GPU with the requested ID
            gpu: GPU | None = (
                self.db.query(GPU)
                .filter(GPU.id == order.gpu_id, GPU.is_available == True)  # noqa: E712
                .first()
            )
            if gpu is None:
                continue
            # Mark GPU as unavailable and update order status
            gpu.is_available = False
            order.status = "matched"
            self.db.commit()
            self.db.refresh(order)
            matched_orders.append(order)
        return matched_orders