"""Deterministic unit tests for the BVA evidence & narrative Gold transforms."""
from __future__ import annotations

from pathlib import Path

from bva.evidence_grounding import (
    VALID_EVIDENCE_STATUS,
    build_evidence_gold_tables,
    build_gold_table,
)


def _real_bva_dir() -> Path:
    path = Path(__file__).resolve().parents[3] / "data" / "master-data" / "bva"
    assert path.name == "bva"
    assert (path / "fact_build_cost_actual.csv").exists()
    return path


def _by_id(rows: list[dict], id_column: str) -> dict[str, dict]:
    return {row[id_column]: row for row in rows}


def test_build_evidence_gold_tables_covers_all_ten_sources() -> None:
    tables = build_evidence_gold_tables(_real_bva_dir())

    assert set(tables) == {
        "bva_evidence_assumption_dim",
        "bva_evidence_cost_element_dim",
        "bva_evidence_source_dim",
        "bva_evidence_azure_cost_weekly_fact",
        "bva_evidence_build_cost_actual_fact",
        "bva_evidence_copilot_usage_weekly_fact",
        "bva_evidence_effort_fact",
        "bva_evidence_roi_scenario_fact",
        "bva_evidence_unit_economics_fact",
        "bva_evidence_value_lever_fact",
    }
    for rows in tables.values():
        assert len(rows) > 0


def test_build_cost_actual_total_is_measured_21286_chf() -> None:
    tables = build_evidence_gold_tables(_real_bva_dir())
    rows = _by_id(tables["bva_evidence_build_cost_actual_fact"], "build_cost_id")

    total = rows["BC-999"]
    assert total["amount_chf"] == 21286.0
    assert total["evidence_status"] == "mixed"

    human = rows["BC-001"]
    assert human["amount_chf"] == 18831.0
    assert human["evidence_status"] == "measured"


def test_roi_scenario_missing_payback_months_is_none_not_zero() -> None:
    tables = build_evidence_gold_tables(_real_bva_dir())
    rows = _by_id(tables["bva_evidence_roi_scenario_fact"], "scenario_id")

    # SC-V1-CONS has no payback_months value in the source CSV.
    assert rows["SC-V1-CONS"]["payback_months"] is None
    assert rows["SC-V2-BASE"]["payback_months"] == 3.6


def test_copilot_usage_empty_cloud_store_columns_are_none() -> None:
    tables = build_evidence_gold_tables(_real_bva_dir())
    rows = _by_id(tables["bva_evidence_copilot_usage_weekly_fact"], "copilot_usage_id")

    cloud_row = rows["CP-2026-05-04"]
    assert cloud_row["store"] == "cloud"
    assert cloud_row["cache_read_tokens"] is None
    assert cloud_row["reasoning_tokens"] is None
    assert cloud_row["aiu_consumed"] is None
    assert cloud_row["input_tokens"] == 476875.0


def test_rows_are_sorted_by_id_column() -> None:
    tables = build_evidence_gold_tables(_real_bva_dir())
    ids = [row["assumption_id"] for row in tables["bva_evidence_assumption_dim"]]
    assert ids == sorted(ids)


def test_all_evidence_status_values_are_in_the_documented_vocabulary() -> None:
    tables = build_evidence_gold_tables(_real_bva_dir())
    for table_name, rows in tables.items():
        for row in rows:
            status = row.get("evidence_status")
            if status is not None:
                assert status in VALID_EVIDENCE_STATUS, f"{table_name}: unexpected evidence_status {status!r}"


def test_build_gold_table_is_a_pure_function_of_its_rows() -> None:
    rows = [
        {"assumption_id": "AS-002", "value": "10"},
        {"assumption_id": "AS-001", "value": ""},
    ]
    result = build_gold_table("dim_assumption", rows)

    assert [r["assumption_id"] for r in result] == ["AS-001", "AS-002"]
    assert result[0]["value"] is None
    assert result[1]["value"] == 10.0
