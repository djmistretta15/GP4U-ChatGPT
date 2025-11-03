"""
Bid service layer.

This module encapsulates business logic around placing bids on orders
and accepting the highest bid.  It keeps the API endpoints thin and
allows the bidding logic to be reused in other contexts (e.g. a
scheduled auction worker).  For simplicity, bids are assumed to be
committed immediately; in a more robust implementation, bid
transactions might be handled atomically and include notifications.
"""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import desc

from backend.models.bid import Bid, BidStatus
from backend.models.order import Order, OrderStatus


class BidService:
    """Service for managing marketplace bids."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def place_bid(self, order_id: int, user_id: int, amount: Decimal) -> Bid:
        """Create a new bid on the specified order.

        Parameters
        ----------
        order_id: int
            The identifier of the order to bid on.
        user_id: int
            The identifier of the user placing the bid.
        amount: Decimal
            The bid amount offered by the user.

        Returns
        -------
        Bid
            The newly created bid record.
        """
        # Ensure the order exists and is open
        order = self.db.query(Order).filter(Order.id == order_id).first()
        if not order:
            raise ValueError("Order not found")
        if order.status != OrderStatus.OPEN.value:
            raise ValueError("Cannot bid on a closed order")

        bid = Bid(order_id=order_id, user_id=user_id, amount=amount)
        self.db.add(bid)
        self.db.commit()
        self.db.refresh(bid)
        return bid

    def list_bids(self, order_id: int) -> List[Bid]:
        """Return all bids associated with a given order."""
        return self.db.query(Bid).filter(Bid.order_id == order_id).order_by(desc(Bid.amount)).all()

    def accept_highest_bid(self, order_id: int) -> Optional[Bid]:
        """Accept the highest bid on an order and reject others.

        Parameters
        ----------
        order_id: int
            The identifier of the order whose bids should be processed.

        Returns
        -------
        Optional[Bid]
            The accepted bid, or ``None`` if no bids exist.
        """
        # Retrieve all open bids for the order, highest first
        bids = (
            self.db.query(Bid)
            .filter(Bid.order_id == order_id, Bid.status == BidStatus.OPEN.value)
            .order_by(desc(Bid.amount))
            .all()
        )
        if not bids:
            return None

        accepted_bid = bids[0]
        accepted_bid.status = BidStatus.ACCEPTED.value

        # Reject all other open bids on this order
        for bid in bids[1:]:
            bid.status = BidStatus.REJECTED.value

        # Update order status and price to reflect the accepted bid
        order = self.db.query(Order).filter(Order.id == order_id).one()
        order.price_per_hour = accepted_bid.amount
        order.status = OrderStatus.MATCHED.value

        self.db.commit()
        # Note: do not refresh all bids individually for performance
        self.db.refresh(accepted_bid)
        return accepted_bid