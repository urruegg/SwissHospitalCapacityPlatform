"""WS-B Class B live-proof: GroundedChunk schema conformance.

Every chunk emitted by ``reconcile`` / ``liveProof`` (verified, drift and
snapshot variants) must validate against the frozen WS-G0 schema
``data/synthetic/schema/grounded-chunk-v1.schema.json``.
"""

import json
from pathlib import Path

import pytest

import probes
import reconcile
from reconcile import Observation

REPO_ROOT = Path(__file__).resolve().parents[5]
SCHEMA_PATH = (
    REPO_ROOT / "data" / "synthetic" / "schema" / "grounded-chunk-v1.schema.json"
)

jsonschema = pytest.importorskip("jsonschema")


@pytest.fixture(scope="module")
def validator():
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    return jsonschema.Draft7Validator(schema)


def _all_variants():
    # verified (matching baseline)
    sku = reconcile.baseline_for("q-fabric-capacity-sku", REPO_ROOT).value
    verified = reconcile.reconcile(
        Observation("q-fabric-capacity-sku", sku, "Azure Resource Graph", "2026-07-25"),
        REPO_ROOT,
    )
    # drift (mismatch)
    drift = reconcile.reconcile(
        Observation("q-fabric-capacity-sku", "F64", "Azure Resource Graph", "2026-07-25"),
        REPO_ROOT,
    )
    # snapshot (probe failed)
    snapshot = reconcile.reconcile(
        Observation("q-fabric-capacity-sku", None, "Azure Resource Graph", "2026-07-25", ok=False),
        REPO_ROOT,
    )
    return {"verified": verified, "drift": drift, "snapshot": snapshot}


@pytest.mark.parametrize("variant", ["verified", "drift", "snapshot"])
def test_grounded_chunk_conforms_to_schema(validator, variant):
    chunk = _all_variants()[variant]
    errors = sorted(validator.iter_errors(chunk), key=str)
    assert not errors, f"{variant}: {[e.message for e in errors]}"
