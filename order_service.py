"""Service layer for marketplace orders.

Provides functions to create and list marketplace orders.  In the future
this service could implement matching logic to pair supply and demand
orders or integrate with payment systems.  By isolating business logic
in a service, API routes remain thin and easier to test.
"""

from sqlalchemy.orm import Session

from backend.models.order import Order


class OrderService:
    """Service for creating and retrieving orders."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def list_orders(self) -> list[Order]:
        """Return all orders in the database."""
        return self.db.query(Order).all()

    def create_order(self, *, gpu_id: int, user_id: int, quantity: int, price_per_hour: float) -> Order:
        """Create a new marketplace order.

        Parameters
        ----------
        gpu_id: int
            The ID of the GPU being requested.
        user_id: int
            The ID of the renter placing the order.
        quantity: int
            Number of GPU instances desired.
        price_per_hour: float
            The price the renter is willing to pay per GPU per hour.

        Returns
        -------
        Order
            The newly created Order object, persisted to the database.
        """
        order = Order(
            gpu_id=gpu_id,
            user_id=user_id,
            quantity=quantity,
            price_per_hour=price_per_hour,
            status="open",
        )
        self.db.add(order)
        self.db.commit()
        self.db.refresh(order)
        return order