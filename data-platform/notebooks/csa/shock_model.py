"""Sprint 16 T5 — CSA shock model (pure functions, no Spark).

The shock model projects a baseline capacity state forward under a scenario's
shock vector, so it can be classified by the tier classifier
(``csa-tier-classifier.py``) and summarised into KPIs. Kept Spark-free so the
model is unit-testable without a Fabric session (design spec §12 notebook
golden test).

Baseline shape::

    {"<resource>": {"capacity": int, "occupied": int}}

Shock shape (subset of the scenario schema)::

    {
      "shockVector": "demand-surge" | "capacity-loss" | "supply-loss" | ...,
      "affectedResources": ["beds", ...],
      "magnitude": {"unit": "percent" | "absolute", "value": number}
    }
"""
from __future__ import annotations

from typing import Any

# Fraction of extra capacity that internal levers (Tier 2 reallocation) can add
# before a scenario is deemed to exceed site capacity (→ Tier 3). Version-pinned
# alongside ADR-0024.
DEFAULT_LEVER_HEADROOM = 0.15

# Resources modelled as equipment/supply (capacity shrinks under supply-loss).
_EQUIPMENT_RESOURCES = frozenset({"ventilators", "supplies", "ppe", "oxygen", "blood"})


def apply_shock(baseline: dict[str, dict[str, Any]], shock: dict[str, Any]) -> dict[str, dict[str, int]]:
    """Return a new capacity state after applying the shock to affected resources."""
    vector = shock.get("shockVector", "demand-surge")
    affected = set(shock.get("affectedResources", []))
    magnitude = shock.get("magnitude", {}) or {}
    unit = magnitude.get("unit", "percent")
    value = float(magnitude.get("value", 0))

    projected: dict[str, dict[str, int]] = {}
    for resource, dim in baseline.items():
        capacity = int(dim.get("capacity", 0))
        occupied = int(dim.get("occupied", 0))

        if resource in affected:
            if vector == "demand-surge":
                occupied = _bump(occupied, unit, value)
            elif vector in ("capacity-loss", "staff-loss"):
                capacity = _drop(capacity, unit, value)
            elif vector in ("supply-loss", "system-loss"):
                if resource in _EQUIPMENT_RESOURCES or vector == "system-loss":
                    capacity = _drop(capacity, unit, value)

        projected[resource] = {"capacity": max(capacity, 0), "occupied": max(occupied, 0)}
    return projected


def _bump(occupied: int, unit: str, value: float) -> int:
    if unit == "percent":
        return round(occupied * (1.0 + value / 100.0))
    return round(occupied + value)


def _drop(capacity: int, unit: str, value: float) -> int:
    if unit == "percent":
        return round(capacity * (1.0 - value / 100.0))
    return round(capacity - value)


def project_state(
    baseline: dict[str, dict[str, Any]],
    shock: dict[str, Any],
    lever_headroom: float = DEFAULT_LEVER_HEADROOM,
    flags: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project the state and shape it for the tier classifier.

    ``capacityExceededAfterLevers`` is derived: True when any resource is still
    over capacity after the internal-lever headroom is applied.
    """
    projected = apply_shock(baseline, shock)
    resources: dict[str, dict[str, float]] = {}
    exceeded_after_levers = False

    for resource, dim in projected.items():
        capacity = dim["capacity"]
        occupied = dim["occupied"]
        utilization = (occupied / capacity) if capacity > 0 else float("inf")
        shortfall = max(occupied - capacity, 0)
        resources[resource] = {"utilization": round(utilization, 4), "shortfall": shortfall}
        effective_capacity = capacity * (1.0 + lever_headroom)
        if occupied > effective_capacity:
            exceeded_after_levers = True

    out_flags = dict(flags or {})
    out_flags.setdefault("capacityExceededAfterLevers", exceeded_after_levers)
    return {"resources": resources, "flags": out_flags}


def summarize_kpis(state: dict[str, Any]) -> dict[str, float]:
    """Summarise a projected state into headline KPIs."""
    resources = state.get("resources", {})
    total_shortfall = sum(int(dim.get("shortfall", 0)) for dim in resources.values())
    finite_utils = [
        float(dim.get("utilization", 0.0))
        for dim in resources.values()
        if dim.get("utilization") not in (None, float("inf"))
    ]
    peak = max(finite_utils) if finite_utils else 0.0
    return {
        "peakUtilization": round(peak, 4),
        "totalShortfall": float(total_shortfall),
        "resourcesOverThreshold": float(
            sum(1 for u in finite_utils if u >= 0.90)
        ),
    }
