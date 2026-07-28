"""Build the Backstage opportunity-pipeline fixture for hcc-app-fluent.

Reads the committed Sprint 33 D1 synthetic Opportunity dataset and emits a
small, byte-stable app fixture with pipeline metrics plus table rows. The app
uses this committed JSON in CI/dev, so the Backstage view has no live data
dependency.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

AS_OF = "2026-07-28"

STAGE_WEIGHTS = {
    "new": 0.1,
    "evaluating": 0.25,
    "qualified": 0.5,
    "onboarding": 0.8,
    "won": 1.0,
    "disqualified": 0.0,
    "lost": 0.0,
}

OPEN_STATUSES = {"new", "evaluating", "qualified", "onboarding"}

DEFAULT_DATASET = (
    Path(__file__).resolve().parents[2] / "data" / "synthetic" / "bva" / "bva-opportunities.json"
)

DEFAULT_OUT = (
    Path(__file__).resolve().parents[2]
    / "apps"
    / "hcc-app-fluent"
    / "src"
    / "data"
    / "opportunity"
    / "opportunity-demo.json"
)


def _load_opportunities(repo_root: Path) -> list[dict[str, Any]]:
    dataset_path = repo_root / "data" / "synthetic" / "bva" / "bva-opportunities.json"
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("opportunities"), list):
        return payload["opportunities"]
    raise ValueError(f"{dataset_path}: expected a list or object with opportunities list")


def _roi_pct(opportunity: dict[str, Any]) -> float | None:
    metrics = (opportunity.get("bvaResult") or {}).get("metrics") or {}
    roi = metrics.get("roiPct")
    return float(roi) if isinstance(roi, int | float) and not isinstance(roi, bool) else None


def _latest_event(opportunity: dict[str, Any]) -> dict[str, str] | None:
    history = opportunity.get("history") or []
    if not history:
        return None
    latest = max(history, key=lambda item: item.get("at", ""))
    return {
        "at": str(latest.get("at", "")),
        "event": str(latest.get("event", "")),
        "by": str(latest.get("by", "")),
    }


def _po_verdict(opportunity: dict[str, Any]) -> str | None:
    verdict = opportunity.get("poVerdict")
    if not isinstance(verdict, dict):
        return None
    value = verdict.get("verdict")
    return str(value) if value is not None else None


def _status_counts(opportunities: list[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in STAGE_WEIGHTS}
    for opportunity in opportunities:
        status = str(opportunity["status"])
        counts[status] = counts.get(status, 0) + 1
    return counts


def _weighted_roi(opportunities: list[dict[str, Any]]) -> dict[str, Any]:
    weighted_sum = 0.0
    weight_sum = 0.0
    opportunity_count = 0
    for opportunity in opportunities:
        roi = _roi_pct(opportunity)
        weight = STAGE_WEIGHTS.get(str(opportunity["status"]), 0.0)
        if roi is None or weight <= 0:
            continue
        weighted_sum += roi * weight
        weight_sum += weight
        opportunity_count += 1
    value = round(weighted_sum / weight_sum, 2) if weight_sum else None
    return {
        "value": value,
        "opportunityCount": opportunity_count,
        "weightSum": round(weight_sum, 2),
    }


def _opportunity_row(opportunity: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": opportunity["id"],
        "hospitalName": opportunity["hospitalName"],
        "archetype": opportunity["archetype"],
        "status": opportunity["status"],
        "language": opportunity["language"],
        "roiPct": _roi_pct(opportunity),
        "poVerdict": _po_verdict(opportunity),
        "latestEvent": _latest_event(opportunity),
    }


def build_dataset(repo_root: Path) -> dict[str, Any]:
    opportunities = _load_opportunities(repo_root)
    weighted_roi = _weighted_roi(opportunities)

    return {
        "generatedAt": AS_OF,
        "sourcePath": "data/synthetic/bva/bva-opportunities.json",
        "pipeline": {
            "total": len(opportunities),
            "open": sum(1 for opportunity in opportunities if opportunity["status"] in OPEN_STATUSES),
            "statusCounts": _status_counts(opportunities),
            "weightedRoiPct": weighted_roi["value"],
            "weightedRoiOpportunityCount": weighted_roi["opportunityCount"],
            "weightedRoiWeightSum": weighted_roi["weightSum"],
            "stageWeights": STAGE_WEIGHTS,
        },
        "opportunities": sorted((_opportunity_row(opportunity) for opportunity in opportunities), key=lambda row: row["id"]),
    }


def write_dataset(dataset: dict[str, Any], out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(dataset, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build the app opportunity-pipeline fixture.")
    parser.add_argument("--repo-root", default=".", type=Path)
    parser.add_argument("--out", default=DEFAULT_OUT, type=Path)
    args = parser.parse_args(argv)

    dataset = build_dataset(args.repo_root.resolve())
    write_dataset(dataset, args.out.resolve())
    print(
        f"wrote {args.out} "
        f"({dataset['pipeline']['total']} opportunities, "
        f"{dataset['pipeline']['weightedRoiPct']} weighted ROI)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
