"""Deterministic unit tests for the BVA Opportunity Gold projection."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DATA_PLATFORM = ROOT / "data-platform"
if str(DATA_PLATFORM) not in sys.path:
    sys.path.insert(0, str(DATA_PLATFORM))

from bva.opportunity import load_dataset
from bva.opportunity_projection import STAGE_WEIGHTS, build_all, build_opportunity_rows, build_pipeline_metrics


EXPECTED_WEIGHTED_ROI = 35.93


def _dataset() -> list[dict]:
    return load_dataset()


def _row_by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["id"]: row for row in rows}


def _metric_by_id(rows: list[dict]) -> dict[str, dict]:
    return {row["metric_id"]: row for row in rows}


def test_opportunity_rows_match_dataset_count() -> None:
    opportunities = _dataset()

    rows = build_opportunity_rows(opportunities)

    assert len(rows) == len(opportunities)


def test_known_opportunity_is_flattened_with_latest_history_event() -> None:
    rows = _row_by_id(build_opportunity_rows(_dataset()))

    row = rows["opp-curanova-university-hospital-0001"]

    assert row["hospitalName"] == "CuraNova University Hospital"
    assert row["status"] == "won"
    assert row["roiPct"] == 42.5
    assert row["paybackMonths"] == 14.0
    assert row["tco3yChf"] == 5_050_000.0
    assert row["npvChf"] == 3_120_000.0
    assert row["hasBvaResult"] is True
    assert row["latestEventAt"] == "2026-07-29T09:00:00Z"
    assert row["latestEvent"] == "commercial approval recorded"
    assert row["historyCount"] == 3
    assert row["poVerdict"] == "go"


def test_rows_are_sorted_deterministically_by_id() -> None:
    rows = build_opportunity_rows(reversed(_dataset()))

    ids = [row["id"] for row in rows]

    assert ids == sorted(ids)


def test_pipeline_status_counts_sum_to_total_and_open_count() -> None:
    metrics = _metric_by_id(build_pipeline_metrics(_dataset()))

    status_total = sum(row["opportunity_count"] for key, row in metrics.items() if key.startswith("status:"))

    assert metrics["total"]["opportunity_count"] == len(_dataset())
    assert status_total == metrics["total"]["opportunity_count"]
    assert metrics["open"]["opportunity_count"] == 4
    assert metrics["weighted_roi_pct"]["stage_weights"] == STAGE_WEIGHTS


def test_weighted_roi_uses_only_records_with_roi_and_positive_stage_weight() -> None:
    metrics = _metric_by_id(build_pipeline_metrics(_dataset()))

    assert metrics["weighted_roi_pct"] == {
        "metric_id": "weighted_roi_pct",
        "metric": "weighted_roi_pct",
        "value": EXPECTED_WEIGHTED_ROI,
        "opportunity_count": 3,
        "weight_sum": 2.3,
        "stage_weights": STAGE_WEIGHTS,
    }


def test_records_without_bva_result_have_null_roi_and_do_not_enter_weighted_roi() -> None:
    rows = _row_by_id(build_opportunity_rows(_dataset()))
    metrics = _metric_by_id(build_pipeline_metrics(_dataset()))

    assert rows["opp-spitex-zurichsee-0001"]["hasBvaResult"] is False
    assert rows["opp-spitex-zurichsee-0001"]["roiPct"] is None
    assert rows["opp-hopital-fribourg-0001"]["roiPct"] is None
    assert metrics["weighted_roi_pct"]["opportunity_count"] == 3


def test_build_all_is_byte_stable_across_runs() -> None:
    first = build_all(_dataset())
    second = build_all(_dataset())

    assert json.dumps(first, sort_keys=False) == json.dumps(second, sort_keys=False)
    assert set(first) == {"bva_opportunity", "bva_opportunity_pipeline"}
