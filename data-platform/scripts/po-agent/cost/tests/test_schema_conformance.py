"""WS-C Class C cost: GroundedChunk schema conformance."""

import json
from pathlib import Path

import pytest

import reconcile_bva
from reconcile_bva import CostObservation

REPO_ROOT = Path(__file__).resolve().parents[5]
SCHEMA_PATH = (
    REPO_ROOT / "data" / "synthetic" / "schema" / "grounded-chunk-v1.schema.json"
)

jsonschema = pytest.importorskip("jsonschema")


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft7Validator(schema)


def _obs(amount=102_000.0, ok=True):
    return CostObservation(
        amount=amount,
        currency="CHF",
        window_start="2026-07-01",
        window_end="2026-07-31",
        feed="Azure Cost Management + GitHub Copilot usage",
        as_of="2026-07-31",
        ok=ok,
    )


def _variants():
    return {
        "within": reconcile_bva.reconcile_bva(_obs(102_000.0), REPO_ROOT),
        "outside": reconcile_bva.reconcile_bva(_obs(500_000.0), REPO_ROOT),
        "refusal": reconcile_bva.reconcile_bva(
            _obs(102_000.0), REPO_ROOT, requested_horizon_end="2027-06-30"
        ),
        "snapshot": reconcile_bva.reconcile_bva(_obs(0.0, ok=False), REPO_ROOT),
    }


@pytest.mark.parametrize("variant", ["within", "outside", "refusal", "snapshot"])
def test_cost_chunk_conforms_to_schema(validator, variant):
    chunk = _variants()[variant]
    errors = sorted(validator.iter_errors(chunk), key=str)
    assert not errors, f"{variant}: {[e.message for e in errors]}"
