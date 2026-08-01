# apps/sim-capacity/tests/test_gold_seed.py
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.gold_seed import seed_sim_state_from_gold
from closedloop.sim_state import Stage

_GOLD = json.loads((Path(__file__).parent / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))


def test_seed_builds_wards_and_beds():
    s = seed_sim_state_from_gold(_GOLD)
    assert s.hospital_id == "USZ"
    assert s.ward("C3").staffed_capacity == 8
    assert len(s.beds_in_ward("C3")) == 8
    assert s.occupancy("C3") == 6


def test_seed_promotes_high_score_inpatients_to_discharge_ready():
    s = seed_sim_state_from_gold(_GOLD)
    ready = {p.patient_id for p in s.patients_in_stage(Stage.DISCHARGE_READY)}
    # PT-0001 (0.92), PT-0002 (0.88), PT-0003 (0.85) are all >= 0.8.
    assert ready == {"PT-0001", "PT-0002", "PT-0003"}


def test_seed_maps_open_barriers():
    s = seed_sim_state_from_gold(_GOLD)
    assert len(s.open_barriers("transport")) == 3


def test_seed_is_deterministic():
    a = seed_sim_state_from_gold(_GOLD)
    b = seed_sim_state_from_gold(_GOLD)
    assert a.snapshot() == b.snapshot()
