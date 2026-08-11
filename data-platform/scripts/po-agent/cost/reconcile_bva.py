"""WS-C Class C cost: reconcile effective cost to the BVA baseline.

Presents cost answers as **ranges within the BVA +/- 30% band** with an
as-of stamp, and **refuses to extrapolate** a bounded feed window into a
longer horizon (FR-POA-006). Emits the frozen WS-G0 ``GroundedChunk``
(classId ``C``).

The BVA annual run-cost baseline and the ROM confidence band are read
from ``docs/BVA.md`` (Sprint 15, ADR-0025). All figures are synthetic
ROM assumptions, not procurement commitments; no PHI.
"""

from __future__ import annotations

import datetime as _dt
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

CLASS_ID = "C"
BVA_ANCHOR = "docs/BVA.md#recurring-annual-costs"


@dataclass
class CostObservation:
    """A measured cost run-rate over a bounded feed window."""

    amount: float
    currency: str
    window_start: str
    window_end: str
    feed: str
    as_of: str
    ok: bool = True


# --------------------------------------------------------------------------
# BVA baseline parsing (read-only)
# --------------------------------------------------------------------------

def _bva_text(repo_root: Path) -> str:
    return (repo_root / "docs" / "BVA.md").read_text(encoding="utf-8")


def bva_annual_run_cost(repo_root: Path) -> float:
    # Case-insensitive and comma-tolerant: docs/BVA.md is human-edited prose
    # (Sprint 40 re-baseline lower-cased "annual run cost" and switched to
    # comma-grouped numbers, e.g. "1,250,000" -- both changes are a legitimate
    # authoring choice, so the parser tolerates them rather than constraining
    # the document's wording to a brittle exact match).
    m = re.search(
        r"total annual run cost\*\*\s*\|\s*\*\*([\d,]+)",
        _bva_text(repo_root),
        re.IGNORECASE,
    )
    if not m:
        raise ValueError("Total Annual Run Cost not found in docs/BVA.md")
    return float(m.group(1).replace(",", ""))


def bva_rom_band(repo_root: Path) -> float:
    m = re.search(
        r"ROM confidence band[:\s]*(?:is\s*)?(?:plus/minus|\u00b1)\s*(\d+)\s*percent",
        _bva_text(repo_root),
        re.IGNORECASE,
    )
    return (float(m.group(1)) / 100.0) if m else 0.30


# --------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------

def rom_range(amount: float, band: float = 0.30) -> tuple[float, float]:
    """The ROM +/- band range around a measured amount."""

    return (amount * (1.0 - band), amount * (1.0 + band))


def _days(start: str, end: str) -> int:
    d0 = _dt.date.fromisoformat(start)
    d1 = _dt.date.fromisoformat(end)
    return (d1 - d0).days + 1  # inclusive window


def _as_datetime(value: str) -> str:
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return f"{value}T00:00:00Z"
    return value


def _grounded_chunk(
    *,
    text: str,
    source_ref: str,
    as_of: str,
    liveness: str,
    status: str,
    confidence: float,
    language: str = "en",
) -> dict[str, Any]:
    return {
        "classId": CLASS_ID,
        "text": text,
        "citation": {"sourceRef": source_ref, "anchor": BVA_ANCHOR},
        "asOf": _as_datetime(as_of),
        "liveness": liveness,
        "status": status,
        "confidence": confidence,
        "language": language,
    }


# --------------------------------------------------------------------------
# Reconcile
# --------------------------------------------------------------------------

def reconcile_bva(
    observation: CostObservation,
    repo_root: Path,
    requested_horizon_end: Optional[str] = None,
) -> dict[str, Any]:
    """Reconcile a measured cost run-rate against the BVA band.

    Parameters
    ----------
    observation:
        Measured effective cost (Azure + Copilot) over a bounded window.
    requested_horizon_end:
        If a caller asks for a horizon that extends beyond the feed
        window, the answer is *refused* (no extrapolation).
    """

    band = bva_rom_band(repo_root)
    feed_ref = f"{observation.feed} @ {observation.as_of}"

    # Refuse to extrapolate beyond the observed feed window.
    if requested_horizon_end is not None and (
        _dt.date.fromisoformat(requested_horizon_end)
        > _dt.date.fromisoformat(observation.window_end)
    ):
        text = (
            f"Requested horizon ends {requested_horizon_end}, beyond the "
            f"measured feed window {observation.window_start}..{observation.window_end}. "
            f"Refusing to extrapolate: cost answers are bounded to the feed "
            f"window and cannot be projected forward without a longer feed. "
            f"As of {observation.as_of}."
        )
        return _grounded_chunk(
            text=text,
            source_ref=feed_ref,
            as_of=observation.as_of,
            liveness="live",
            status="partial",
            confidence=0.4,
        )

    # Degrade to snapshot if the live feed was unavailable.
    if not observation.ok:
        annual = bva_annual_run_cost(repo_root)
        lo, hi = rom_range(annual, band)
        text = (
            f"Live cost feed unavailable; showing the BVA annual run-cost "
            f"baseline range {lo:,.0f}-{hi:,.0f} {observation.currency} "
            f"(+/- {band:.0%} ROM band) as a snapshot. As of {observation.as_of}."
        )
        return _grounded_chunk(
            text=text,
            source_ref="docs/BVA.md (snapshot)",
            as_of=observation.as_of,
            liveness="snapshot",
            status="partial",
            confidence=0.5,
        )

    # Pro-rate the BVA annual band to the feed window for comparison.
    annual = bva_annual_run_cost(repo_root)
    window_fraction = _days(observation.window_start, observation.window_end) / 365.0
    band_lo = annual * (1.0 - band) * window_fraction
    band_hi = annual * (1.0 + band) * window_fraction

    lo, hi = rom_range(observation.amount, band)
    within = band_lo <= observation.amount <= band_hi
    status = "verified" if within else "requires-validation"
    confidence = 0.8 if within else 0.5
    verdict = (
        "within the BVA band"
        if within
        else "OUTSIDE the BVA band [drift]"
    )

    text = (
        f"Effective cost for {observation.window_start}..{observation.window_end} "
        f"is {observation.amount:,.0f} {observation.currency}, presented as a ROM "
        f"range {lo:,.0f}-{hi:,.0f} {observation.currency} (+/- {band:.0%}). "
        f"This is {verdict}: pro-rated BVA band for the window is "
        f"{band_lo:,.0f}-{band_hi:,.0f} {observation.currency}. "
        f"Not extrapolated beyond the feed window. As of {observation.as_of}."
    )
    return _grounded_chunk(
        text=text,
        source_ref=feed_ref,
        as_of=observation.as_of,
        liveness="live",
        status=status,
        confidence=confidence,
    )


# --------------------------------------------------------------------------
# Measured build-cost evidence (BVA evidence & narrative master data)
# --------------------------------------------------------------------------

_EVIDENCE_STATUS_TO_CHUNK_STATUS = {
    "measured": "verified",
    "measured_extrapolated": "verified",
    "telemetry": "verified",
    "mixed": "partial",
    "modelled_on_measured": "partial",
    "estimated": "requires-validation",
    "modelled": "requires-validation",
    "ROM": "requires-validation",
    "derived": "requires-validation",
}

_EVIDENCE_STATUS_CONFIDENCE = {
    "measured": 0.9,
    "measured_extrapolated": 0.75,
    "telemetry": 0.7,
    "mixed": 0.7,
    "modelled_on_measured": 0.6,
    "estimated": 0.5,
    "modelled": 0.4,
    "ROM": 0.4,
    "derived": 0.6,
}


def _evidence_grounding_module(repo_root: Path):
    """Load `bva.evidence_grounding.build_evidence_gold_tables` by file path.

    Loaded relative to the caller-supplied ``repo_root`` (never `__file__`):
    this file is copied flat into the container image (``/app/cost/...``),
    where `__file__`-relative ``.parents[N]`` climbing cannot reach
    ``data-platform/bva/`` at all (that tree is not part of the runtime
    image's normal Python source layout). ``repo_root`` is resolved once by
    ``app.py``'s ``_resolve_repo_root()``, which already knows how to find
    the subset of docs/data/data-platform that runtime/Dockerfile copies
    into ``/app/repo/`` for exactly this purpose -- reuse it instead of
    duplicating the dev-tree-vs-container detection here.
    """
    import importlib.util

    module_path = repo_root / "data-platform" / "bva" / "evidence_grounding.py"
    spec = importlib.util.spec_from_file_location("bva_evidence_grounding", module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load evidence_grounding module from {module_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_evidence_gold_tables


def build_cost_evidence_chunk(repo_root: Path, *, as_of: str = "2026-08-11T00:00:00Z") -> dict[str, Any]:
    """The measured 90-day showcase build-cost total as a Class-C `GroundedChunk`.

    Distinct from `reconcile_bva()` above, which reconciles the *live, ongoing
    Azure/Copilot run-rate* to the BVA annual budget baseline. This answers a
    different question -- "what did the Curavias showcase cost to build" --
    sourced from the committed, `evidence_status`-labelled master data rather
    than a live cost-management probe, so it is always available even when
    the live Azure/Copilot feeds are unreachable (unlike `reconcile_bva`,
    there is no snapshot-degradation path to design for here).
    """
    build_evidence_gold_tables = _evidence_grounding_module(repo_root)
    bva_dir = repo_root / "data" / "master-data" / "bva"
    tables = build_evidence_gold_tables(bva_dir)
    rows = {row["build_cost_id"]: row for row in tables["bva_evidence_build_cost_actual_fact"]}
    total = rows["BC-999"]
    components = [row for row in rows.values() if row["build_cost_id"] != "BC-999"]
    components.sort(key=lambda r: -float(r["amount_chf"] or 0))

    breakdown = ", ".join(
        f"{c['cost_element']} {c['amount_chf']:,.0f} CHF ({c['share_pct']}%, {c['evidence_status']})"
        for c in components
    )
    text = (
        f"The Curavias showcase cost {total['amount_chf']:,.0f} CHF to build over "
        f"90 days ({total['period_start']}..{total['period_end']}). Breakdown: "
        f"{breakdown}. This is the measured cost of the art-of-the-possible "
        f"showcase itself, not a projected hospital-implementation cost."
    )
    evidence_status = str(total["evidence_status"])
    return _grounded_chunk(
        text=text,
        source_ref="data/master-data/bva/fact_build_cost_actual.csv (BC-999)",
        as_of=as_of,
        liveness="snapshot",
        status=_EVIDENCE_STATUS_TO_CHUNK_STATUS.get(evidence_status, "requires-validation"),
        confidence=_EVIDENCE_STATUS_CONFIDENCE.get(evidence_status, 0.5),
    )


def combined_run_rate(
    azure_amount: float,
    copilot_amount: float,
    currency: str,
    window_start: str,
    window_end: str,
    as_of: str,
    feed: str = "Azure Cost Management + GitHub Copilot usage",
) -> CostObservation:
    """Sum the read-only Azure + Copilot feeds into one run-rate observation."""

    return CostObservation(
        amount=float(azure_amount) + float(copilot_amount),
        currency=currency,
        window_start=window_start,
        window_end=window_end,
        feed=feed,
        as_of=as_of,
    )
