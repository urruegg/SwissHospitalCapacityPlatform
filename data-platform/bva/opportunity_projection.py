"""Pure Cosmos-to-Gold projection for Sprint 33 WS-D BVA Opportunities.

Cosmos DB remains the system of record for ``Opportunity`` documents. This
module only flattens already-read documents into deterministic analytics rows
for the one-way ``gold.bva_opportunity`` projection and its companion
``gold.bva_opportunity_pipeline`` metric table.

Weighted ROI is a stage-probability-weighted mean over opportunities that have
both a numeric ``bvaResult.metrics.roiPct`` and a positive status weight:

``sum(STAGE_WEIGHTS[status] * roiPct) / sum(STAGE_WEIGHTS[status])``.

Records with no ROI, unknown statuses, or zero-weight terminal statuses are
excluded from the weighted ROI denominator. Monetary and percentage values are
rounded to two decimals, and all output rows are sorted for byte stability.
"""
from __future__ import annotations

from typing import Iterable, Mapping

STAGE_WEIGHTS: dict[str, float] = {
    "new": 0.1,
    "evaluating": 0.25,
    "qualified": 0.5,
    "onboarding": 0.8,
    "won": 1.0,
    "disqualified": 0.0,
    "lost": 0.0,
}

_OPEN_STATUSES = {"new", "evaluating", "qualified", "onboarding"}


def _num_or_none(value: object) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return round(float(value), 2)
    except (TypeError, ValueError):
        return None


def _metrics(doc: Mapping) -> Mapping:
    bva_result = doc.get("bvaResult")
    if not isinstance(bva_result, Mapping):
        return {}
    metrics = bva_result.get("metrics")
    return metrics if isinstance(metrics, Mapping) else {}


def _latest_history(history: object) -> tuple[str | None, str | None]:
    if not isinstance(history, list) or not history:
        return None, None
    entries = [entry for entry in history if isinstance(entry, Mapping)]
    if not entries:
        return None, None
    latest = max(entries, key=lambda entry: str(entry.get("at", "")))
    return (
        str(latest["at"]) if latest.get("at") is not None else None,
        str(latest["event"]) if latest.get("event") is not None else None,
    )


def _po_verdict(doc: Mapping) -> str | None:
    verdict = doc.get("poVerdict")
    if not isinstance(verdict, Mapping):
        return None
    value = verdict.get("verdict")
    return str(value) if value is not None else None


def build_opportunity_rows(opportunities: Iterable[Mapping]) -> list[dict]:
    """Return one flat ``gold.bva_opportunity`` row per Opportunity document."""
    rows: list[dict] = []
    for doc in opportunities:
        metrics = _metrics(doc)
        history = doc.get("history")
        latest_at, latest_event = _latest_history(history)
        rows.append(
            {
                "id": doc.get("id"),
                "hospitalName": doc.get("hospitalName"),
                "archetype": doc.get("archetype"),
                "status": doc.get("status"),
                "language": doc.get("language"),
                "createdAt": doc.get("createdAt"),
                "createdBy": doc.get("createdBy"),
                "latestEventAt": latest_at,
                "latestEvent": latest_event,
                "historyCount": len(history) if isinstance(history, list) else 0,
                "poVerdict": _po_verdict(doc),
                "roiPct": _num_or_none(metrics.get("roiPct")),
                "paybackMonths": _num_or_none(metrics.get("paybackMonths")),
                "tco3yChf": _num_or_none(metrics.get("tco3yChf")),
                "npvChf": _num_or_none(metrics.get("npvChf")),
                "hasBvaResult": isinstance(doc.get("bvaResult"), Mapping),
            }
        )
    rows.sort(key=lambda row: str(row.get("id", "")))
    return rows


def build_pipeline_metrics(opportunities: Iterable[Mapping]) -> list[dict]:
    """Return deterministic aggregate metric rows for Opportunity pipeline reporting."""
    docs = list(opportunities)
    status_counts: dict[str, int] = {}
    weighted_sum = 0.0
    weight_sum = 0.0
    weighted_count = 0

    for doc in docs:
        status = str(doc.get("status", ""))
        status_counts[status] = status_counts.get(status, 0) + 1
        roi = _num_or_none(_metrics(doc).get("roiPct"))
        weight = STAGE_WEIGHTS.get(status, 0.0)
        if roi is not None and weight > 0.0:
            weighted_sum += weight * roi
            weight_sum += weight
            weighted_count += 1

    known_statuses = [status for status in STAGE_WEIGHTS if status in status_counts]
    unknown_statuses = sorted(status for status in status_counts if status not in STAGE_WEIGHTS)
    rows = [
        {
            "metric_id": f"status:{status}",
            "metric": "status_count",
            "status": status,
            "opportunity_count": status_counts[status],
        }
        for status in [*known_statuses, *unknown_statuses]
    ]
    rows.extend(
        [
            {
                "metric_id": "open",
                "metric": "open_count",
                "opportunity_count": sum(1 for doc in docs if str(doc.get("status", "")) in _OPEN_STATUSES),
            },
            {
                "metric_id": "total",
                "metric": "total_count",
                "opportunity_count": len(docs),
            },
            {
                "metric_id": "weighted_roi_pct",
                "metric": "weighted_roi_pct",
                "value": round(weighted_sum / weight_sum, 2) if weight_sum else None,
                "opportunity_count": weighted_count,
                "weight_sum": round(weight_sum, 2),
                "stage_weights": STAGE_WEIGHTS,
            },
        ]
    )
    rows.sort(key=lambda row: str(row["metric_id"]))
    return rows


def build_all(opportunities: Iterable[Mapping]) -> dict[str, list[dict]]:
    """Return both WS-D Opportunity Gold projection tables."""
    docs = list(opportunities)
    return {
        "bva_opportunity": build_opportunity_rows(docs),
        "bva_opportunity_pipeline": build_pipeline_metrics(docs),
    }


def load_and_build(path=None) -> dict[str, list[dict]]:
    """Load the D1 Opportunity dataset and return both Gold projection tables."""
    from bva.opportunity import load_dataset

    return build_all(load_dataset(path))


__all__ = [
    "STAGE_WEIGHTS",
    "build_all",
    "build_opportunity_rows",
    "build_pipeline_metrics",
    "load_and_build",
]
