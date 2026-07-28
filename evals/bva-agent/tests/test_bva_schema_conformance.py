"""Contract conformance tests for Sprint 33 BVA Agent frozen contracts.

Frozen contract owned by WS-G0. Validates the deterministic bva.simulate
result and Opportunity example fixtures against their JSON Schemas. Run:

    python -m pytest evals/bva-agent/tests/test_bva_schema_conformance.py -v
"""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCHEMA_DIR = REPO_ROOT / "data" / "synthetic" / "schema"
FIXTURE_DIR = REPO_ROOT / "evals" / "bva-agent" / "fixtures"
SIM_SCHEMA_PATH = SCHEMA_DIR / "bva-simulation-result-v1.schema.json"
OPP_SCHEMA_PATH = SCHEMA_DIR / "bva-opportunity-v1.schema.json"
SIM_FIXTURE_PATH = FIXTURE_DIR / "bva-simulation-result-example.json"
SIM_WHATIF_FIXTURE_PATH = FIXTURE_DIR / "bva-simulation-result-whatif.json"
SIM_FIXTURE_PATHS = (SIM_FIXTURE_PATH, SIM_WHATIF_FIXTURE_PATH)
OPP_FIXTURE_PATH = FIXTURE_DIR / "bva-opportunity-example.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_schemas_exist() -> None:
    assert SIM_SCHEMA_PATH.is_file(), f"missing frozen schema: {SIM_SCHEMA_PATH}"
    assert OPP_SCHEMA_PATH.is_file(), f"missing frozen schema: {OPP_SCHEMA_PATH}"


def test_simulation_result_validates() -> None:
    import jsonschema

    schema = _load(SIM_SCHEMA_PATH)
    for fixture_path in SIM_FIXTURE_PATHS:
        jsonschema.validate(instance=_load(fixture_path), schema=schema)


def test_all_money_is_chf() -> None:
    for fixture_path in SIM_FIXTURE_PATHS:
        fixture = _load(fixture_path)
        assert fixture["currency"] == "CHF"


def test_every_metric_has_a_chunk() -> None:
    for fixture_path in SIM_FIXTURE_PATHS:
        fixture = _load(fixture_path)
        chunks = fixture["chunks"]
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk["classId"] == "C"
            assert chunk["citation"]["sourceRef"]


def test_opportunity_validates() -> None:
    import jsonschema

    jsonschema.validate(instance=_load(OPP_FIXTURE_PATH), schema=_load(OPP_SCHEMA_PATH))
