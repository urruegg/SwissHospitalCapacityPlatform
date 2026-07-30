"""Input models for the deterministic BVA simulation engine."""
from __future__ import annotations

from dataclasses import dataclass


class InsufficientInputError(ValueError):
    """Raised when a simulation input slot is missing or invalid."""


@dataclass(frozen=True)
class BvaBaseline:
    """ROM baseline cost inputs in CHF."""

    total_cost_chf: float
    one_time_chf: float
    annual_run_chf: float
    hospitals: int

    @classmethod
    def rom_default(cls) -> "BvaBaseline":
        """Return the docs/BVA.md ROM baseline for the current MVP case."""
        one_time_chf = 1_300_000.0
        annual_run_chf = 1_250_000.0
        return cls(
            total_cost_chf=one_time_chf + annual_run_chf,
            one_time_chf=one_time_chf,
            annual_run_chf=annual_run_chf,
            hospitals=3,
        )


@dataclass(frozen=True)
class HospitalDelta:
    """New hospital what-if inputs supplied to bva.simulate."""

    hospital_name: str
    archetype: str
    beds: int
    occupancy_target: float
    onboarding_scope: str
