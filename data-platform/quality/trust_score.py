"""Sprint 31 DQA — deterministic, versioned trust score (design Sec 6).

**This module contains NO randomness and NEVER produces an LLM estimate.** The
trust score is a pure function of its dimension inputs: the same
``(domain, dimensions, weights)`` always produce the same score dict. It mirrors
the determinism guarantees of
``data-platform/decision/impact/compute_expected_impact.py``.

The score is the weighted aggregate of the eight canonical trust dimensions
(design Sec 6). Weights default to equal per dimension; a decision class may pass
its own ADR-ratified weighting (``docs/adr/0053-dqa-trust-score-model.md``). The
result is shaped as a ``DC-DQ-TRUSTSCORE-v1`` record
(``data/synthetic/schema/dc-dq-trustscore-v1.schema.json``) minus ``asOf``, which
the caller stamps at emit time so the pure core stays clock-free and
deterministic.
"""
from __future__ import annotations

from typing import Dict, Optional

#: The eight canonical trust dimensions, in a fixed order (design Sec 6).
DIMENSIONS = (
    "completeness",
    "timeliness",
    "validity",
    "uniqueness",
    "consistency",
    "lineage_integrity",
    "provenance",
    "ontology_mapping",
)

#: Deterministic trust-score model version. Bump when weights/dimensions change.
MODEL_VERSION = "trustscore-v1"

_EQUAL_WEIGHT = 1.0 / len(DIMENSIONS)


def _is_unit_number(value: object) -> bool:
    return (
        isinstance(value, (int, float))
        and not isinstance(value, bool)
        and 0.0 <= float(value) <= 1.0
    )


def _validate_dimensions(dimensions: Dict[str, float]) -> None:
    for dim in DIMENSIONS:
        if dim not in dimensions:
            raise ValueError(f"missing dimension {dim!r}")
        if not _is_unit_number(dimensions[dim]):
            raise ValueError(
                f"dimension {dim!r} must be a number in [0,1], got {dimensions[dim]!r}"
            )


def _resolve_weights(weights: Optional[Dict[str, float]]) -> Dict[str, float]:
    if weights is None:
        return {dim: _EQUAL_WEIGHT for dim in DIMENSIONS}
    for dim in DIMENSIONS:
        if dim not in weights:
            raise ValueError(f"weights missing dimension {dim!r}")
    total = sum(float(weights[dim]) for dim in DIMENSIONS)
    if total <= 0.0:
        raise ValueError("sum of weights must be > 0")
    return {dim: float(weights[dim]) for dim in DIMENSIONS}


def trust_score(
    domain: str,
    dimensions: Dict[str, float],
    weights: Optional[Dict[str, float]] = None,
    decision_class: Optional[str] = None,
) -> Dict[str, object]:
    """Return a ``DC-DQ-TRUSTSCORE-v1``-shaped dict for one ``domain``.

    Pure and deterministic: no randomness, no LLM estimate, no I/O, no clock.

    Args:
        domain: The gold/serving domain being assessed (e.g. ``staffing.skills``).
        dimensions: Every dimension in :data:`DIMENSIONS` mapped to a value in ``[0,1]``.
        weights: Optional per-dimension weights (must cover every dimension); a
            decision class supplies its ADR-ratified weighting here. Defaults to
            equal weights.
        decision_class: Optional decision class label, echoed into the record.

    Raises:
        ValueError: If a dimension is missing, out of ``[0,1]``, boolean, or the
            supplied weights are incomplete or sum to zero.
    """
    _validate_dimensions(dimensions)
    resolved = _resolve_weights(weights)
    total_weight = sum(resolved[dim] for dim in DIMENSIONS)
    score = sum(resolved[dim] * float(dimensions[dim]) for dim in DIMENSIONS) / total_weight
    return {
        "contractId": "DC-DQ-TRUSTSCORE-v1",
        "domain": domain,
        "score": round(score, 4),
        "dimensions": {dim: float(dimensions[dim]) for dim in DIMENSIONS},
        "decisionClass": decision_class,
        "modelVersion": MODEL_VERSION,
    }
