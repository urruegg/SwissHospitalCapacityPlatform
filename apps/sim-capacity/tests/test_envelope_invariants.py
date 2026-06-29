import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from contracts.demand_encounter import build_thin_demand_envelope
from producer import emit_once


def test_build_thin_envelope_has_required_top_level_fields():
    envelope = build_thin_demand_envelope()
    assert envelope["contractId"] == "DC-DEMAND-ENCOUNTER-v1"
    assert envelope["residency"] == "CH"
    assert envelope["purposeTags"] == ["capacity-planning"]
    assert len(envelope["records"]) == 1


def test_build_thin_envelope_record_has_contract_invariants():
    envelope = build_thin_demand_envelope()
    record = envelope["records"][0]
    assert record["contractId"] == "DC-DEMAND-ENCOUNTER-v1"
    assert record["class"] == "IMP"
    assert record["purposeTag"] in envelope["purposeTags"]
    assert record["dataResidencyRegion"] in {"switzerlandnorth", "switzerlandwest"}
    assert record["pseudonymId"].startswith("PID-")


def test_emit_once_returns_json_string_for_eventstream_payload_shape():
    payload = emit_once()
    obj = json.loads(payload)
    assert obj["contractId"] == "DC-DEMAND-ENCOUNTER-v1"
    assert isinstance(obj["records"], list)
    assert len(obj["records"]) == 1
