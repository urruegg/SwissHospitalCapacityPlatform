# apps/sim-capacity/tests/test_sim_state.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import SimState, Stage, build_sim_state


def test_build_is_deterministic():
    a = build_sim_state(hospital_id="USZ", seed=42, wards=[("C3", "internal-medicine", 20)])
    b = build_sim_state(hospital_id="USZ", seed=42, wards=[("C3", "internal-medicine", 20)])
    assert a.snapshot() == b.snapshot()


def test_wards_and_beds_created():
    s = build_sim_state(hospital_id="USZ", seed=1, wards=[("C3", "internal-medicine", 20)])
    assert s.ward("C3").staffed_capacity == 20
    assert len(s.beds_in_ward("C3")) == 20


def test_occupancy_counts_occupied_beds():
    s = build_sim_state(hospital_id="USZ", seed=1, wards=[("C3", "internal-medicine", 20)])
    occupied = [b for b in s.beds_in_ward("C3") if b.state == "occupied"]
    assert s.occupancy("C3") == len(occupied)


def test_discharge_ready_patients_query():
    s = build_sim_state(hospital_id="USZ", seed=7, wards=[("C3", "internal-medicine", 20)])
    ready = s.patients_in_stage(Stage.DISCHARGE_READY)
    assert all(p.journey_stage == Stage.DISCHARGE_READY for p in ready)
