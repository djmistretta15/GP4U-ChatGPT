"""
Pricing options service layer.

This service provides a simple algorithm to compute pricing options for a
given GPU.  Two pricing strategies are returned: a base price (the
configured price per hour for the GPU) and a dynamic price calculated
based on supply and demand.  Supply is defined as the number of
available GPUs of the same model, while demand is measured by the
number of open marketplace orders for the specific GPU.  The dynamic
price scales the base price proportionally to the demand/supply ratio.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from backend.models.gpu import GPU
from backend.models.order import Order, OrderStatus


class PricingOptionsService:
    """Service for computing pricing options for GPUs."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_price_options(self, gpu_id: int) -> dict[str, float]:
        """Return base and dynamic pricing options for a GPU.

        Parameters
        ----------
        gpu_id: int
            The primary key of the GPU for which to compute pricing.

        Returns
        -------
        dict[str, float]
            A dictionary containing ``base_price`` and ``dynamic_price``.

        Raises
        ------
        ValueError
            If the GPU does not exist.
        """
        gpu = self.db.query(GPU).get(gpu_id)
        if not gpu:
            raise ValueError("Invalid GPU ID")
        base_price = float(gpu.price_per_hour)
        # Compute supply: count of available GPUs with same name
        supply = (
            self.db.query(GPU)
            .filter(GPU.name == gpu.name, GPU.is_available == True)
            .count()
        )
        # Compute demand: count of open orders for this GPU
        demand = (
            self.db.query(Order)
            .filter(
                Order.gpu_id == gpu_id,
                Order.status == OrderStatus.OPEN.value,
            )
            .count()
        )
        # Avoid division by zero by ensuring supply >= 1
        dynamic_price = base_price * (demand + 1) / (supply + 1)
        # Round to two decimal places for consistency
        dynamic_price = round(dynamic_price, 2)
        return {"base_price": base_price, "dynamic_price": dynamic_price}