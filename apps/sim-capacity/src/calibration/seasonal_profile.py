"""Seasonal / weekly / hourly demand profile for the sim-capacity simulator.

Combines three multiplicative curves that shape admission demand over time:

- **Monthly** (Nov-Feb winter peak +20%, Jul-Aug summer dip -15%).
- **Weekly** (Mon spike +15%, Fri-Sat drop -10%, Sun trough -25%).
- **Hourly** (all-day average blending ED evening peak with elective morning peak).

Curves are hand-authored to match the HCC utilization pattern PNG
(``docs/reviews/2026-07-01-ama-hcc-northstar-review/hcc-apacities-utilization-pattern-overview.png``).

Design spec: §4.5 (seasonal shape) + §4.7 (hourly arrival mix).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

from .hospital_presets import HospitalPreset

# Monthly curve (Jan..Dec). Peak in Nov-Feb, dip in Jul-Aug.
_MONTHLY: List[float] = [
    1.20, 1.18, 1.05, 1.00, 0.95, 0.90,
    0.85, 0.85, 0.95, 1.00, 1.15, 1.22,
]

# Weekly curve (Mon..Sun). Mon spike, Sun trough.
_WEEKLY_RAW: List[float] = [1.15, 1.05, 1.00, 1.00, 0.90, 0.90, 0.75]

# Hourly curve (0..23). Blend of ED evening peak (18-02) and elective morning
# peak (07-11). Normalized below so sum ~ 24.
_HOURLY_RAW: List[float] = [
    1.10, 1.05, 0.95, 0.75, 0.60, 0.55,  # 00-05
    0.60, 0.90, 1.15, 1.25, 1.20, 1.10,  # 06-11
    1.00, 0.95, 0.95, 0.95, 1.00, 1.05,  # 12-17
    1.20, 1.30, 1.30, 1.25, 1.20, 1.15,  # 18-23
]


def _normalize(values: List[float], target_sum: float) -> List[float]:
    s = sum(values)
    return [v * target_sum / s for v in values]


@dataclass(frozen=True)
class SeasonalProfile:
    """Multiplicative demand profile combining monthly, weekly, and hourly curves."""

    hospital: str
    seed: int
    _monthly: List[float] = field(default_factory=list)
    _weekly: List[float] = field(default_factory=list)
    _hourly: List[float] = field(default_factory=list)

    @classmethod
    def from_preset(cls, preset: HospitalPreset, seed: int = 42) -> "SeasonalProfile":
        monthly = list(_MONTHLY)
        weekly = _normalize(_WEEKLY_RAW, target_sum=7.0)
        hourly = _normalize(_HOURLY_RAW, target_sum=24.0)
        return cls(
            hospital=preset.short_name,
            seed=seed,
            _monthly=monthly,
            _weekly=weekly,
            _hourly=hourly,
        )

    def demand_multiplier(self, when: datetime) -> float:
        """Combined multiplier: monthly * weekly * hourly.

        ``weekday()`` returns Monday=0 .. Sunday=6.
        """
        m = self._monthly[when.month - 1]
        w = self._weekly[when.weekday()]
        h = self._hourly[when.hour]
        return m * w * h
