"""Dependency-free Opportunity validation tests for the shared BVA dataset."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_PLATFORM = REPO_ROOT / "data-platform"
if str(DATA_PLATFORM) not in sys.path:
    sys.path.insert(0, str(DATA_PLATFORM))

SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "bva-opportunity-v1.schema.json"
DATASET_PATH = REPO_ROOT / "data" / "synthetic" / "bva" / "bva-opportunities.json"
EXAMPLE_PATH = REPO_ROOT / "evals" / "bva-agent" / "fixtures" / "bva-opportunity-example.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_example_fixture_validates_against_frozen_schema() -> None:
    from bva.opportunity import validate_opportunity

    assert validate_opportunity(_load(EXAMPLE_PATH)) == []


def test_every_shared_dataset_record_validates_against_frozen_schema() -> None:
    from bva.opportunity import load_dataset, validate_opportunity

    opportunities = load_dataset(DATASET_PATH)

    assert opportunities
    for opportunity in opportunities:
        assert validate_opportunity(opportunity) == []


def test_broken_opportunity_fails_validation() -> None:
    from bva.opportunity import validate_opportunity

    broken = _load(EXAMPLE_PATH)
    broken["status"] = "auto-approved"
    broken["unexpected"] = True

    errors = validate_opportunity(broken)

    assert any("status" in error and "enum" in error for error in errors)
    assert any("unexpected" in error and "additional" in error for error in errors)


def test_make_opportunity_id_is_deterministic_ascii_slug() -> None:
    from bva.opportunity import make_opportunity_id, slugify

    assert slugify("Hopital de Fribourg") == "hopital-de-fribourg"
    assert make_opportunity_id("Hopital de Fribourg") == "opp-hopital-de-fribourg-0001"
    assert make_opportunity_id("Hopital de Fribourg") == make_opportunity_id("Hopital de Fribourg")
    assert make_opportunity_id("Reha Zentrum Zürich Süd") == "opp-reha-zentrum-zurich-sud-0001"


def test_shared_dataset_covers_pipeline_statuses() -> None:
    from bva.opportunity import load_dataset

    statuses = {opportunity["status"] for opportunity in load_dataset(DATASET_PATH)}

    assert len(statuses) >= 6
    assert {"new", "evaluating", "qualified", "disqualified", "onboarding", "won"} <= statuses


def test_present_bva_snapshots_carry_engine_metrics() -> None:
    """A non-null bvaResult snapshot must mirror the engine metrics shape so the
    Cosmos->gold projection can derive weighted ROI (roiPct is numeric)."""
    from bva.opportunity import load_dataset

    snapshots = [o["bvaResult"] for o in load_dataset(DATASET_PATH) if o.get("bvaResult")]

    assert snapshots
    for snapshot in snapshots:
        metrics = snapshot.get("metrics")
        assert isinstance(metrics, dict), "bvaResult snapshot must carry a metrics object"
        assert isinstance(metrics.get("roiPct"), (int, float))

