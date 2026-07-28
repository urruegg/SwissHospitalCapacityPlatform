"""Sprint 31 DQA — deterministic gap assessment + the SGA seam (design Sec 6, Sec 8).

**This module contains NO randomness and NEVER produces an LLM estimate.** For a
domain, it emits one ``DC-DQ-GAP-v1`` finding
(``data/synthetic/schema/dc-dq-gap-v1.schema.json``) per dimension whose measured
metric is below its threshold. The ``newSourceNeeded`` flag on a mapped domain is
the FROZEN seam Sprint 32 SGA consumes: SGA's channel intake is triggered only by
a gap with ``newSourceNeeded=true`` (design Sec 8).

DQA is read-only and advisory: it routes each gap to the accountable ``owner`` but
never edits source data — the owner remediates. As with ``trust_score``, the pure
core is clock-free (no ``detected`` timestamp), so the caller stamps time at emit.
"""
from __future__ import annotations

import hashlib
from typing import Any, Dict, List, Optional


def _gap_id(domain: str, dimension: str) -> str:
    """Stable, deterministic gap id derived from ``domain`` + ``dimension``."""
    digest = hashlib.sha256(f"{domain}:{dimension}".encode("utf-8")).hexdigest()
    return "GAP-" + digest[:16]


def _default_owner(domain: str) -> str:
    return f"data-owner:{domain.split('.')[0]}"


def assess_gaps(
    domain: str,
    metrics: Dict[str, float],
    thresholds: Dict[str, float],
    impact_map: Optional[Dict[str, Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Return ``DC-DQ-GAP-v1`` findings for dimensions below their threshold.

    Pure and deterministic: no randomness, no LLM estimate, no I/O, no clock.
    Findings are returned sorted by dimension name for a stable order.

    Args:
        domain: The gold/serving domain assessed (e.g. ``staffing.skills``).
        metrics: Measured value per dimension in ``[0,1]``. A dimension absent
            from ``metrics`` is treated as a maximal gap (value ``0``).
        thresholds: The minimum acceptable value per dimension; only dimensions
            present here are assessed.
        impact_map: Optional per-domain impact metadata (impacted KPIs/agents,
            recommended fill source, ``newSourceNeeded``, ``owner``, ``effort``).
            An unmapped domain defaults to ``newSourceNeeded=False`` and a
            ``data-owner:<top-level>`` owner.
    """
    impact_map = impact_map or {}
    domain_meta = impact_map.get(domain, {})
    gaps: List[Dict[str, Any]] = []
    for dimension, threshold in sorted(thresholds.items()):
        value = metrics.get(dimension, 0.0)
        if value >= threshold:
            continue
        # Impact = normalised shortfall vs threshold, deterministic and in [0,1].
        impact = round((threshold - value) / threshold, 4) if threshold else 1.0
        gaps.append(
            {
                "contractId": "DC-DQ-GAP-v1",
                "gapId": _gap_id(domain, dimension),
                "domain": domain,
                "dimension": dimension,
                "impactedKpi": list(domain_meta.get("impactedKpi", [])),
                "impactedAgents": list(domain_meta.get("impactedAgents", [])),
                "impactScore": impact,
                "recommendedSource": dict(domain_meta.get("recommendedSource", {})),
                "newSourceNeeded": bool(domain_meta.get("newSourceNeeded", False)),
                "owner": domain_meta.get("owner", _default_owner(domain)),
                "effort": domain_meta.get("effort", "M"),
                "status": "open",
            }
        )
    return gaps
