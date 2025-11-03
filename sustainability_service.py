"""
Sustainability metrics service.

This module provides functions to estimate the environmental impact
associated with using GPUs.  Given a GPU's specifications and
assumed utilisation, the service returns approximate energy
consumption and carbon emissions per hour as well as a suggested
offset cost.  The underlying numbers are illustrative and should be
replaced with real measurements or integrations with external carbon
tracking APIs in a production deployment【29899153745735†L22-L46】.【29899153745735†L55-L72】
"""

from __future__ import annotations

from typing import Dict

from sqlalchemy.orm import Session

from backend.models.gpu import GPU


class SustainabilityService:
    """Service for estimating the environmental impact of GPU usage."""

    # A rough mapping of GPU types to typical power draw in watts.  In
    # practice this could come from a hardware database or API.
    _DEFAULT_WATTAGE = {
        "NVIDIA A100": 250,
        "NVIDIA H100": 300,
        "NVIDIA V100": 250,
        "NVIDIA L40S": 250,
        "AMD MI250": 300,
    }

    # Approximate carbon intensity (kg CO2 per kWh).  This is a
    # conservative global average; regional values vary widely.  For
    # illustrative purposes only【29899153745735†L22-L46】.
    _CARBON_INTENSITY = 0.4

    # Suggested cost per kg of carbon offset (USD).  Real markets
    # fluctuate; this constant is a placeholder.
    _OFFSET_COST_PER_KG = 10.0

    def __init__(self, db: Session) -> None:
        self.db = db

    def _get_power_draw(self, gpu_name: str) -> float:
        """Return the typical power draw in watts for a given GPU model.

        Parameters
        ----------
        gpu_name: str
            The human-readable name of the GPU.

        Returns
        -------
        float
            Estimated power draw in watts.
        """
        return self._DEFAULT_WATTAGE.get(gpu_name, 250)

    def get_gpu_metrics(self, gpu_id: int) -> Dict[str, float | str]:
        """Estimate carbon metrics for a single GPU.

        Parameters
        ----------
        gpu_id: int
            The ID of the GPU to analyse.

        Returns
        -------
        dict
            A dictionary containing estimated power draw, carbon emissions
            per hour, and the cost to offset those emissions.

        Raises
        ------
        ValueError
            If the GPU does not exist.
        """
        gpu = self.db.query(GPU).get(gpu_id)
        if not gpu:
            raise ValueError("Invalid GPU ID")
        power_watts = self._get_power_draw(gpu.name)
        # Convert watts to kWh per hour (watts / 1000)
        energy_kwh = power_watts / 1000.0
        carbon_kg_per_hour = energy_kwh * self._CARBON_INTENSITY
        offset_cost = carbon_kg_per_hour * self._OFFSET_COST_PER_KG
        return {
            "gpu_name": gpu.name,
            "power_watts": round(power_watts, 2),
            "energy_kwh_per_hour": round(energy_kwh, 3),
            "carbon_kg_per_hour": round(carbon_kg_per_hour, 3),
            "offset_cost_per_hour": round(offset_cost, 2),
            "suggested_action": "Consider purchasing renewable energy credits or donating to tree planting schemes to offset emissions."
        }

    def get_summary_metrics(self) -> Dict[str, float]:
        """Compute aggregate sustainability metrics across all GPUs.

        Returns
        -------
        dict
            Total power draw, energy consumption, carbon emissions and
            estimated offset cost for all registered GPUs.
        """
        gpus = self.db.query(GPU).all()
        total_power = 0.0
        total_energy = 0.0
        total_carbon = 0.0
        for gpu in gpus:
            power = self._get_power_draw(gpu.name)
            energy = power / 1000.0
            carbon = energy * self._CARBON_INTENSITY
            total_power += power
            total_energy += energy
            total_carbon += carbon
        total_offset_cost = total_carbon * self._OFFSET_COST_PER_KG
        return {
            "total_power_watts": round(total_power, 2),
            "total_energy_kwh_per_hour": round(total_energy, 3),
            "total_carbon_kg_per_hour": round(total_carbon, 3),
            "total_offset_cost_per_hour": round(total_offset_cost, 2)
        }