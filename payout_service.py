"""
Payout service.

This module encapsulates logic for issuing payouts to GPU owners
through an external payment processor. It provides a wrapper around
Stripe's payout API, but gracefully falls back to a no‑op if the
`STRIPE_API_KEY` environment variable is not set.

The service can be extended in the future to support other payout
providers or more sophisticated payout logic (e.g. scheduled bulk
payouts, multi‑currency support, etc.).
"""

from __future__ import annotations

import os
from typing import Optional

try:
    import stripe  # type: ignore
except ImportError:
    stripe = None  # If Stripe is not installed, we run in mock mode


class PayoutService:
    """Service for issuing payouts to providers."""

    def __init__(self, stripe_api_key: Optional[str] = None) -> None:
        self.api_key = stripe_api_key or os.getenv("STRIPE_API_KEY")
        if stripe and self.api_key:
            stripe.api_key = self.api_key

    def create_payout(self, amount: float, currency: str = "usd", description: str = "") -> Optional[str]:
        """Issue a payout of the given amount and return the payout ID.

        If Stripe is not configured or installed, the payout is logged
        instead of being sent. The amount should be provided in major
        currency units (e.g. dollars rather than cents). The method
        returns the payout ID on success or ``None`` in mock mode.
        """
        if not self.api_key or not stripe:
            # Log a debug message and return None in mock mode
            print(
                f"PayoutService (mock): would create payout of {amount} {currency}"
                f" with description '{description}'"
            )
            return None
        # Convert to the smallest currency unit (e.g. cents) as required by Stripe
        payout = stripe.Payout.create(
            amount=int(amount * 100),
            currency=currency,
            description=description,
        )
        return payout.id  # type: ignore[no-any-return]

