import csv
import importlib.util
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "validate_master_data.py"
spec = importlib.util.spec_from_file_location("validate_master_data", MODULE_PATH)
vmd = importlib.util.module_from_spec(spec)
sys.modules["validate_master_data"] = vmd
spec.loader.exec_module(vmd)


def _write(dirpath, name, header, rows):
    with (dirpath / name).open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)


def _good_bva_evidence(tmp):
    bva = tmp / "bva"
    bva.mkdir(parents=True, exist_ok=True)

    _write(bva, "dim_assumption.csv", ["assumption_id", "assumption", "value", "unit", "basis", "confidence"], [
        ["AS-001", "USD to CHF conversion rate", "0.88", "CHF/USD", "Stated modelling assumption", "medium"],
    ])
    _write(
        bva,
        "dim_cost_element.csv",
        ["cost_element_id", "cost_element", "category", "cost_type", "model_version", "amount_chf", "confidence", "evidence_status", "source_ref"],
        [
            ["CE-001", "Platform build", "one_time", "build", "v1.0.1", "640000", "ROM_30", "modelled", "BVA v1.0.1"],
            ["CE-001", "Platform build", "one_time", "build", "v2.0.0", "60000", "ROM_30", "modelled_on_measured", "BVA v2.0.0"],
        ],
    )
    _write(bva, "dim_evidence_source.csv", ["source_id", "source", "source_type", "authority", "period", "used_for", "caveat"], [
        ["EV-001", "Azure Cost Management ActualCost", "billing", "authoritative", "2026-06-29..2026-07-27", "Azure build cost", ""],
    ])
    _write(bva, "fact_azure_cost_weekly.csv", ["azure_cost_id", "week_start", "service", "amount_usd", "amount_chf", "currency", "settlement_status", "source"], [
        ["AZ-1", "2026-06-29", "Microsoft Fabric", "5.83", "5.13", "USD", "settled", "ActualCost"],
    ])
    _write(
        bva,
        "fact_build_cost_actual.csv",
        ["build_cost_id", "cost_element", "category", "amount_chf", "amount_usd", "share_pct", "evidence_status", "source_system", "period_start", "period_end", "caveat"],
        [
            ["BC-001", "Human effort", "human", "18831", "", "88.5", "measured", "Tracked engagement", "2026-05-01", "2026-07-31", ""],
            ["BC-002", "Copilot agent tokens", "agent_tokens", "1240", "1409.46", "5.8", "estimated", "Copilot CLI session store", "2026-07-17", "2026-07-27", ""],
            ["BC-003", "Azure cloud services", "cloud", "1111", "1262.85", "5.2", "measured_extrapolated", "Azure Cost Management", "2026-06-29", "2026-07-27", ""],
            ["BC-004", "Copilot subscription", "subscription", "103", "117.0", "0.5", "estimated", "List price", "2026-05-01", "2026-07-31", ""],
            ["BC-999", "TOTAL", "total", "21286", "", "100.0", "mixed", "Composite", "2026-05-01", "2026-07-31", ""],
        ],
    )
    _write(bva, "fact_copilot_usage_weekly.csv", ["copilot_usage_id", "week_start", "sessions", "input_tokens", "output_tokens", "cache_read_tokens", "reasoning_tokens", "aiu_consumed", "store", "evidence_status"], [
        ["CP-1", "2026-07-17", "3", "468390537", "2616277", "442175660", "906779", "44191.973", "local", "telemetry"],
        ["CP-2", "2026-05-04", "1", "476875", "3320", "", "", "", "cloud", "telemetry"],
    ])
    _write(bva, "fact_effort.csv", ["effort_id", "effort_type", "person", "quantity", "unit", "hours", "hourly_rate_chf", "cost_chf", "period", "evidence_status"], [
        ["EF-999", "TOTAL", "Urs Rueegg", "1", "person", "174.0", "108.23", "18831", "90-day build window", "measured"],
    ])
    _write(
        bva,
        "fact_roi_scenario.csv",
        ["scenario_id", "model_version", "scenario", "annual_benefit_chf", "annual_run_cost_chf", "one_time_cost_chf", "tco_3yr_chf", "gross_benefit_3yr_chf", "net_value_3yr_chf", "roi_3yr_pct", "payback_months"],
        [
            ["SC-V2-BASE", "v2.0.0", "Base (Frontier-informed)", "3820000", "1250000", "780000", "4530000", "11460000", "6930000", "153", "3.6"],
            ["SC-V1-CONS", "v1.0.1", "Conservative", "2600000", "1320000", "1300000", "5260000", "7800000", "2540000", "48", ""],
        ],
    )
    _write(bva, "fact_unit_economics.csv", ["unit_id", "metric", "value_chf", "denominator", "denominator_count", "evidence_status"], [
        ["UE-005", "Blended human hourly rate", "108.23", "productive hours/yr", "1848", "derived"],
    ])
    _write(bva, "fact_value_lever.csv", ["value_lever_id", "value_lever", "annual_benefit_chf", "value_logic", "evidence_status", "validation_required"], [
        ["VL-001", "Reduced avoidable bed-day blocking", "1650000", "Faster discharge decisions", "ROM", "Provider finance validation"],
    ])
    return bva


def test_good_bva_evidence_passes(tmp_path):
    bva = _good_bva_evidence(tmp_path)
    assert vmd.validate_bva_evidence(bva) == []


def test_missing_file_is_reported(tmp_path):
    bva = _good_bva_evidence(tmp_path)
    (bva / "fact_value_lever.csv").unlink()
    errors = vmd.validate_bva_evidence(bva)
    assert any("missing file: fact_value_lever.csv" in e for e in errors)


def test_invalid_evidence_status_is_rejected(tmp_path):
    bva = _good_bva_evidence(tmp_path)
    _write(bva, "fact_value_lever.csv", ["value_lever_id", "value_lever", "annual_benefit_chf", "value_logic", "evidence_status", "validation_required"], [
        ["VL-001", "Reduced avoidable bed-day blocking", "1650000", "Faster discharge decisions", "guessed", "Provider finance validation"],
    ])
    errors = vmd.validate_bva_evidence(bva)
    assert any("evidence_status='guessed'" in e for e in errors)


def test_non_numeric_amount_is_rejected(tmp_path):
    bva = _good_bva_evidence(tmp_path)
    _write(bva, "fact_effort.csv", ["effort_id", "effort_type", "person", "quantity", "unit", "hours", "hourly_rate_chf", "cost_chf", "period", "evidence_status"], [
        ["EF-999", "TOTAL", "Urs Rueegg", "1", "person", "not-a-number", "108.23", "18831", "90-day build window", "measured"],
    ])
    errors = vmd.validate_bva_evidence(bva)
    assert any("hours='not-a-number' must be numeric" in e for e in errors)


def test_build_cost_reconciliation_tolerates_chf_1_rounding(tmp_path):
    # BC-999=21286 vs components summing to 21285 is the real, committed
    # figure and must pass (CHF 1 rounding tolerance).
    bva = _good_bva_evidence(tmp_path)
    assert vmd.validate_bva_evidence(bva) == []


def test_build_cost_reconciliation_rejects_large_drift(tmp_path):
    bva = _good_bva_evidence(tmp_path)
    _write(
        bva,
        "fact_build_cost_actual.csv",
        ["build_cost_id", "cost_element", "category", "amount_chf", "amount_usd", "share_pct", "evidence_status", "source_system", "period_start", "period_end", "caveat"],
        [
            ["BC-001", "Human effort", "human", "18831", "", "88.5", "measured", "Tracked engagement", "2026-05-01", "2026-07-31", ""],
            ["BC-999", "TOTAL", "total", "21286", "", "100.0", "mixed", "Composite", "2026-05-01", "2026-07-31", ""],
        ],
    )
    errors = vmd.validate_bva_evidence(bva)
    assert any("exceeds CHF 1 rounding tolerance" in e for e in errors)


def test_dim_cost_element_duplicate_composite_key_is_rejected(tmp_path):
    bva = _good_bva_evidence(tmp_path)
    _write(
        bva,
        "dim_cost_element.csv",
        ["cost_element_id", "cost_element", "category", "cost_type", "model_version", "amount_chf", "confidence", "evidence_status", "source_ref"],
        [
            ["CE-001", "Platform build", "one_time", "build", "v1.0.1", "640000", "ROM_30", "modelled", "BVA v1.0.1"],
            ["CE-001", "Platform build (dup)", "one_time", "build", "v1.0.1", "640000", "ROM_30", "modelled", "BVA v1.0.1"],
        ],
    )
    errors = vmd.validate_bva_evidence(bva)
    assert any("duplicate primary key (cost_element_id, model_version)" in e for e in errors)
