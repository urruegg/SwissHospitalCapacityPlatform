import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from kickstart import emit_kickstart_once


def test_emit_kickstart_once_returns_json_payload():
    payload = emit_kickstart_once()
    obj = json.loads(payload)
    assert obj["contractId"] == "DC-DEMAND-ENCOUNTER-v1"
    assert len(obj["records"]) == 1


def test_emit_kickstart_once_includes_requested_profile_name():
    payload = emit_kickstart_once(profile_name="winter-flu-peak")
    obj = json.loads(payload)
    assert obj["simulationProfile"] == "winter-flu-peak"
