# EPIC Closed-Loop Simulation Engine — Operational Loop Implementation Plan (Sprint 38, Plan 1)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn `apps/sim-capacity` from a one-way demand producer into a **stateful EPIC system-of-record twin** that consumes HITL-approved agent actions and applies them back to its patient-flow state — proven by a deterministic end-to-end patient-journey test where an approved discharge frees a real bed and changes the next tick.

**Architecture:** Add a new `apps/sim-capacity/src/closedloop/` subpackage — `SimState` (patient-flow entity graph), a `SystemAdapter` seam with an `EpicAdapter`, a stateful `tick` that advances state, a declarative lever-`effect` interpreter, an `ActuationConsumer` that applies **already-approved** decision-tier actions to `SimState` (idempotently), and an `OutcomeRecorder` that emits the new `DC-SIM-OUTCOME-v1` contract (predicted-vs-realised divergence). The decision-tier lifecycle (`open_plan → propose_action → approve_action`) in `data-platform/decision/coordination/` is **reused unchanged**; the consumer only reads its `PlanStore` and applies effects. All new logic is pure, seeded, and TDD-able with no live Azure.

**Tech Stack:** Python 3.11, dataclasses, `random.Random(seed)` determinism, pytest (each test file inserts `apps/sim-capacity/src` into `sys.path` via `Path(__file__).resolve().parents[3]`). Reuses `envelope.build_envelope`, `clock.sim_clock.SimClock`, and the decision-tier `coordination.store.InMemoryStore` + `coordination.plan_runtime` + `impact.compute_expected_impact`.

**Scope note:** Sprint 38 is one large loop (M0–M5 in the [design spec](../specs/2026-07-31-sprint-38-epic-closed-loop-simulation-engine-design.md)). **This plan delivers the operational loop only — M0–M4** — which produces working, testable software on its own: a closed loop you can drive end-to-end in a deterministic test. **Follow-on plan** (its own file when we reach it): **M5 — the thin finetuning slice** (an `outcome_divergence` evaluator wired into the Sprint 30 evaluator library + advisory backlog + a calibration gate). M5 is cleanly separable because it only *consumes* the `DC-SIM-OUTCOME-v1` records this plan produces.

**Working directory for all commands:** `apps/sim-capacity` (run `cd apps/sim-capacity` first). Full test suite command: `python -m pytest`. The E2E test in Task 12 also adds `data-platform/decision` to `sys.path`; no install step is required.

---

## File structure

| File | Responsibility |
|------|----------------|
| `apps/sim-capacity/src/closedloop/__init__.py` *(create)* | Package marker for the closed-loop subpackage. |
| `apps/sim-capacity/src/closedloop/sim_state.py` *(create)* | `SimState` entity graph (Patient/Encounter/Bed/Ward/ORSlot/StaffShift/DischargeBarrier) + a deterministic seeded builder + query/mutation helpers. One responsibility: hold and mutate patient-flow state. |
| `apps/sim-capacity/src/closedloop/state_store.py` *(create)* | `SimStateStore` protocol + `InMemorySimStateStore` + JSON snapshot save/load (CI persistence; Cosmos-ready seam). |
| `apps/sim-capacity/src/closedloop/system_adapter.py` *(create)* | `SystemAdapter` protocol + `EpicAdapter`: derive demand/capacity envelopes from `SimState` using `build_envelope`. |
| `apps/sim-capacity/src/closedloop/tick.py` *(create)* | `advance_state(sim, rng)`: deterministic time transitions (arrivals, LOS countdown, barrier ageing). |
| `apps/sim-capacity/src/closedloop/effect.py` *(create)* | Declarative lever-`effect` interpreter: `apply_effect(sim, effect_decl, params) -> RealisedDelta`. |
| `apps/sim-capacity/src/closedloop/actuation.py` *(create)* | `ActuationConsumer`: apply already-approved decision-tier actions to `SimState`, idempotent per `action_id`, refuse non-approved. |
| `apps/sim-capacity/src/closedloop/outcome.py` *(create)* | `OutcomeRecorder` + `build_sim_outcome(...)` -> `DC-SIM-OUTCOME-v1` (predicted vs realised, divergence, PHI-free). |
| `apps/sim-capacity/src/closedloop/journey.py` *(create)* | Shared E2E patient-journey definition (stages + expected lever per agent). |
| `data/synthetic/schema/dc-sim-outcome-v1.schema.json` *(create)* | The `DC-SIM-OUTCOME-v1` JSON Schema contract. |
| `data-platform/decision/levers/lever.schema.json` *(modify)* | Add the optional `effect` property to the lever schema. |
| `data-platform/decision/levers/dca.yaml` *(modify)* | Add the `effect:` block to `DCA-UNBLOCK-BARRIER` — the lever the MVP journey drives (OOA/BMCA/ORSA/SBA effect blocks are the multi-agent follow-on). |
| `apps/sim-capacity/tests/test_sim_state.py` *(create)* | `SimState` builder + mutation unit tests. |
| `apps/sim-capacity/tests/test_state_store.py` *(create)* | Store + snapshot round-trip tests. |
| `apps/sim-capacity/tests/test_system_adapter.py` *(create)* | Adapter derives envelopes; PHI-free. |
| `apps/sim-capacity/tests/test_tick.py` *(create)* | Tick transitions + determinism. |
| `apps/sim-capacity/tests/test_effect.py` *(create)* | Effect interpreter mutations. |
| `apps/sim-capacity/tests/test_actuation.py` *(create)* | Consumer applies approved actions; idempotency + refusal. |
| `apps/sim-capacity/tests/test_outcome.py` *(create)* | Outcome contract + divergence + no-PHI. |
| `apps/sim-capacity/tests/test_e2e_closed_loop.py` *(create)* | End-to-end journey: happy path + 3 failure modes. |
| `docs/DATA.md` *(modify)* | Register `DC-SIM-OUTCOME-v1` + the lever `effect` convention. |
| `docs/PRD.md` *(modify)* | Add `FR-SIM-*` / `FR-CLP-*` / `NFR-SIM-*` and §7 traceability row. |
| `docs/adr/0057-sim-outcome-and-effect-schema.md` *(create)* | Ratify `DC-SIM-OUTCOME-v1`, the lever `effect` schema, and the sim-as-ground-truth pattern. |

---

## M0 — SimState + SystemAdapter seam

### Task 1: `SimState` entity graph + deterministic builder

**Files:**

- Create: `apps/sim-capacity/src/closedloop/__init__.py`
- Create: `apps/sim-capacity/src/closedloop/sim_state.py`
- Test: `apps/sim-capacity/tests/test_sim_state.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_sim_state.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop'`

- [ ] **Step 3: Write minimal implementation**

```python
# apps/sim-capacity/src/closedloop/__init__.py
"""Sprint 38 closed-loop operational engine: stateful EPIC twin + actuation."""
```

```python
# apps/sim-capacity/src/closedloop/sim_state.py
"""Stateful patient-flow twin (Sprint 38 M0, design spec Sec 5).

Synthetic, PHI-free by construction: only synthetic IDs (PT-*, BED-*) and
non-identifying attributes (acuity, specialty, stage). Deterministic: the
builder draws from a seeded ``random.Random`` so the same (hospital, seed,
wards) always yields the same state.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class Stage(str, Enum):
    ARRIVAL = "ARRIVAL"
    TRIAGE = "TRIAGE"
    ADMIT = "ADMIT"
    INPATIENT = "INPATIENT"
    DISCHARGE_READY = "DISCHARGE_READY"
    DISCHARGED = "DISCHARGED"


@dataclass
class Patient:
    patient_id: str
    acuity: int
    specialty: str
    journey_stage: Stage


@dataclass
class Bed:
    bed_id: str
    ward_id: str
    state: str  # available | occupied | blocked | planned
    patient_id: str | None = None


@dataclass
class Ward:
    ward_id: str
    specialty: str
    staffed_capacity: int


@dataclass
class DischargeBarrier:
    barrier_id: str
    patient_id: str
    barrier_type: str
    status: str  # open | cleared
    aged_h: int


@dataclass
class SimState:
    hospital_id: str
    patients: Dict[str, Patient] = field(default_factory=dict)
    beds: Dict[str, Bed] = field(default_factory=dict)
    wards: Dict[str, Ward] = field(default_factory=dict)
    barriers: Dict[str, DischargeBarrier] = field(default_factory=dict)

    def ward(self, ward_id: str) -> Ward:
        return self.wards[ward_id]

    def beds_in_ward(self, ward_id: str) -> List[Bed]:
        return [b for b in self.beds.values() if b.ward_id == ward_id]

    def occupancy(self, ward_id: str) -> int:
        return sum(1 for b in self.beds_in_ward(ward_id) if b.state == "occupied")

    def patients_in_stage(self, stage: Stage) -> List[Patient]:
        return [p for p in self.patients.values() if p.journey_stage == stage]

    def open_barriers(self, barrier_type: str) -> List[DischargeBarrier]:
        return [
            b for b in self.barriers.values()
            if b.barrier_type == barrier_type and b.status == "open"
        ]

    def snapshot(self) -> Dict[str, Any]:
        """Deterministic, order-stable dict of the whole state (for equality/JSON)."""
        return {
            "hospital_id": self.hospital_id,
            "patients": [vars(self.patients[k]) | {"journey_stage": self.patients[k].journey_stage.value}
                         for k in sorted(self.patients)],
            "beds": [vars(self.beds[k]) for k in sorted(self.beds)],
            "wards": [vars(self.wards[k]) for k in sorted(self.wards)],
            "barriers": [vars(self.barriers[k]) for k in sorted(self.barriers)],
        }


def build_sim_state(hospital_id: str, seed: int, wards: List[tuple[str, str, int]]) -> SimState:
    """Deterministically construct an initial twin. ``wards`` is a list of
    ``(ward_id, specialty, staffed_capacity)``. Roughly 80% of beds start
    occupied; ~15% of inpatients start discharge-ready, half of those with an
    open ``transport`` barrier — enough structure for the journey levers."""
    rng = random.Random(seed)
    state = SimState(hospital_id=hospital_id)
    pt_seq = 0
    for ward_id, specialty, cap in wards:
        state.wards[ward_id] = Ward(ward_id=ward_id, specialty=specialty, staffed_capacity=cap)
        for i in range(cap):
            bed_id = f"BED-{ward_id}-{i:02d}"
            occupied = rng.random() < 0.80
            patient_id = None
            if occupied:
                pt_seq += 1
                patient_id = f"PT-{pt_seq:04d}"
                ready = rng.random() < 0.15
                stage = Stage.DISCHARGE_READY if ready else Stage.INPATIENT
                state.patients[patient_id] = Patient(
                    patient_id=patient_id,
                    acuity=rng.randint(1, 4),
                    specialty=specialty,
                    journey_stage=stage,
                )
                if ready and rng.random() < 0.5:
                    bid = f"BAR-{patient_id}"
                    state.barriers[bid] = DischargeBarrier(
                        barrier_id=bid, patient_id=patient_id,
                        barrier_type="transport", status="open",
                        aged_h=rng.randint(6, 48),
                    )
            state.beds[bed_id] = Bed(
                bed_id=bed_id, ward_id=ward_id,
                state="occupied" if occupied else "available",
                patient_id=patient_id,
            )
    return state
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_sim_state.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/sim-capacity/src/closedloop/__init__.py apps/sim-capacity/src/closedloop/sim_state.py apps/sim-capacity/tests/test_sim_state.py
git commit -m "feat(sim): add stateful SimState patient-flow twin (Sprint 38 M0)"
```

### Task 2: `SimStateStore` + JSON snapshot persistence

**Files:**

- Create: `apps/sim-capacity/src/closedloop/state_store.py`
- Test: `apps/sim-capacity/tests/test_state_store.py`

- [ ] **Step 1: Write the failing test**

```python
# apps/sim-capacity/tests/test_state_store.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.state_store import InMemorySimStateStore, save_snapshot, load_snapshot


def test_store_put_get_roundtrip():
    store = InMemorySimStateStore()
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    store.put(s)
    assert store.get("USZ").snapshot() == s.snapshot()


def test_json_snapshot_roundtrip(tmp_path):
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    p = tmp_path / "state.json"
    save_snapshot(s, p)
    reloaded = load_snapshot(p)
    assert reloaded.snapshot() == s.snapshot()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_state_store.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.state_store'`

- [ ] **Step 3: Write minimal implementation**

```python
# apps/sim-capacity/src/closedloop/state_store.py
"""SimState persistence (Sprint 38 M0). In-memory for CI; JSON snapshot for
reproducible fixtures. The protocol keeps a Cosmos-backed store additive later
(design spec Sec 4, open question Q1)."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict

from closedloop.sim_state import (
    Bed, DischargeBarrier, Patient, SimState, Stage, Ward,
)


class SimStateStore(ABC):
    @abstractmethod
    def put(self, state: SimState) -> None: ...

    @abstractmethod
    def get(self, hospital_id: str) -> SimState: ...


class InMemorySimStateStore(SimStateStore):
    def __init__(self) -> None:
        self._by_hospital: Dict[str, SimState] = {}

    def put(self, state: SimState) -> None:
        self._by_hospital[state.hospital_id] = state

    def get(self, hospital_id: str) -> SimState:
        return self._by_hospital[hospital_id]


def _state_from_snapshot(snap: dict) -> SimState:
    state = SimState(hospital_id=snap["hospital_id"])
    for w in snap["wards"]:
        state.wards[w["ward_id"]] = Ward(**w)
    for b in snap["beds"]:
        state.beds[b["bed_id"]] = Bed(**b)
    for p in snap["patients"]:
        state.patients[p["patient_id"]] = Patient(
            patient_id=p["patient_id"], acuity=p["acuity"],
            specialty=p["specialty"], journey_stage=Stage(p["journey_stage"]),
        )
    for br in snap["barriers"]:
        state.barriers[br["barrier_id"]] = DischargeBarrier(**br)
    return state


def save_snapshot(state: SimState, path: Path) -> None:
    Path(path).write_text(json.dumps(state.snapshot(), indent=2, sort_keys=True), encoding="utf-8")


def load_snapshot(path: Path) -> SimState:
    return _state_from_snapshot(json.loads(Path(path).read_text(encoding="utf-8")))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_state_store.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/sim-capacity/src/closedloop/state_store.py apps/sim-capacity/tests/test_state_store.py
git commit -m "feat(sim): add SimState store + JSON snapshot persistence (Sprint 38 M0)"
```

### Task 3: `SystemAdapter` seam + `EpicAdapter`

**Files:**

- Create: `apps/sim-capacity/src/closedloop/system_adapter.py`
- Test: `apps/sim-capacity/tests/test_system_adapter.py`

- [ ] **Step 1: Write the failing test**

```python
# apps/sim-capacity/tests/test_system_adapter.py
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.system_adapter import EpicAdapter

_PHI_TOKEN = re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b")  # SSN-like guard


def test_adapter_emits_bed_state_envelopes():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    adapter = EpicAdapter(s)
    envs = adapter.read_demand(simulated_at=datetime(2027, 1, 15, 8), sim_run_id="run-x", seed=42)
    bed_states = [e for e in envs if e["eventKind"] == "bed_state"]
    assert len(bed_states) == 10
    assert all(e["hospitalId"] == "USZ" for e in bed_states)


def test_adapter_derives_ward_occupancy_summary():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    adapter = EpicAdapter(s)
    envs = adapter.read_demand(simulated_at=datetime(2027, 1, 15, 8), sim_run_id="run-x", seed=42)
    summary = next(e for e in envs if e["eventKind"] == "ward_occupancy")
    assert summary["payload"]["wardId"] == "C3"
    assert summary["payload"]["occupiedBeds"] == s.occupancy("C3")


def test_adapter_output_is_phi_free():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 10)])
    adapter = EpicAdapter(s)
    envs = adapter.read_demand(simulated_at=datetime(2027, 1, 15, 8), sim_run_id="run-x", seed=42)
    blob = str(envs)
    assert not _PHI_TOKEN.search(blob)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_system_adapter.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.system_adapter'`

- [ ] **Step 3: Write minimal implementation**

```python
# apps/sim-capacity/src/closedloop/system_adapter.py
"""SystemAdapter seam (Sprint 38 M0, design spec Sec 5.3). Only the EPIC twin
ships this sprint; the protocol makes SuccessFactors/LMS additive later. The
adapter derives demand/capacity envelopes from SimState using the shared
``build_envelope`` helper — the downstream envelope shape is unchanged."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List

from envelope import build_envelope
from closedloop.sim_state import SimState


class SystemAdapter(ABC):
    @abstractmethod
    def read_demand(self, simulated_at: datetime, sim_run_id: str, seed: int) -> List[dict]: ...


class EpicAdapter(SystemAdapter):
    def __init__(self, state: SimState) -> None:
        self._state = state

    def read_demand(self, simulated_at: datetime, sim_run_id: str, seed: int) -> List[dict]:
        s = self._state
        envelopes: List[dict] = []
        for bed in sorted(s.beds.values(), key=lambda b: b.bed_id):
            envelopes.append(build_envelope(
                event_kind="bed_state",
                hospital_id=s.hospital_id,
                simulated_at=simulated_at,
                payload={"bedId": bed.bed_id, "wardId": bed.ward_id, "state": bed.state},
                sim_run_id=sim_run_id, seed=seed,
            ))
        for ward_id in sorted(s.wards):
            ward = s.wards[ward_id]
            envelopes.append(build_envelope(
                event_kind="ward_occupancy",
                hospital_id=s.hospital_id,
                simulated_at=simulated_at,
                payload={
                    "wardId": ward_id,
                    "bedCapacity": ward.staffed_capacity,
                    "occupiedBeds": s.occupancy(ward_id),
                },
                sim_run_id=sim_run_id, seed=seed,
            ))
        return envelopes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_system_adapter.py -q`
Expected: PASS (3 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/sim-capacity/src/closedloop/system_adapter.py apps/sim-capacity/tests/test_system_adapter.py
git commit -m "feat(sim): add SystemAdapter seam + EpicAdapter demand derivation (Sprint 38 M0)"
```

---

## M1 — Stateful tick

### Task 4: `advance_state` time transitions

**Files:**

- Create: `apps/sim-capacity/src/closedloop/tick.py`
- Test: `apps/sim-capacity/tests/test_tick.py`

- [ ] **Step 1: Write the failing test**

```python
# apps/sim-capacity/tests/test_tick.py
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.tick import advance_state


def test_tick_ages_open_barriers_by_one_hour():
    s = build_sim_state("USZ", 3, [("C3", "internal-medicine", 20)])
    before = {b.barrier_id: b.aged_h for b in s.barriers.values() if b.status == "open"}
    advance_state(s, random.Random(3))
    for bid, aged in before.items():
        assert s.barriers[bid].aged_h == aged + 1


def test_tick_is_deterministic_for_same_seed():
    a = build_sim_state("USZ", 5, [("C3", "internal-medicine", 20)])
    b = build_sim_state("USZ", 5, [("C3", "internal-medicine", 20)])
    for _ in range(5):
        advance_state(a, random.Random(99))
        advance_state(b, random.Random(99))
    assert a.snapshot() == b.snapshot()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_tick.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.tick'`

- [ ] **Step 3: Write minimal implementation**

```python
# apps/sim-capacity/src/closedloop/tick.py
"""Stateful tick (Sprint 38 M1, design spec Sec 5.2). Advances time-driven
transitions on the persistent twin. Fully deterministic: all randomness comes
from the injected ``random.Random``; no wall-clock reads."""
from __future__ import annotations

import random

from closedloop.sim_state import SimState, Stage


def advance_state(state: SimState, rng: random.Random) -> None:
    """Advance the twin by one simulated hour: age open barriers, and promote a
    small deterministic fraction of INPATIENT to DISCHARGE_READY (LOS maturing).
    Applied approved actions are handled separately by the ActuationConsumer
    (M2); this function only models autonomous time transitions."""
    for barrier in state.barriers.values():
        if barrier.status == "open":
            barrier.aged_h += 1

    inpatients = sorted(state.patients_in_stage(Stage.INPATIENT), key=lambda p: p.patient_id)
    for patient in inpatients:
        if rng.random() < 0.05:
            patient.journey_stage = Stage.DISCHARGE_READY
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_tick.py -q`
Expected: PASS (2 passed)

- [ ] **Step 5: Commit**

```bash
git add apps/sim-capacity/src/closedloop/tick.py apps/sim-capacity/tests/test_tick.py
git commit -m "feat(sim): add deterministic stateful tick transitions (Sprint 38 M1)"
```

---

## M2 — Lever effects + ActuationConsumer

### Task 5: Extend the lever schema with an `effect` block

**Files:**

- Modify: `data-platform/decision/levers/lever.schema.json`
- Test: `apps/sim-capacity/tests/test_effect.py` (schema-load assertion added here in Task 6; this task only widens the schema)

- [ ] **Step 1: Read the current schema to find the lever `properties` object**

Run: `cd ../..; sed -n '1,80p' data-platform/decision/levers/lever.schema.json` (from `apps/sim-capacity`, or open the file directly)
Expected: a JSON Schema whose lever object lists `lever_id`, `preconditions`, `params_schema`, `impact_formula_ref`, `hitl` under `properties`.

- [ ] **Step 2: Add the optional `effect` property**

Add this key inside the lever object's `"properties"` map (do not add it to `required`):

```json
"effect": {
  "type": "object",
  "description": "Declarative state mutation applied to SimState when the action is HITL-approved (Sprint 38, ADR-0057). Interpreted by apps/sim-capacity/src/closedloop/effect.py.",
  "required": ["applies_to", "mutation"],
  "properties": {
    "applies_to": { "type": "string", "enum": ["DischargeBarrier", "Patient", "Bed"] },
    "mutation": { "type": "string", "enum": ["set_status", "set_stage", "free_bed"] },
    "from": { "type": "string" },
    "to": { "type": "string" },
    "select_by": { "type": "string", "enum": ["barrier_type", "stage", "ward"] },
    "cascade": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["when", "set"],
        "properties": {
          "when": { "type": "string" },
          "set": { "type": "string" }
        }
      }
    }
  }
}
```

- [ ] **Step 3: Validate the JSON parses**

Run: `python -c "import json,pathlib; json.loads(pathlib.Path('data-platform/decision/levers/lever.schema.json').read_text())"`
Expected: no output, exit 0

- [ ] **Step 4: Commit**

```bash
git add data-platform/decision/levers/lever.schema.json
git commit -m "feat(decision): add optional lever effect schema for sim actuation (Sprint 38 M2)"
```

### Task 6: Add the `effect` block to `DCA-UNBLOCK-BARRIER` + effect interpreter

**Files:**

- Modify: `data-platform/decision/levers/dca.yaml`
- Create: `apps/sim-capacity/src/closedloop/effect.py`
- Test: `apps/sim-capacity/tests/test_effect.py`

- [ ] **Step 1: Write the failing test**

```python
# apps/sim-capacity/tests/test_effect.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state, Stage
from closedloop.effect import apply_effect

UNBLOCK_BARRIER_EFFECT = {
    "applies_to": "DischargeBarrier",
    "mutation": "set_status",
    "from": "open",
    "to": "cleared",
    "select_by": "barrier_type",
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGE_READY"}],
}


def test_unblock_barrier_clears_n_barriers_and_frees_beds():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    open_before = len(s.open_barriers("transport"))
    assert open_before >= 2  # seed 42 guarantees barriers to clear
    delta = apply_effect(s, UNBLOCK_BARRIER_EFFECT, {"barrier_type": "transport", "n": 2})
    assert len(s.open_barriers("transport")) == open_before - 2
    assert delta["metric"] == "beds_freed"
    assert delta["delta"] == 2
    assert len(delta["state_delta"]["beds_freed"]) == 2


def test_effect_is_bounded_by_available_barriers():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    open_before = len(s.open_barriers("transport"))
    delta = apply_effect(s, UNBLOCK_BARRIER_EFFECT, {"barrier_type": "transport", "n": open_before + 5})
    assert delta["delta"] == open_before  # cannot clear more than exist
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_effect.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.effect'`

- [ ] **Step 3: Write the effect interpreter**

```python
# apps/sim-capacity/src/closedloop/effect.py
"""Declarative lever-effect interpreter (Sprint 38 M2, design spec Sec 6.2).

Reads a lever's declared ``effect`` block and executes the corresponding
SimState mutation deterministically. Adding a lever == adding a YAML effect
block; no new Python. Returns a realised-delta dict shaped to mirror
``compute_expected_impact`` so the OutcomeRecorder can compare predicted vs
realised on the same metric axis."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.sim_state import SimState, Stage


def _free_bed_for_patient(state: SimState, patient_id: str) -> str | None:
    for bed in sorted(state.beds.values(), key=lambda b: b.bed_id):
        if bed.patient_id == patient_id and bed.state == "occupied":
            bed.state = "available"
            bed.patient_id = None
            return bed.bed_id
    return None


def apply_effect(state: SimState, effect: Dict[str, Any], params: Dict[str, Any]) -> Dict[str, Any]:
    """Execute ``effect`` against ``state`` bounded by ``params['n']``.

    Currently implements the ``set_status`` mutation on ``DischargeBarrier``
    with a ``patient_all_barriers_cleared`` cascade that discharges the patient
    and frees their bed — the mutation the four journey levers share. Returns
    ``{metric, delta, state_delta}`` where ``delta`` is the realised bed-relief
    magnitude."""
    if effect["applies_to"] != "DischargeBarrier" or effect["mutation"] != "set_status":
        raise ValueError(f"unsupported effect: {effect.get('applies_to')}/{effect.get('mutation')}")

    barrier_type = params["barrier_type"]
    n = int(params["n"])
    candidates = sorted(state.open_barriers(barrier_type), key=lambda b: b.barrier_id)[:n]

    freed_beds: list[str] = []
    discharged: list[str] = []
    for barrier in candidates:
        barrier.status = effect["to"]
        patient_id = barrier.patient_id
        remaining = [b for b in state.barriers.values()
                     if b.patient_id == patient_id and b.status == "open"]
        if not remaining and patient_id in state.patients:
            state.patients[patient_id].journey_stage = Stage.DISCHARGED
            bed_id = _free_bed_for_patient(state, patient_id)
            if bed_id:
                freed_beds.append(bed_id)
            discharged.append(patient_id)

    return {
        "metric": "beds_freed",
        "delta": len(freed_beds),
        "state_delta": {"beds_freed": sorted(freed_beds), "patients_discharged": sorted(discharged)},
    }
```

- [ ] **Step 4: Add the `effect` block to `DCA-UNBLOCK-BARRIER`**

Append this `effect:` block under the `DCA-UNBLOCK-BARRIER` lever in `data-platform/decision/levers/dca.yaml` (sibling of `impact_formula_ref`, matching the existing 4-space indentation):

```yaml
    effect:
      applies_to: DischargeBarrier
      mutation: set_status
      from: open
      to: cleared
      select_by: barrier_type
      cascade:
        - when: patient_all_barriers_cleared
          set: "Patient.stage=DISCHARGED"
```

Scope note: only `DCA-UNBLOCK-BARRIER` gets an `effect` block this task — it is the sole lever the interpreter and the E2E journey exercise. The other confirmed levers (`OOA-EXPEDITE-DISCHARGE`, `BMCA-REBALANCE-CENSUS`, `ORSA-DEFER-ELECTIVE`, `SBA-FLEX-STAFF-BEDS`) each need a *distinct* mutation (promote-to-discharge-ready, move-patient-between-wards, free-OR-slot, flex-capacity), so reusing the barrier-clear effect for them would be semantically wrong. Those land in the multi-agent enrichment tracked in the Follow-on section, not this task.

- [ ] **Step 5: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_effect.py -q`
Expected: PASS (2 passed)

- [ ] **Step 6: Commit**

```bash
git add apps/sim-capacity/src/closedloop/effect.py apps/sim-capacity/tests/test_effect.py data-platform/decision/levers/dca.yaml
git commit -m "feat(sim): add declarative lever-effect interpreter + DCA effect block (Sprint 38 M2)"
```

### Task 7: `ActuationConsumer` applies approved decision-tier actions

**Files:**

- Create: `apps/sim-capacity/src/closedloop/actuation.py`
- Test: `apps/sim-capacity/tests/test_actuation.py`

The consumer reads a decision-tier `PlanStore` (duck-typed: `list_actions`, `get_action`, `upsert_action`) and applies **only** actions the decision-tier already marked `"applied"` (i.e. HITL-approved via `approve_action`). It stamps `sim_applied_at` so re-runs are idempotent, and it maps a lever's declared `effect` (looked up from an injected `effect_by_lever` dict) to a SimState mutation via `apply_effect`.

- [ ] **Step 1: Write the failing test**

```python
# apps/sim-capacity/tests/test_actuation.py
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SRC = ROOT / "apps" / "sim-capacity" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from closedloop.sim_state import build_sim_state
from closedloop.actuation import ActuationConsumer

EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
}


class FakePlanStore:
    """Minimal PlanStore stand-in matching coordination.store.PlanStore's surface."""
    def __init__(self):
        self._actions = {}
        self._order = []

    def create_action(self, a):
        self._actions[a["id"]] = dict(a)
        self._order.append(a["id"])

    def get_action(self, aid):
        return dict(self._actions[aid]) if aid in self._actions else None

    def upsert_action(self, a):
        self._actions[a["id"]] = dict(a)

    def list_actions(self, plan_id):
        return [dict(self._actions[i]) for i in self._order if self._actions[i]["plan_id"] == plan_id]


def _approved_action(aid, delta):
    return {
        "id": aid, "plan_id": "plan-ep1", "role": "dca",
        "lever_id": "DCA-UNBLOCK-BARRIER", "params": {"barrier_type": "transport", "n": 2},
        "expected_impact": {"metric": "beds", "delta": delta},
        "status": "applied", "hitl_approver": "alice",
    }


def test_consumer_applies_approved_action_to_state():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = FakePlanStore()
    store.create_action(_approved_action("a0", 2))
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    outcomes = consumer.apply_approved("plan-ep1", s)
    assert len(outcomes) == 1
    assert outcomes[0]["realised_impact"]["value"] == 2
    assert store.get_action("a0")["sim_applied_at"] is not None


def test_consumer_is_idempotent():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = FakePlanStore()
    store.create_action(_approved_action("a0", 2))
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    consumer.apply_approved("plan-ep1", s)
    second = consumer.apply_approved("plan-ep1", s)  # already actuated
    assert second == []


def test_consumer_refuses_unapproved_action():
    s = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = FakePlanStore()
    proposed = _approved_action("a0", 2)
    proposed["status"] = "proposed"  # NOT yet HITL-approved
    store.create_action(proposed)
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    assert consumer.apply_approved("plan-ep1", s) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_actuation.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.actuation'`

- [ ] **Step 3: Write minimal implementation**

```python
# apps/sim-capacity/src/closedloop/actuation.py
"""ActuationConsumer (Sprint 38 M2, design spec Sec 6). Applies HITL-approved
decision-tier actions to SimState. It never approves anything: it only acts on
actions the decision-tier already moved to status 'applied' via approve_action
(which enforces the bot/self-approval refusal). Idempotent per action id via a
'sim_applied_at' stamp."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List

from closedloop.effect import apply_effect
from closedloop.outcome import build_sim_outcome


class ActuationConsumer:
    def __init__(self, plan_store: Any, effect_by_lever: Dict[str, Dict[str, Any]]) -> None:
        self._store = plan_store
        self._effects = effect_by_lever

    def apply_approved(self, plan_id: str, state, now: str | None = None) -> List[Dict[str, Any]]:
        """Apply every approved-but-not-yet-actuated action for ``plan_id``.
        Returns the list of DC-SIM-OUTCOME-v1 records produced."""
        stamp = now or datetime.now(tz=timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        outcomes: List[Dict[str, Any]] = []
        for action in self._store.list_actions(plan_id):
            if action.get("status") != "applied":
                continue  # only HITL-approved actions
            if action.get("sim_applied_at"):
                continue  # idempotency guard
            effect = self._effects.get(action["lever_id"])
            if effect is None:
                continue
            pre = state.snapshot()
            realised = apply_effect(state, effect, action["params"])
            post = state.snapshot()
            outcomes.append(build_sim_outcome(action, pre, post, realised, applied_ts=stamp))
            action["sim_applied_at"] = stamp
            self._store.upsert_action(action)
        return outcomes
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_actuation.py -q`
Expected: PASS (3 passed) — note this depends on `outcome.build_sim_outcome` from Task 8; if you are running strictly in order, implement Task 8 first or temporarily stub `build_sim_outcome`. Recommended: do Task 8 before running this step.

- [ ] **Step 5: Commit**

```bash
git add apps/sim-capacity/src/closedloop/actuation.py apps/sim-capacity/tests/test_actuation.py
git commit -m "feat(sim): add ActuationConsumer applying HITL-approved actions (Sprint 38 M2)"
```

---

## M3 — `DC-SIM-OUTCOME-v1` + OutcomeRecorder

### Task 8: `DC-SIM-OUTCOME-v1` schema + `build_sim_outcome`

**Files:**

- Create: `data/synthetic/schema/dc-sim-outcome-v1.schema.json`
- Create: `apps/sim-capacity/src/closedloop/outcome.py`
- Test: `apps/sim-capacity/tests/test_outcome.py`

- [ ] **Step 1: Write the failing test**

```python
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
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_outcome.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.outcome'`

- [ ] **Step 3: Write the schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://curavias/schema/dc-sim-outcome-v1.schema.json",
  "title": "DC-SIM-OUTCOME-v1",
  "type": "object",
  "required": ["contract", "cosmos_id", "plan_id", "golden_thread", "lever_id", "applied_ts", "predicted_impact", "realised_impact", "state_delta", "divergence", "provenance"],
  "additionalProperties": true,
  "properties": {
    "contract": { "const": "DC-SIM-OUTCOME-v1" },
    "cosmos_id": { "type": "string" },
    "plan_id": { "type": "string" },
    "golden_thread": { "type": "string" },
    "lever_id": { "type": "string" },
    "applied_ts": { "type": "string" },
    "predicted_impact": { "type": "object", "required": ["metric", "value"] },
    "realised_impact": { "type": "object", "required": ["metric", "value"] },
    "state_delta": { "type": "object" },
    "divergence": { "type": "number", "minimum": 0 },
    "provenance": { "const": "simulated" }
  }
}
```

- [ ] **Step 4: Write `build_sim_outcome`**

```python
# apps/sim-capacity/src/closedloop/outcome.py
"""DC-SIM-OUTCOME-v1 builder (Sprint 38 M3, design spec Sec 6.3). PHI-free by
construction: synthetic bed/patient IDs only. Divergence is the normalised gap
between the agent's predicted impact and the simulator's realised impact — the
single signal the M5 learning slice consumes."""
from __future__ import annotations

from typing import Any, Dict


def build_sim_outcome(
    action: Dict[str, Any],
    pre_state: Dict[str, Any],
    post_state: Dict[str, Any],
    realised: Dict[str, Any],
    applied_ts: str,
) -> Dict[str, Any]:
    predicted_value = int(action.get("expected_impact", {}).get("delta", 0))
    realised_value = int(realised.get("delta", 0))
    denom = max(abs(predicted_value), abs(realised_value), 1)
    divergence = round(abs(predicted_value - realised_value) / denom, 4)
    return {
        "contract": "DC-SIM-OUTCOME-v1",
        "cosmos_id": action["id"],
        "plan_id": action["plan_id"],
        "golden_thread": action.get("golden_thread", action["plan_id"]),
        "lever_id": action["lever_id"],
        "applied_ts": applied_ts,
        "predicted_impact": {"metric": realised.get("metric", "beds"), "value": predicted_value},
        "realised_impact": {"metric": realised.get("metric", "beds"), "value": realised_value},
        "state_delta": realised.get("state_delta", {}),
        "divergence": divergence,
        "provenance": "simulated",
    }
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_outcome.py tests/test_actuation.py -q`
Expected: PASS (all pass — Task 7 tests now resolve `build_sim_outcome`)

- [ ] **Step 6: Commit**

```bash
git add data/synthetic/schema/dc-sim-outcome-v1.schema.json apps/sim-capacity/src/closedloop/outcome.py apps/sim-capacity/tests/test_outcome.py
git commit -m "feat(sim): add DC-SIM-OUTCOME-v1 contract + divergence recorder (Sprint 38 M3)"
```

---

## M4 — End-to-end closed-loop journey harness

### Task 9: Shared journey definition

**Files:**

- Create: `apps/sim-capacity/src/closedloop/journey.py`

The MVP `CANONICAL_JOURNEY` is a DCA-driven walking skeleton (the one lever with an implemented `effect`), which fully proves the closed-loop mechanism. Enriching it to the spec's multi-agent OOA->DCA->BMCA->ORSA path is the Follow-on item that lands once each role's `effect` mutation exists.

- [ ] **Step 1: Write the journey definition (no test yet — it is data consumed by Task 10)**

```python
# apps/sim-capacity/src/closedloop/journey.py
"""Shared closed-loop journey definition (Sprint 38 M4, design spec Sec 7.1).

A journey is an ordered list of steps; each step names the agent role, the
lever it should propose, and the params. The SAME definition drives the CI
harness (Task 10) and the demo-able interactive run, so the two never diverge."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(frozen=True)
class JourneyStep:
    role: str
    lever_id: str
    params: Dict[str, Any]
    approver: str


CANONICAL_JOURNEY: List[JourneyStep] = [
    JourneyStep("dca", "DCA-UNBLOCK-BARRIER", {"barrier_type": "transport", "n": 2}, approver="alice"),
    JourneyStep("dca", "DCA-UNBLOCK-BARRIER", {"barrier_type": "transport", "n": 1}, approver="bob"),
]
```

- [ ] **Step 2: Commit**

```bash
git add apps/sim-capacity/src/closedloop/journey.py
git commit -m "feat(sim): add shared closed-loop journey definition (Sprint 38 M4)"
```

### Task 10: End-to-end closed-loop test (happy path + failure modes)

**Files:**

- Test: `apps/sim-capacity/tests/test_e2e_closed_loop.py`

This test wires the **real decision-tier** (`coordination.store.InMemoryStore`, `coordination.plan_runtime`, `impact.compute_expected_impact`) to the **new sim closed loop**. It adds both `src` roots to `sys.path`. It builds `gold` (a forecast row) from `SimState` occupancy so `compute_expected_impact` is grounded in the twin, proposes an action, HITL-approves it with a scripted human, runs the `ActuationConsumer`, and asserts the trajectory changed and divergence is within tolerance.

- [ ] **Step 1: Write the end-to-end tests**

```python
# apps/sim-capacity/tests/test_e2e_closed_loop.py
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
SIM_SRC = ROOT / "apps" / "sim-capacity" / "src"
DEC_SRC = ROOT / "data-platform" / "decision"
for p in (SIM_SRC, DEC_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.sim_state import build_sim_state, Stage
from closedloop.actuation import ActuationConsumer
from closedloop.journey import CANONICAL_JOURNEY
from coordination.store import InMemoryStore
from coordination import plan_runtime

EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
}
CATALOG = [{
    "lever_id": "DCA-UNBLOCK-BARRIER", "owner_role": "dca",
    "impact_formula_ref": "unblock_barrier_beds",
}]


def _gold_from_state(state, ward="C3", horizon_h=72):
    cap = state.ward(ward).staffed_capacity
    return {"forecast": [{"wardId": ward, "horizonH": horizon_h,
                          "bedCapacity": cap, "forecastOccupiedBeds": state.occupancy(ward)}]}


def _open_plan(store, state, ward="C3"):
    return plan_runtime.open_plan(
        store, episode_key="ep1", ward=ward,
        bed_capacity=state.ward(ward).staffed_capacity,
        baseline_occupied_beds=state.occupancy(ward), target_pct=90,
    )


def test_happy_path_closes_the_loop():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    beds_free_before = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    store = InMemoryStore()
    plan = _open_plan(store, state)
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})

    all_outcomes = []
    for step in CANONICAL_JOURNEY:
        gold = _gold_from_state(state)
        action = plan_runtime.propose_action(
            store, plan_id=plan["id"], role=step.role, lever_id=step.lever_id,
            params={**step.params, "ward": "C3"}, gold=gold, catalog=CATALOG,
            proposed_by=step.role,
        )
        plan_runtime.approve_action(
            store, action_id=action["id"], approver=step.approver, gold=gold, catalog=CATALOG,
        )
        all_outcomes.extend(consumer.apply_approved(plan["id"], state, now="1970-01-01T00:00:00Z"))

    beds_free_after = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    total_freed = sum(o["realised_impact"]["value"] for o in all_outcomes)
    assert total_freed > 0                                      # the loop actually did something
    assert beds_free_after - beds_free_before == total_freed    # state change == recorded realised outcomes
    assert all_outcomes[0]["divergence"] == 0.0                 # first step: predicted == realised (deterministic)


def test_approval_withheld_does_not_change_trajectory():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    beds_free_before = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    # No approve_action call — the human withheld approval.
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    outcomes = consumer.apply_approved(plan["id"], state)
    beds_free_after = sum(1 for b in state.beds_in_ward("C3") if b.state == "available")
    assert outcomes == []
    assert beds_free_after == beds_free_before           # trajectory unchanged


def test_self_approval_is_refused_by_decision_tier():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    action = plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    with pytest.raises(PermissionError, match="self-approval"):
        plan_runtime.approve_action(store, action_id=action["id"], approver="dca", gold=gold, catalog=CATALOG)


def test_second_apply_is_idempotent():
    state = build_sim_state("USZ", 42, [("C3", "internal-medicine", 30)])
    store = InMemoryStore()
    plan = _open_plan(store, state)
    gold = _gold_from_state(state)
    action = plan_runtime.propose_action(
        store, plan_id=plan["id"], role="dca", lever_id="DCA-UNBLOCK-BARRIER",
        params={"barrier_type": "transport", "n": 2, "ward": "C3"}, gold=gold, catalog=CATALOG,
        proposed_by="dca",
    )
    plan_runtime.approve_action(store, action_id=action["id"], approver="alice", gold=gold, catalog=CATALOG)
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": EFFECT})
    consumer.apply_approved(plan["id"], state, now="1970-01-01T00:00:00Z")
    assert consumer.apply_approved(plan["id"], state, now="1970-01-01T00:00:00Z") == []   # already actuated
```

- [ ] **Step 2: Run the end-to-end test**

Run: `cd apps/sim-capacity; python -m pytest tests/test_e2e_closed_loop.py -q`
Expected: PASS (4 passed). If `coordination`/`impact` import fails, confirm `DEC_SRC` points at `data-platform/decision` and that `data-platform/decision/coordination/__init__.py` and `impact/__init__.py` exist (they do).

- [ ] **Step 3: Run the whole sim-capacity suite to confirm no regressions**

Run: `cd apps/sim-capacity; python -m pytest -q`
Expected: PASS (all prior generator/clock/PHI tests still green + the new closed-loop tests)

- [ ] **Step 4: Commit**

```bash
git add apps/sim-capacity/tests/test_e2e_closed_loop.py
git commit -m "test(sim): add end-to-end closed-loop journey (happy path + failure modes) (Sprint 38 M4)"
```

---

## Docs, contract registration, and ADR

### Task 11: Register the contract, requirements, and ADR

**Files:**

- Modify: `docs/DATA.md`
- Modify: `docs/PRD.md`
- Create: `docs/adr/0057-sim-outcome-and-effect-schema.md`

- [ ] **Step 1: Register `DC-SIM-OUTCOME-v1` in `docs/DATA.md`**

Add a row to the data-contract table (near the `DC-AGENT-INTERACTION-v1` row at line ~145) and a container/retention note mirroring the existing style:

```markdown
| Sim-outcome contract | DC-SIM-OUTCOME-v1 | Closed-loop operational outcome: one PHI-free record per HITL-approved action applied to the EPIC twin, with predicted-vs-realised divergence (Sprint 38). R3 retention alongside DC-AGENT-INTERACTION-v1. |
```

- [ ] **Step 2: Add the requirements to `docs/PRD.md`**

Add a new FR family block (activating the reserved `FR-SIM-*` namespace referenced by `FR-ONT-005`) and the `NFR-SIM-*` rows, copying the exact IDs and text from the design spec §14 (`FR-SIM-001`..`FR-SIM-006`, `FR-CLP-001`..`FR-CLP-003`, `NFR-SIM-001`..`NFR-SIM-003`). Add a §7 traceability row:

```markdown
| [`docs/superpowers/specs/2026-07-31-sprint-38-epic-closed-loop-simulation-engine-design.md`](superpowers/specs/2026-07-31-sprint-38-epic-closed-loop-simulation-engine-design.md) + [`docs/adr/0057-sim-outcome-and-effect-schema.md`](adr/0057-sim-outcome-and-effect-schema.md) *(Sprint 38: EPIC closed-loop simulation engine — stateful twin, HITL-approved actuation, DC-SIM-OUTCOME-v1, E2E journey)* | `FR-SIM-001` to `FR-SIM-006`, `FR-CLP-001` to `FR-CLP-003`, `NFR-SIM-001` to `NFR-SIM-003` |
```

Bump the `docs/PRD.md` version header MINOR (additive) and update **Previous Version** per §9.

- [ ] **Step 3: Write ADR-0057**

```markdown
# ADR-0057: Sim-outcome contract, lever effect schema, and sim-as-ground-truth

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-31 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 38 design](../superpowers/specs/2026-07-31-sprint-38-epic-closed-loop-simulation-engine-design.md), [ADR-0040](0040-prescriptive-decision-ontology-and-runtime-store.md), [ADR-0055](0055-closed-loop-learning-capture-and-eval.md), [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), `NFR-AI-001` |

## Context

Sprint 38 closes the operational loop: the EPIC simulator applies HITL-approved
agent actions back to patient-flow state. Three cross-cutting decisions underpin
every milestone and any future lever that joins the loop, so they are fixed here.

## Decision

1. **`DC-SIM-OUTCOME-v1` (ratified).** One PHI-free record per applied action,
   capturing pre/post state delta and predicted-vs-realised `divergence`, linked
   by `plan_id` / `golden_thread` / `cosmos_id`. Validated by
   `data/synthetic/schema/dc-sim-outcome-v1.schema.json`. Retained R3 alongside
   `DC-AGENT-INTERACTION-v1` (ADR-0055).
2. **Declarative lever `effect` schema.** Each lever may declare an `effect`
   block (state mutation) alongside its `impact_formula_ref` (metric prediction).
   The `apps/sim-capacity` effect interpreter executes it; adding a lever is a
   YAML change, not new Python.
3. **Sim-as-ground-truth, human-gated.** The simulator is the ground truth agents
   are graded against, but it applies **only** actions a human moved to
   `approved-to-apply` (ADR-0007, `NFR-AI-001`). Every outcome is stamped
   `provenance: simulated`; this is not clinical actuation.

## Consequences

Predicted-vs-realised divergence becomes the operational signal the Sprint 30
learning loop (ADR-0055) consumes in Sprint 38 M5. No PHI, no autonomous action.
```

- [ ] **Step 4: Run the doc gates**

Run: `cd ../..; python scripts/lint/check_mojibake.py docs/DATA.md docs/PRD.md docs/adr/0057-sim-outcome-and-effect-schema.md; npx --yes markdownlint-cli2 "docs/DATA.md" "docs/PRD.md" "docs/adr/0057-sim-outcome-and-effect-schema.md"`
Expected: `OK: no mojibake` + `Summary: 0 issues`

- [ ] **Step 5: Commit**

```bash
git add docs/DATA.md docs/PRD.md docs/adr/0057-sim-outcome-and-effect-schema.md
git commit -m "docs: register DC-SIM-OUTCOME-v1, FR-SIM/FR-CLP/NFR-SIM, ADR-0057 (Sprint 38)"
```

---

## Self-review checklist (run after implementing)

- [ ] **Spec coverage:** M0 (Tasks 1-3), M1 (Task 4), M2 (Tasks 5-7), M3 (Task 8), M4 (Tasks 9-10), docs/ADR (Task 11). M5 (finetuning slice) is the explicit follow-on plan.
- [ ] **`NFR-AI-001`:** the consumer applies only `status == "applied"` (HITL-approved) actions; `test_approval_withheld_*` and `test_self_approval_is_refused_*` prove the boundary; every outcome is `provenance: simulated`.
- [ ] **Determinism:** `test_build_is_deterministic`, `test_tick_is_deterministic_for_same_seed`, and the seeded E2E prove reproducibility (no wall-clock in computed values).
- [ ] **Type consistency:** `build_sim_outcome(action, pre, post, realised, applied_ts)` signature matches its one caller in `actuation.py`; `apply_effect(state, effect, params)` matches its callers in `effect` tests and `actuation.py`; `Stage` enum values are stable strings.
- [ ] **No cross-package import hacks:** the consumer is duck-typed on `PlanStore`; only the E2E test imports the real decision-tier, via the documented dual-`sys.path` pattern.

---

## Follow-on plan (M5 — not in this plan)

`docs/superpowers/plans/YYYY-MM-DD-sprint-38-m5-finetuning-slice.md` (create when we reach it):

- Add an `outcome_divergence` evaluator to `evals/lib/` that scores `DC-SIM-OUTCOME-v1` records the way existing evaluators score conversations.
- Capture `DC-SIM-OUTCOME-v1` alongside `DC-AGENT-INTERACTION-v1` at the Sprint 30 choke point.
- Feed high-divergence journeys through the existing `evals/curate_job.py` → `evals/prompt_optimize_job.py` / `evals/finetune_plan_job.py` (draft only, human-gated).
- Add a **calibration gate**: a batch assertion that the sim's outcome distribution is internally consistent (occupancy accounting balances; no state leaks). This is the "simulator is working" check.

**Multi-agent journey enrichment (M4 follow-on):** extend the effect interpreter with per-role mutations — `OOA-EXPEDITE-DISCHARGE` (INPATIENT -> DISCHARGE_READY), `BMCA-REBALANCE-CENSUS` (move a patient between wards), `ORSA-DEFER-ELECTIVE` (free an OR slot), `SBA-FLEX-STAFF-BEDS` (raise effective capacity) — then extend `CANONICAL_JOURNEY` to the full OOA->DCA->BMCA->ORSA path from design spec §7.1.
