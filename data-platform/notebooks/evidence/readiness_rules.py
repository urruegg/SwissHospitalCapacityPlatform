"""Readiness scoring rules for the Showcase Evidence data product.

Pure functions (no PySpark / no I/O) implementing the T-SHOW / T-PROD scoring
rules from the design spec §6 and ADR-0021. The Fabric ``score_readiness``
notebook imports :func:`score_readiness` and applies it to Silver Delta rows;
keeping the logic here (framework-agnostic) makes it unit-testable with a
byte-stable golden regression fixture.

Design contract (design spec §6):

* **T-SHOW** (synthetic, non-PHI): ``Ready`` if the resource is available (GA or
  Preview) in the chosen showcase region (Switzerland North, else EU fallback)
  and every dependency is likewise available. Flagged ``showcaseOnly`` when the
  resource or any dependency is Preview-only (allowed for synthetic data per
  ADR-0006 scoping).
* **T-PROD** (real PHI): ``Ready`` only if the resource is GA in Switzerland
  North and every dependency is GA there. Otherwise ``Blocked`` with a
  ``blockingReason``.
"""

from __future__ import annotations

from typing import Iterable

SHOWCASE_REGION = "Switzerland North"
FALLBACK_REGION = "West Europe"
PROD_REGION = "Switzerland North"

_AVAILABLE = ("GA", "Preview")


def _availability_index(availability: Iterable[dict]) -> dict[tuple[str, str], str]:
    """Map ``(bomId, region) -> maturity`` (last write wins, then sorted input)."""
    index: dict[tuple[str, str], str] = {}
    for fact in availability:
        index[(fact["bomId"], fact["region"])] = fact["maturity"]
    return index


def _dependency_index(bom_items: Iterable[dict]) -> dict[str, list[str]]:
    deps: dict[str, list[str]] = {}
    for item in bom_items:
        edges = item.get("dependsOn") or []
        deps[item["id"]] = sorted({edge["to"] for edge in edges})
    return deps


def _showcase_maturity(bom_id: str, index: dict[tuple[str, str], str]) -> tuple[str | None, str | None]:
    """Return ``(maturity, region)`` for the best showcase-region availability."""
    for region in (SHOWCASE_REGION, FALLBACK_REGION):
        maturity = index.get((bom_id, region))
        if maturity in _AVAILABLE:
            return maturity, region
    return None, None


def _score_tshow(bom_id: str, index, deps) -> dict:
    maturity, region = _showcase_maturity(bom_id, index)
    if maturity is None:
        return {
            "status": "Blocked",
            "showcaseOnly": False,
            "blockingReason": f"{bom_id} not available in {SHOWCASE_REGION} or {FALLBACK_REGION}",
            "region": SHOWCASE_REGION,
        }

    showcase_only = maturity == "Preview"
    for dep_id in deps.get(bom_id, []):
        dep_maturity, _ = _showcase_maturity(dep_id, index)
        if dep_maturity is None:
            return {
                "status": "Blocked",
                "showcaseOnly": False,
                "blockingReason": f"dependency {dep_id} not available in {SHOWCASE_REGION} or {FALLBACK_REGION}",
                "region": region,
            }
        if dep_maturity == "Preview":
            showcase_only = True

    return {
        "status": "Ready",
        "showcaseOnly": showcase_only,
        "blockingReason": None,
        "region": region,
    }


def _score_tprod(bom_id: str, index, deps) -> dict:
    self_maturity = index.get((bom_id, PROD_REGION))
    if self_maturity != "GA":
        detail = self_maturity or "NotAvailable"
        return {
            "status": "Blocked",
            "showcaseOnly": False,
            "blockingReason": f"{bom_id} is {detail} (not GA) in {PROD_REGION}",
            "region": PROD_REGION,
        }

    for dep_id in deps.get(bom_id, []):
        dep_maturity = index.get((dep_id, PROD_REGION))
        if dep_maturity != "GA":
            detail = dep_maturity or "NotAvailable"
            return {
                "status": "Blocked",
                "showcaseOnly": False,
                "blockingReason": f"dependency {dep_id} is {detail} (not GA) in {PROD_REGION}",
                "region": PROD_REGION,
            }

    return {
        "status": "Ready",
        "showcaseOnly": False,
        "blockingReason": None,
        "region": PROD_REGION,
    }


def score_readiness(bom_items: list[dict], availability: list[dict]) -> list[dict]:
    """Return sorted readiness-snapshot rows for both tracks.

    Row shape: ``{bomId, track, region, status, showcaseOnly, blockingReason}``.
    Output is byte-stable for a fixed input (rows sorted by ``(bomId, track)``).
    """
    index = _availability_index(availability)
    deps = _dependency_index(bom_items)

    rows: list[dict] = []
    for item in bom_items:
        bom_id = item["id"]
        for track, scorer in (("T-SHOW", _score_tshow), ("T-PROD", _score_tprod)):
            result = scorer(bom_id, index, deps)
            rows.append(
                {
                    "bomId": bom_id,
                    "track": track,
                    "region": result["region"],
                    "status": result["status"],
                    "showcaseOnly": result["showcaseOnly"],
                    "blockingReason": result["blockingReason"],
                }
            )

    return sorted(rows, key=lambda r: (r["bomId"], r["track"]))


def aggregate_readiness(rows: list[dict]) -> list[dict]:
    """Aggregate to ``% Ready`` per track (design spec §6 headline gauge).

    Returns sorted ``{track, readyCount, total, readyPct}`` rows plus the
    GA-parity gap between T-SHOW and T-PROD ready counts.
    """
    totals: dict[str, list[int]] = {}
    for row in rows:
        ready, total = totals.setdefault(row["track"], [0, 0])
        totals[row["track"]] = [ready + (1 if row["status"] == "Ready" else 0), total + 1]

    summary = []
    for track in sorted(totals):
        ready, total = totals[track]
        summary.append(
            {
                "track": track,
                "readyCount": ready,
                "total": total,
                "readyPct": round(100.0 * ready / total, 1) if total else 0.0,
            }
        )

    ready_by_track = {s["track"]: s["readyCount"] for s in summary}
    gap = ready_by_track.get("T-SHOW", 0) - ready_by_track.get("T-PROD", 0)
    summary.append({"track": "GA-parity-gap", "readyCount": gap, "total": 0, "readyPct": 0.0})
    return summary
