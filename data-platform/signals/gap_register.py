"""Sprint 32 SGA — deterministic Signal Gap Register (design §7, FR-SIG-001).

Referenced-but-unwired channels + DQ-demanded new sources, ranked. DQ-demanded
gaps rank first (they carry a measured impact score). NO randomness.
"""
from __future__ import annotations

from typing import Any, Dict, List, Set


def build_gap_register(
    referenced: Set[str],
    wired: Set[str],
    dq_gaps: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Return a ranked list of signal gaps (highest rank first)."""
    dq_by_kind = {
        g["recommendedSource"]["kind"]: g
        for g in dq_gaps
        if g.get("newSourceNeeded") and g.get("recommendedSource", {}).get("kind")
    }
    rows: List[Dict[str, Any]] = []
    for signal in sorted((referenced - wired) | set(dq_by_kind)):
        g = dq_by_kind.get(signal)
        rows.append({
            "signal": signal,
            "demandedByDq": g is not None,
            # rank: DQ impact (0..1) + 0.5 base for referenced-but-unwired
            "rank": round((g["impactScore"] if g else 0.0) + (0.5 if signal in referenced else 0.0), 4),
        })
    return sorted(rows, key=lambda r: (-r["rank"], r["signal"]))
