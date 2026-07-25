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
    m = re.search(r"Total Annual Run Cost\*\*\s*\|\s*\*\*(\d+)", _bva_text(repo_root))
    if not m:
        raise ValueError("Total Annual Run Cost not found in docs/BVA.md")
    return float(m.group(1))


def bva_rom_band(repo_root: Path) -> float:
    m = re.search(r"ROM confidence band: plus/minus (\d+) percent", _bva_text(repo_root))
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
