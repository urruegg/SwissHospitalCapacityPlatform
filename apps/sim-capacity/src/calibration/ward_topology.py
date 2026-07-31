"""Ward topology loader for the sim-capacity simulator.

Reads ``07_dim_ward_capacityunit.csv`` and returns the per-hospital ward map.

Design spec: §4.5 (ward-level capacity envelope).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CSV_PATH = (
    _REPO_ROOT
    / "data"
    / "master-data"
    / "capacity"
    / "07_dim_ward_capacityunit.csv"
)


@dataclass(frozen=True)
class WardInfo:
    ward_id: str
    hospital_id: str
    name: str
    unit_type: str
    specialty_id: str
    bed_count: Optional[int]
    beds_quality: str


def _to_int(value: str) -> Optional[int]:
    v = (value or "").strip()
    if not v:
        return None
    try:
        return int(v)
    except ValueError:
        return None


def load_ward_topology(hospital_short: str) -> Dict[str, WardInfo]:
    """Return ``{ward_id: WardInfo}`` for the given hospital."""
    target_hid = f"H_{hospital_short.upper()}"
    result: Dict[str, WardInfo] = {}
    with _CSV_PATH.open(newline="", encoding="utf-8-sig") as fh:
        for row in csv.DictReader(fh):
            if row["hospital_id"] != target_hid:
                continue
            ward_id = row["ward_id"]
            result[ward_id] = WardInfo(
                ward_id=ward_id,
                hospital_id=row["hospital_id"],
                name=row["name"],
                unit_type=row["unit_type"],
                specialty_id=row["specialty_id"],
                bed_count=_to_int(row["bed_count"]),
                beds_quality=row["bed_count_quality"],
            )
    return result
