"""Hospital preset loader for the sim-capacity simulator.

Reads ``01_dim_hospital.csv`` from the 2026-06-29 AMA capacity metadata review
and returns a :class:`HospitalPreset` for a given hospital short name.

Design spec: §4.5 (bed inference formula for USZ).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

# Bed inference defaults (design spec §4.5)
_AVG_LOS_DAYS = 5.5
_TARGET_OCCUPANCY = 0.85
_DAYS_IN_YEAR = 365

_SUPPORTED = {"USZ", "LUKS", "SZB", "HSL"}

_REPO_ROOT = Path(__file__).resolve().parents[4]
_CSV_PATH = (
    _REPO_ROOT
    / "docs"
    / "reviews"
    / "2026-06-29-ama-capacity-metadata-review"
    / "01_dim_hospital.csv"
)


@dataclass(frozen=True)
class HospitalPreset:
    hospital_id: str
    name: str
    short_name: str
    type: str
    care_level: str
    canton: str
    city: str
    beds: Optional[int]
    beds_quality: str
    staff: Optional[int]
    staff_quality: str
    stationary_cases_yr: Optional[int]
    ambulatory_yr: Optional[int]
    ed_visits_yr: Optional[int]
    org_axis: str
    residency_tag: str
    source: str
    inferred_bed_count: Optional[int] = None


def _to_int(value: str) -> Optional[int]:
    v = (value or "").strip()
    if not v:
        return None
    # Tolerate values like ">50000" by stripping leading comparators.
    if v[0] in "<>~":
        v = v[1:].strip()
    try:
        return int(v)
    except ValueError:
        return None


def _infer_beds(stationary_cases_yr: Optional[int]) -> Optional[int]:
    if not stationary_cases_yr:
        return None
    beds = (stationary_cases_yr * _AVG_LOS_DAYS) / (_DAYS_IN_YEAR * _TARGET_OCCUPANCY)
    return round(beds)


def load_preset(short_name: str) -> HospitalPreset:
    """Load a hospital preset by short name (e.g. ``"USZ"``)."""
    key = short_name.upper()
    if key not in _SUPPORTED:
        raise KeyError(f"Unknown hospital preset: {short_name!r}")
    if key == "HSL":
        raise ValueError("HSL preset deferred (insufficient bed/OR data)")

    target_id = f"H_{key}"
    with _CSV_PATH.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row["hospital_id"] == target_id:
                stationary = _to_int(row["stationary_cases_yr"])
                beds = _to_int(row["beds"])
                inferred = _infer_beds(stationary) if beds is None else None
                # Upgrade quality label when we successfully inferred a value
                # from stationary_cases_yr (CSV marks it "missing" until then).
                beds_quality = (
                    "inferred" if beds is None and inferred is not None
                    else row["beds_quality"]
                )
                return HospitalPreset(
                    hospital_id=row["hospital_id"],
                    name=row["name"],
                    short_name=row["short_name"],
                    type=row["type"],
                    care_level=row["care_level"],
                    canton=row["canton"],
                    city=row["city"],
                    beds=beds,
                    beds_quality=beds_quality,
                    staff=_to_int(row["staff"]),
                    staff_quality=row["staff_quality"],
                    stationary_cases_yr=stationary,
                    ambulatory_yr=_to_int(row["ambulatory_yr"]),
                    ed_visits_yr=_to_int(row["ed_visits_yr"]),
                    org_axis=row["org_axis"],
                    residency_tag=row["residency_tag"],
                    source=row["source"],
                    inferred_bed_count=inferred,
                )
    raise KeyError(f"Hospital {target_id!r} not found in {_CSV_PATH.name}")
