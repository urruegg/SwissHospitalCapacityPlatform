"""WS-B Class B live-proof: reconcile-and-flag tests.

TDD step 1 (RED): a mocked Resource Graph observation whose Fabric
capacity SKU differs from ``docs/bom.yaml`` must reconcile to a
``drift``-flagged GroundedChunk that surfaces BOTH the live and the
recorded value.
"""

from pathlib import Path

import reconcile
from reconcile import Observation

REPO_ROOT = Path(__file__).resolve().parents[5]


def test_sku_mismatch_is_flagged_as_drift():
    # docs/bom.yaml records the Fabric capacity SKU as F2 (see ADR-0037).
    # A live Resource Graph probe reports F64 -> must be flagged drift.
    obs = Observation(
        question_id="q-fabric-capacity-sku",
        observed="F64",
        feed="Azure Resource Graph",
        as_of="2026-07-25",
        ok=True,
    )

    chunk = reconcile.reconcile(obs, repo_root=REPO_ROOT)

    assert chunk["classId"] == "B"
    # Both values present and explicitly flagged as drift.
    assert "F64" in chunk["text"]
    assert "F2" in chunk["text"]
    assert "drift" in chunk["text"].lower()
    # Drift is unverified until a human confirms which value is correct.
    assert chunk["status"] == "requires-validation"
    assert chunk["liveness"] == "live"
