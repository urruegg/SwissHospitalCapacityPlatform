"""Hazard-uplift map for the forecast overlay (FR-EXT-011/012).

Pure, dependency-free. Reads forecast_uplift.yaml (pyyaml if present, else an
embedded stdlib default) and computes the incremental multiplicative uplift a
Trust-A signal applies to a base forecast bucket. Uplift is INCREMENTAL over the
seasonal baseline already in gold.forecast_output, combined as (1+f), clamped.
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Optional

_MAP_PATH = Path(__file__).resolve().parent / "forecast_uplift.yaml"
_DEFAULT_CLAMP = 2.0

_EMBEDDED = {
    "clamp": 2.0,
    "rules": [
        {"hazardType": "heat", "severity": ["Severe", "Extreme"], "decay": "none",
         "specialties": {"geriatrics": 0.25, "cardiology": 0.15, "emergency": 0.20, "pulmonology": 0.15,
                         "SPEC_INNERE": 0.25, "SPEC_KARDIO": 0.15, "SPEC_NOTFALL": 0.20, "SPEC_PNEUMO": 0.15}},
        {"hazardType": "heat", "severity": ["Moderate"], "decay": "none",
         "specialties": {"geriatrics": 0.10, "emergency": 0.08, "SPEC_INNERE": 0.10, "SPEC_NOTFALL": 0.08}},
        {"hazardType": "epidemic", "severity": ["Severe", "Extreme"], "decay": "none",
         "specialties": {"pulmonology": 0.30, "emergency": 0.20, "paediatrics": 0.20,
                         "SPEC_PNEUMO": 0.30, "SPEC_NOTFALL": 0.20, "SPEC_NEONAT": 0.20}},
        {"hazardType": "earthquake", "severity": ["Severe", "Extreme"], "decay": "none",
         "specialties": {"emergency": 0.40, "trauma": 0.50, "surgery": 0.25,
                         "SPEC_NOTFALL": 0.40, "SPEC_TRAUMA": 0.50, "SPEC_CHIR": 0.25}},
        {"hazardType": "flood", "severity": ["Severe", "Extreme"], "decay": "none",
         "specialties": {"emergency": 0.15, "SPEC_NOTFALL": 0.15}},
    ],
}


def load_uplift_map(path: Optional[Path] = None) -> dict:
    p = path or _MAP_PATH
    try:
        import yaml  # type: ignore
        loaded = yaml.safe_load(p.read_text(encoding="utf-8"))
        return loaded if loaded else _EMBEDDED
    except Exception:
        return _EMBEDDED


def uplift_factor(hazard_type: str, severity: str, specialty_id: Optional[str], uplift_map: dict) -> float:
    """Incremental uplift (e.g. 0.25) for one hazard/severity/specialty; 0.0 if none."""
    if not specialty_id:
        return 0.0
    total = 0.0
    for rule in uplift_map.get("rules", []):
        if rule["hazardType"] != hazard_type:
            continue
        if severity not in rule["severity"]:
            continue
        total = max(total, float(rule["specialties"].get(specialty_id, 0.0)))
    return total


def _as_date(value) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00")).date()


def signal_applies(forecast_date, onset, expires) -> bool:
    """True when the forecast bucket date is within the signal window (inclusive)."""
    if onset is None:
        return False
    d = _as_date(forecast_date)
    if expires is None:
        return _as_date(onset) <= d
    return _as_date(onset) <= d <= _as_date(expires)


def combine(base_capacity: float, factors: Iterable[float], clamp: float = _DEFAULT_CLAMP) -> float:
    """Adjusted = base * min(clamp, prod(1 + f)); factors are incremental deltas."""
    multiplier = 1.0
    for f in factors:
        multiplier *= (1.0 + max(0.0, float(f)))
    return round(base_capacity * min(clamp, multiplier), 4)
