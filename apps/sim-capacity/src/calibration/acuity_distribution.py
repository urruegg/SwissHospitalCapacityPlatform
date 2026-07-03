"""Acuity distribution sampler for the sim-capacity simulator.

Builds a weighted sampler over ``(disease_id, drg_code, mean_los_norm)`` tuples
for a given hospital (optionally filtered by specialty), driven by the mappings
in ``09_map_disease_treatment_specialty_service.csv`` and enriched with DRG
weights + LOS from ``06_dim_drg.csv``.

Design spec: §4.4 (acuity mix drives arrival envelope + LOS distribution).
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

_REPO_ROOT = Path(__file__).resolve().parents[4]
_REVIEW_DIR = _REPO_ROOT / "docs" / "reviews" / "2026-06-29-ama-capacity-metadata-review"
_MAP_CSV = _REVIEW_DIR / "09_map_disease_treatment_specialty_service.csv"
_DRG_CSV = _REVIEW_DIR / "06_dim_drg.csv"
_DISEASE_CSV = _REVIEW_DIR / "04_dim_disease.csv"


@dataclass(frozen=True)
class _AcuityEntry:
    disease_id: str
    drg_code: str
    mean_los_norm: float
    weight: float  # cost_weight; used as sampling weight proxy


@dataclass
class AcuitySampler:
    hospital_short: str
    specialty_id: Optional[str]
    entries: List[_AcuityEntry] = field(default_factory=list)

    def sample(self, seed: Optional[int] = None) -> Tuple[str, str, float]:
        if not self.entries:
            raise ValueError(
                f"No acuity entries for hospital={self.hospital_short!r} "
                f"specialty={self.specialty_id!r}"
            )
        rng = random.Random(seed)
        weights = [e.weight for e in self.entries]
        chosen = rng.choices(self.entries, weights=weights, k=1)[0]
        return (chosen.disease_id, chosen.drg_code, chosen.mean_los_norm)


def _load_drg_lookup() -> Dict[str, Tuple[float, float]]:
    """Return ``{drg_code: (cost_weight, mean_los_norm)}``."""
    lookup: Dict[str, Tuple[float, float]] = {}
    with _DRG_CSV.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            code = row["drg_code"]
            try:
                cw = float(row["cost_weight"])
                los = float(row["mean_los_norm"])
            except (ValueError, KeyError):
                continue
            lookup[code] = (cw, los)
    return lookup


def build_acuity_sampler(
    hospital_short: str,
    specialty_id: Optional[str] = None,
) -> AcuitySampler:
    """Build an acuity sampler for a hospital (optionally filtered by specialty)."""
    target_hid = f"H_{hospital_short.upper()}"
    drg_lookup = _load_drg_lookup()

    entries: List[_AcuityEntry] = []
    with _MAP_CSV.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["hospital_id"] != target_hid:
                continue
            if specialty_id and row["specialty_id"] != specialty_id:
                continue
            drg_code = row["drg_code"]
            drg = drg_lookup.get(drg_code)
            if not drg:
                continue
            cost_weight, mean_los = drg
            entries.append(
                _AcuityEntry(
                    disease_id=row["disease_id"],
                    drg_code=drg_code,
                    mean_los_norm=mean_los,
                    weight=cost_weight,
                )
            )

    return AcuitySampler(
        hospital_short=hospital_short.upper(),
        specialty_id=specialty_id,
        entries=entries,
    )
