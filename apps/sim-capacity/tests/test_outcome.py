# apps/sim-capacity/tests/test_outcome.py
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.outcome import build_sim_outcome

_PHI_TOKEN = re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b")


def _action(delta):
    return {
        "id": "plan-ep1-action-0", "plan_id": "plan-ep1", "lever_id": "DCA-UNBLOCK-BARRIER",
        "golden_thread": "gt-pt1042", "expected_impact": {"metric": "beds", "delta": delta},
    }


def test_outcome_records_predicted_and_realised():
    realised = {"metric": "beds_freed", "delta": 2, "state_delta": {"beds_freed": ["BED-C3-01", "BED-C3-02"]}}
    out = build_sim_outcome(_action(2), {"x": 1}, {"x": 0}, realised, applied_ts="2027-01-15T09:00:00Z")
    assert out["contract"] == "DC-SIM-OUTCOME-v1"
    assert out["predicted_impact"]["value"] == 2
    assert out["realised_impact"]["value"] == 2
    assert out["divergence"] == 0.0


def test_outcome_divergence_is_normalised_gap():
    realised = {"metric": "beds_freed", "delta": 1, "state_delta": {"beds_freed": ["BED-C3-01"]}}
    out = build_sim_outcome(_action(2), {}, {}, realised, applied_ts="2027-01-15T09:00:00Z")
    assert out["divergence"] == 0.5  # |2-1| / max(2,1)


def test_outcome_is_phi_free():
    realised = {"metric": "beds_freed", "delta": 2, "state_delta": {"beds_freed": ["BED-C3-01", "BED-C3-02"]}}
    out = build_sim_outcome(_action(2), {}, {}, realised, applied_ts="2027-01-15T09:00:00Z")
    assert not _PHI_TOKEN.search(json.dumps(out))
    assert out["provenance"] == "simulated"


def test_outcome_validates_against_schema():
    schema_path = ROOT / "data" / "synthetic" / "schema" / "dc-sim-outcome-v1.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    realised = {"metric": "beds_freed", "delta": 2, "state_delta": {"beds_freed": ["BED-C3-01", "BED-C3-02"]}}
    out = build_sim_outcome(_action(2), {}, {}, realised, applied_ts="2027-01-15T09:00:00Z")
    for key in schema["required"]:
        assert key in out, f"missing required key {key}"
