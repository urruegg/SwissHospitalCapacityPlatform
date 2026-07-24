"""Deterministic ``compute_expected_impact`` tool (Sprint 26 WS-B, design Sec 3.3).

**This module contains NO randomness and NEVER produces an LLM estimate.** Every
formula is a pure function of its ``(params, gold)`` inputs: same inputs always
produce the same output dict. The impact is grounded in the injected WS-A Gold
occupancy-forecast data (``gold.fact_occupancy_forecast`` /
``gold.fact_forecast_driver``) — never in a model guess.

Two layers:

1. **Formula registry** (dependency-free core) — ``FORMULA_REGISTRY`` maps
   ``impact_formula_ref`` -> ``f(params: dict, gold: dict) -> dict``. Each
   formula returns ``{"metric": "beds", "delta": <int>, "assumptions": [...]}``.

2. **Resolver** (thin) — ``compute_expected_impact(lever_id, params, gold,
   catalog=None)`` resolves the lever's ``impact_formula_ref`` and
   ``owner_role`` from the lever catalog (an injected list/dict for
   dependency-light tests, or the real YAML catalog under
   ``data-platform/decision/levers/`` otherwise), calls the formula, and echoes
   ``lever_id`` / ``owner_role`` in the result so callers know the HITL
   handoff target.

**Grounding rule (identical across all three formulas):** the impact is the
requested ``n``, bounded only by the number of beds that are physically
occupied in the matched forecast row — a lever cannot recover more beds than
are actually occupied. ``delta = min(int(params["n"]), round(forecastOccupiedBeds))``
for the deterministically-selected forecast row. This bound is **not** capped
at the ward's over-capacity gap (``forecastOccupiedBeds - bedCapacity``), so an
approved lever can legitimately move a ward from over-capacity down to
below-100% occupancy. No randomness, never an LLM estimate: the delta and its
assumptions are a pure, deterministic function of the injected gold forecast
row.
"""
from __future__ import annotations

import pathlib
from typing import Any, Callable, Dict, List, Optional

try:
    import yaml  # noqa: F401

    _HAS_YAML = True
except ImportError:
    _HAS_YAML = False

_LEVERS_DIR = pathlib.Path(__file__).resolve().parent.parent / "levers"
_ROLE_FILES = ["ooa.yaml", "dca.yaml", "bmca.yaml", "orsa.yaml", "sba.yaml", "csa.yaml"]

FormulaFn = Callable[[Dict[str, Any], Dict[str, Any]], Dict[str, Any]]


# ---------------------------------------------------------------------------
# Shared grounding helpers (pure, no I/O, no randomness).
# ---------------------------------------------------------------------------
def _require_positive_int(params: Dict[str, Any], key: str = "n") -> int:
    value = params.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"params[{key!r}] must be a positive int, got {value!r}")
    return value


def _require_present(params: Dict[str, Any], key: str) -> Any:
    value = params.get(key)
    if value is None or (isinstance(value, str) and not value.strip()):
        raise ValueError(f"params[{key!r}] is required")
    return value


def _select_forecast_row(params: Dict[str, Any], gold: Dict[str, Any]) -> Dict[str, Any]:
    """Deterministically select exactly one forecast row: match ward (if given)
    and horizon_h (default 72). Raise ValueError on zero or multiple matches."""
    horizon_h = params.get("horizon_h", 72)
    ward = params.get("ward")
    rows = gold.get("forecast") or []

    matches = [r for r in rows if r.get("horizonH") == horizon_h]
    if ward is not None:
        matches = [r for r in matches if r.get("wardId") == ward]

    if len(matches) == 0:
        raise ValueError(
            f"no forecast row found for ward={ward!r} horizon_h={horizon_h!r}"
        )
    if len(matches) > 1:
        raise ValueError(
            f"ambiguous forecast selection: {len(matches)} rows match "
            f"ward={ward!r} horizon_h={horizon_h!r} (expected exactly 1)"
        )
    return matches[0]


def _driver_context_assumptions(
    params: Dict[str, Any], gold: Dict[str, Any], ward: Optional[str], horizon_h: int
) -> List[str]:
    """Optional driver-row context (e.g. net admissions/discharges), sorted by
    factor name for determinism. Silently empty if no driver rows are present
    or injected — this is supplementary context, not part of the grounding
    calculation itself."""
    driver_rows = gold.get("drivers") or []
    relevant = [
        d
        for d in driver_rows
        if d.get("horizonH") == horizon_h and (ward is None or d.get("wardId") == ward)
    ]
    relevant.sort(key=lambda d: str(d.get("factor")))
    return [f"driver:{d.get('factor')}={d.get('delta'):+g}" for d in relevant if d.get("delta") is not None]


def _require_numeric_row_field(row: Dict[str, Any], key: str, ward: Any, horizon_h: Any) -> float:
    value = row.get(key)
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(
            f"forecast row missing numeric {key} for ward={ward!r} horizon={horizon_h!r} "
            f"(got {value!r})"
        )
    return value


def _bounded_bed_impact(
    params: Dict[str, Any], gold: Dict[str, Any], extra_assumptions: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Shared grounding calculation used by all three formulas: bound the
    requested ``n`` by the number of beds physically occupied in the matched
    forecast row (not by the over-capacity gap — see module docstring)."""
    n = _require_positive_int(params, "n")
    row = _select_forecast_row(params, gold)

    ward = row.get("wardId")
    horizon_h = row.get("horizonH")
    bed_capacity = _require_numeric_row_field(row, "bedCapacity", ward, horizon_h)
    forecast_occupied = _require_numeric_row_field(row, "forecastOccupiedBeds", ward, horizon_h)
    bed_gap = max(0, round(forecast_occupied - bed_capacity))
    available = max(0, round(forecast_occupied))
    delta = min(n, available)

    assumptions = [
        f"ward={ward}",
        f"horizon_h={horizon_h}",
        f"forecast_bed_gap={bed_gap}",
        f"requested_n={n}",
        f"delta=min(n, occupied_beds)={delta}",
    ]
    assumptions.extend(_driver_context_assumptions(params, gold, ward, horizon_h))
    if extra_assumptions:
        assumptions.extend(extra_assumptions)

    return {"metric": "beds", "delta": int(delta), "assumptions": assumptions}


# ---------------------------------------------------------------------------
# Formula registry — one pure function per `impact_formula_ref`.
# ---------------------------------------------------------------------------
def expedite_discharge_beds(params: Dict[str, Any], gold: Dict[str, Any]) -> Dict[str, Any]:
    """OOA-EXPEDITE-DISCHARGE: expedite N discharge-ready patients before a
    given time. Grounded by the ward's physically occupied beds (see module docstring)."""
    before = _require_present(params, "before")
    return _bounded_bed_impact(params, gold, extra_assumptions=[f"before={before}"])


def divert_low_acuity_beds(params: Dict[str, Any], gold: Dict[str, Any]) -> Dict[str, Any]:
    """OOA-DIVERT-LOW-ACUITY: divert N low-acuity patients to another ward.
    Grounded by the ward's physically occupied beds (see module docstring)."""
    to_ward = _require_present(params, "to_ward")
    return _bounded_bed_impact(params, gold, extra_assumptions=[f"to_ward={to_ward}"])


def unblock_barrier_beds(params: Dict[str, Any], gold: Dict[str, Any]) -> Dict[str, Any]:
    """DCA-UNBLOCK-BARRIER: resolve N cases of a given discharge-barrier type.
    Grounded by the ward's physically occupied beds (see module docstring)."""
    barrier_type = _require_present(params, "barrier_type")
    return _bounded_bed_impact(params, gold, extra_assumptions=[f"barrier_type={barrier_type}"])


FORMULA_REGISTRY: Dict[str, FormulaFn] = {
    "expedite_discharge_beds": expedite_discharge_beds,
    "divert_low_acuity_beds": divert_low_acuity_beds,
    "unblock_barrier_beds": unblock_barrier_beds,
}


# ---------------------------------------------------------------------------
# Resolver — thin lever-catalog lookup + formula dispatch.
# ---------------------------------------------------------------------------
def _load_real_catalog() -> List[Dict[str, Any]]:
    if not _HAS_YAML:
        raise ValueError(
            "PyYAML is not installed and no catalog was injected; install PyYAML "
            "or pass catalog= explicitly"
        )
    records: List[Dict[str, Any]] = []
    for role_file in _ROLE_FILES:
        path = _LEVERS_DIR / role_file
        if not path.exists():
            continue
        with open(path, "r", encoding="utf-8") as f:
            doc = yaml.safe_load(f) or {}
        records.extend(doc.get("levers") or [])
    return records


def _resolve_lever(lever_id: str, catalog: Optional[List[Dict[str, Any]]]) -> Dict[str, Any]:
    records = catalog if catalog is not None else _load_real_catalog()
    for record in records:
        if record.get("lever_id") == lever_id:
            return record
    raise ValueError(f"unknown lever_id: {lever_id!r}")


def compute_expected_impact(
    lever_id: str,
    params: Dict[str, Any],
    gold: Dict[str, Any],
    catalog: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """Resolve ``lever_id`` -> ``impact_formula_ref`` / ``owner_role`` via the
    lever catalog (injected ``catalog`` as a flat list of lever records, or the
    real on-disk YAML catalog when ``catalog`` is None), then dispatch to the
    matching pure formula in ``FORMULA_REGISTRY``. Pure and deterministic
    end-to-end: no randomness, no
    LLM estimate, no network/Fabric I/O (only local file reads for the catalog)."""
    lever = _resolve_lever(lever_id, catalog)

    formula_ref = lever.get("impact_formula_ref")
    formula = FORMULA_REGISTRY.get(formula_ref)
    if formula is None:
        raise ValueError(f"unknown impact_formula_ref: {formula_ref!r} for lever_id={lever_id!r}")

    owner_role = lever.get("owner_role")
    result = formula(params, gold)

    return {
        "lever_id": lever_id,
        "owner_role": owner_role,
        "metric": result["metric"],
        "delta": result["delta"],
        "assumptions": result["assumptions"],
    }
