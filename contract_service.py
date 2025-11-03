"""
Contract service layer.

This module encapsulates business logic for creating and retrieving
contracts between renters and GPU providers.  A contract records the
agreed pricing model (fixed or spot), the price per hour, and the
time period for which the renter is entitled to use the GPU.  The
service computes the correct price based on the chosen contract type
and ensures that referenced users and GPUs exist.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict

from sqlalchemy.orm import Session

from backend.models.contract import Contract, ContractType, ContractStatus
from backend.models.gpu import GPU
from backend.models.user import User
from backend.services.pricing_options_service import PricingOptionsService


class ContractService:
    """Service for managing rental contracts."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def create_contract(
        self,
        user_id: int,
        gpu_id: int,
        contract_type: str,
        duration_hours: int = 1,
    ) -> Contract:
        """Create a new contract for the specified user and GPU.

        Parameters
        ----------
        user_id: int
            The ID of the renter entering into the contract.
        gpu_id: int
            The ID of the GPU being rented.
        contract_type: str
            Either ``fixed`` or ``spot``.  Fixed contracts use the GPU's
            base price; spot contracts use the dynamic price computed by
            the pricing options service.
        duration_hours: int, optional
            The length of the contract in hours.  Defaults to 1 hour.

        Returns
        -------
        Contract
            The newly created Contract instance.

        Raises
        ------
        ValueError
            If the user or GPU does not exist, or if an invalid
            contract type is provided.
        """
        # Validate user and GPU existence
        user = self.db.query(User).get(user_id)
        gpu = self.db.query(GPU).get(gpu_id)
        if not user:
            raise ValueError("Invalid user ID")
        if not gpu:
            raise ValueError("Invalid GPU ID")
        # Determine contract type
        try:
            ctype = ContractType(contract_type)
        except Exception:
            raise ValueError("Invalid contract type; must be 'fixed' or 'spot'")
        # Compute price based on contract type
        if ctype == ContractType.FIXED:
            price_per_hour = float(gpu.price_per_hour)
        else:
            # Use dynamic price from PricingOptionsService
            pricing_service = PricingOptionsService(self.db)
            options = pricing_service.get_price_options(gpu_id)
            price_per_hour = options["dynamic_price"]
        # Compute start and end times
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=duration_hours)
        # Create contract
        contract = Contract(
            user_id=user_id,
            gpu_id=gpu_id,
            contract_type=ctype.value,
            price_per_hour=price_per_hour,
            start_time=start_time,
            end_time=end_time,
            status=ContractStatus.ACTIVE.value
        )
        self.db.add(contract)
        self.db.commit()
        self.db.refresh(contract)
        return contract

    def get_contracts_by_user(self, user_id: int) -> List[Contract]:
        """Return all contracts for a given user.

        Parameters
        ----------
        user_id: int
            The ID of the user whose contracts to retrieve.

        Returns
        -------
        List[Contract]
            A list of Contract objects belonging to the user.
        """
        contracts = (
            self.db.query(Contract)
            .filter(Contract.user_id == user_id)
            .order_by(Contract.start_time.desc())
            .all()
        )
        return contracts