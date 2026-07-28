"""Deterministic unit tests for the BVA cost-basis Gold transforms."""
from __future__ import annotations

import json
from pathlib import Path

from bva.costbasis import (
    build_all,
    build_baseline_kpi,
    build_cost_fact,
    build_effort_fact,
    consistency_report,
)


def _real_bva_dir() -> Path:
    path = Path(__file__).resolve().parents[3] / "data" / "master-data" / "bva"
    assert path.name == "bva"
    assert (path / "bva_cost_element.csv").exists()
    return path


def _metric_rows(rows: list[dict]) -> dict[str, dict]:
    return {row["metric_id"]: row for row in rows}


def test_baseline_reconciles_to_rom() -> None:
    tables = build_all(_real_bva_dir())
    baseline = _metric_rows(tables["bva_baseline_kpi"])

    assert baseline["oneTimeChf"]["value"] == 1_300_000.0
    assert baseline["annualRunChf"]["value"] == 1_250_000.0
    assert baseline["totalCostChf"]["value"] == 2_550_000.0
    assert baseline["hospitals"]["value"] == 3.0


def test_cost_fact_uses_fx_only() -> None:
    rows = build_cost_fact(
        [
            {
                "service_name": "Fabric",
                "resource_group": "rg",
                "resource_id": "fabric",
                "iso_week": "2026-W20",
                "cost_usd": "100.00",
            }
        ],
        [],
        [{"period": "2026-H1", "usd_to_chf": "0.5"}],
    )

    assert rows == [
        {
            "source": "azure",
            "iso_week": "2026-W20",
            "cost_usd": 100.0,
            "usd_to_chf": 0.5,
            "cost_chf": 50.0,
        }
    ]


def test_cost_fact_is_byte_stable() -> None:
    azure_rows = [
        {"iso_week": "2026-W21", "cost_usd": "20"},
        {"iso_week": "2026-W20", "cost_usd": "10"},
    ]
    copilot_rows = [
        {"iso_week": "2026-W20", "aiu": "1", "tokens_in": "2", "tokens_out": "3", "cost_usd": "5"}
    ]
    fx_rows = [{"period": "2026-H1", "usd_to_chf": "0.8"}]

    first = build_cost_fact(azure_rows, copilot_rows, fx_rows)
    second = build_cost_fact(azure_rows, copilot_rows, fx_rows)

    assert json.dumps(first, sort_keys=False) == json.dumps(second, sort_keys=False)
    assert [(row["source"], row["iso_week"]) for row in first] == [
        ("azure", "2026-W20"),
        ("azure", "2026-W21"),
        ("copilot", "2026-W20"),
    ]


def test_baseline_kpi_metric_rows_have_provenance() -> None:
    rows = build_baseline_kpi(
        [{"cost_type": "one_time", "amount_chf": "1"}, {"cost_type": "annual_run", "amount_chf": "2"}],
        [{"beds": "10"}],
    )

    assert rows
    assert all(row["as_of"] for row in rows)
    assert all("docs/BVA.md" in row["source_ref"] for row in rows)


def test_cost_per_bed_and_forecast_run() -> None:
    tables = build_all(_real_bva_dir())
    baseline = _metric_rows(tables["bva_baseline_kpi"])
    beds = sum(row["beds"] for row in tables["bva_hospital_profile_dim"])

    assert baseline["costPerHospitalChf"]["value"] == round(2_550_000.0 / 3, 2)
    assert baseline["costPerBedChf"]["value"] == round(2_550_000.0 / beds, 2)
    assert baseline["costPerForecastRunChf"]["value"] == round(1_250_000.0 / 8760, 2)


def test_consistency_report_band() -> None:
    within = consistency_report(
        {
            "bva_cost_fact": [
                {"source": "azure", "iso_week": "2026-W20", "cost_chf": 11_000.0},
            ],
            "bva_effort_fact": [
                {"role": "Engineer", "iso_week": "2026-W20", "team_cost_chf": 12_000.0},
            ],
        }
    )
    out_of_band = consistency_report(
        {
            "bva_cost_fact": [
                {"source": "azure", "iso_week": "2026-W20", "cost_chf": 1_000.0},
            ],
            "bva_effort_fact": [
                {"role": "Engineer", "iso_week": "2026-W20", "team_cost_chf": 1_000.0},
            ],
        }
    )

    assert _metric_rows(within)["run-azure"]["within_rom_band"] is True
    assert _metric_rows(within)["ot-build"]["within_rom_band"] is True
    assert _metric_rows(out_of_band)["run-azure"]["within_rom_band"] is False
    assert _metric_rows(out_of_band)["ot-build"]["within_rom_band"] is False


def test_effort_fact_chf() -> None:
    rows = build_effort_fact(
        [{"role": "Engineer", "iso_week": "2026-W20", "elective_hours": "10", "role_rate_chf": "150"}]
    )

    assert rows == [
        {
            "role": "Engineer",
            "iso_week": "2026-W20",
            "elective_hours": 10.0,
            "role_rate_chf": 150.0,
            "team_cost_chf": 1500.0,
        }
    ]
