# Sprint 39 Plan 1 — Real-Gold Evidence Backbone Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a reproducible, per-role **`DC-EVIDENCE-TRACE-v1`** for one synthetic patient's journey through the capacity agents, driven on **real EPIC-simulator data** (a materialized gold snapshot the sim already produces), with an **accept** branch (bed freed) and a **deny** branch (breach persists) — the backend/data backbone the app surface (Plan 2) renders.

**Architecture:** Reuse the Sprint 38 closed-loop engine + the real decision tier. Add (1) a `gold_seed` that maps a materialized sim **gold snapshot** into a Sprint 38 `SimState`, and (2) an `evidence` harness that seeds from gold, walks `CANONICAL_JOURNEY` via `plan_runtime` (propose → approve/deny) + `ActuationConsumer` + `build_sim_outcome`, and emits `DC-EVIDENCE-TRACE-v1` (accept + deny). Deterministic (fixed seed, `now=` sentinel), PHI-free, CI-runnable; live SIT gold backs it at runtime (Plan 2 / operator step).

**Tech Stack:** Python 3.11, pytest (`parents[3]/src` sys.path convention), reuse `closedloop/{sim_state,effect,actuation,outcome,journey}.py`, `coordination.plan_runtime`, `impact.compute_expected_impact`, `evals/lib/sim_outcome_eval.py`.

**Scope note:** Sprint 39 is two plans (design §Confirmed direction). **This is Plan 1 — the backend evidence backbone** (no UI). **Plan 2** (its own file) adds the app per-role evidence panel + demo-E2E walk and the agent-host `/worklist` + `/decisions` operational loop; it benefits from the live app walk + `ux-design-agent`. `FR-UXL-*` and the app `FR-EVD-003/004/005` are Plan 2.

**Working directory for tests:** `apps/sim-capacity` (`cd apps/sim-capacity; python -m pytest`). The evidence-scoring test runs from repo root. PowerShell: chain with `;`, never `&&`.

---

## File structure

| File | Responsibility |
|------|----------------|
| `data/synthetic/schema/dc-evidence-trace-v1.schema.json` *(create)* | The `DC-EVIDENCE-TRACE-v1` JSON Schema contract. |
| `apps/sim-capacity/src/closedloop/gold_seed.py` *(create)* | `seed_sim_state_from_gold(gold)` — map a materialized sim gold snapshot into a Sprint 38 `SimState`. |
| `apps/sim-capacity/src/closedloop/evidence.py` *(create)* | `build_evidence_trace(gold, branch)` — seed + walk the journey + emit `DC-EVIDENCE-TRACE-v1` (accept/deny). |
| `apps/sim-capacity/tests/fixtures/gold-snapshot-usz.json` *(create)* | A deterministic materialized gold snapshot (real-sim-shaped) for CI. |
| `apps/sim-capacity/tests/test_gold_seed.py` *(create)* | Seeder unit tests. |
| `apps/sim-capacity/tests/test_evidence.py` *(create)* | Harness tests (accept applies, deny no-op, schema-valid, PHI-free). |
| `evals/lib/tests/test_evidence_scoring.py` *(create)* | The evidence outcomes pass the M5 calibration gate. |
| `docs/DATA.md` *(modify)* | Register `DC-EVIDENCE-TRACE-v1`. |
| `docs/adr/0059-evidence-trace-and-surface.md` *(create)* | Ratify `DC-EVIDENCE-TRACE-v1` + the evidence-surface/provenance pattern. |
| `docs/PRD.md` *(modify)* | Add `FR-EVD-001/002` + `NFR-EVD-001/002` + §7 row (app FRs land in Plan 2). |

---

## Task 1: `DC-EVIDENCE-TRACE-v1` schema

**Files:**

- Create: `data/synthetic/schema/dc-evidence-trace-v1.schema.json`

- [ ] **Step 1: Write the schema**

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://curavias/schema/dc-evidence-trace-v1.schema.json",
  "title": "DC-EVIDENCE-TRACE-v1",
  "type": "object",
  "required": ["contract", "golden_thread", "patient", "branch", "generated_ts", "steps"],
  "additionalProperties": true,
  "properties": {
    "contract": { "const": "DC-EVIDENCE-TRACE-v1" },
    "golden_thread": { "type": "string" },
    "patient": { "type": "object", "required": ["synthetic_id", "provenance"] },
    "branch": { "enum": ["accept", "deny"] },
    "generated_ts": { "type": "string" },
    "steps": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["role", "agent", "journey_stage", "epic_input", "agent_read", "recommendation", "copilot", "action", "outcome"],
        "properties": {
          "role": { "type": "string" },
          "agent": { "type": "string" },
          "journey_stage": { "type": "string" },
          "epic_input": { "type": "object", "required": ["provenance"] },
          "agent_read": { "type": "object" },
          "recommendation": { "type": "object", "required": ["lever_id", "predicted_impact"] },
          "copilot": { "type": "object", "required": ["decision", "requiresApproval"] },
          "action": { "type": "object", "required": ["status"] },
          "outcome": { "type": "object", "required": ["provenance"] }
        }
      }
    }
  }
}
```

- [ ] **Step 2: Validate the JSON parses**

Run: `python -c "import json,pathlib; json.loads(pathlib.Path('data/synthetic/schema/dc-evidence-trace-v1.schema.json').read_text())"`
Expected: exit 0, no output.

- [ ] **Step 3: Commit**

```bash
git add data/synthetic/schema/dc-evidence-trace-v1.schema.json
git commit -m "feat(evidence): add DC-EVIDENCE-TRACE-v1 contract (Sprint 39 P1)"
```

## Task 2: `gold_seed` — SimState from a materialized gold snapshot

**Files:**

- Create: `apps/sim-capacity/src/closedloop/gold_seed.py`
- Create: `apps/sim-capacity/tests/fixtures/gold-snapshot-usz.json`
- Test: `apps/sim-capacity/tests/test_gold_seed.py`

- [ ] **Step 1: Write the deterministic gold snapshot fixture**

This is the materialized current-state view of the sim's gold (bed states + encounters + discharge scores + barriers), the same shape the app Live toggle reads. Ids are consistent (a bed's `patientId` == an encounter's `encounterId` == a barrier's `encounterId`).

```json
{
  "hospital_id": "USZ",
  "captured_ts": "2027-01-15T08:00:00Z",
  "provenance": "simulated",
  "wards": [{ "wardId": "C3", "specialty": "internal-medicine", "bedCapacity": 8 }],
  "beds": [
    { "bedId": "BED-C3-00", "wardId": "C3", "state": "occupied", "patientId": "PT-0001" },
    { "bedId": "BED-C3-01", "wardId": "C3", "state": "occupied", "patientId": "PT-0002" },
    { "bedId": "BED-C3-02", "wardId": "C3", "state": "occupied", "patientId": "PT-0003" },
    { "bedId": "BED-C3-03", "wardId": "C3", "state": "occupied", "patientId": "PT-0004" },
    { "bedId": "BED-C3-04", "wardId": "C3", "state": "occupied", "patientId": "PT-0005" },
    { "bedId": "BED-C3-05", "wardId": "C3", "state": "occupied", "patientId": "PT-0006" },
    { "bedId": "BED-C3-06", "wardId": "C3", "state": "available", "patientId": null },
    { "bedId": "BED-C3-07", "wardId": "C3", "state": "available", "patientId": null }
  ],
  "encounters": [
    { "encounterId": "PT-0001", "specialty": "internal-medicine", "acuity": 2, "status": "inpatient" },
    { "encounterId": "PT-0002", "specialty": "internal-medicine", "acuity": 2, "status": "inpatient" },
    { "encounterId": "PT-0003", "specialty": "internal-medicine", "acuity": 1, "status": "inpatient" },
    { "encounterId": "PT-0004", "specialty": "internal-medicine", "acuity": 1, "status": "inpatient" },
    { "encounterId": "PT-0005", "specialty": "internal-medicine", "acuity": 2, "status": "inpatient" },
    { "encounterId": "PT-0006", "specialty": "internal-medicine", "acuity": 1, "status": "inpatient" }
  ],
  "discharge_scores": [
    { "encounterId": "PT-0001", "score": 0.92 },
    { "encounterId": "PT-0002", "score": 0.88 },
    { "encounterId": "PT-0003", "score": 0.85 }
  ],
  "barriers": [
    { "barrierId": "BAR-PT-0001", "encounterId": "PT-0001", "barrierType": "transport", "status": "open", "agedH": 18 },
    { "barrierId": "BAR-PT-0002", "encounterId": "PT-0002", "barrierType": "transport", "status": "open", "agedH": 9 },
    { "barrierId": "BAR-PT-0003", "encounterId": "PT-0003", "barrierType": "transport", "status": "open", "agedH": 6 }
  ]
}
```

- [ ] **Step 2: Write the failing test**

```python
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
```

- [ ] **Step 3: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_gold_seed.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.gold_seed'`

- [ ] **Step 4: Write the implementation**

```python
# apps/sim-capacity/src/closedloop/gold_seed.py
"""Seed a Sprint 38 SimState from a materialized EPIC-simulator gold snapshot
(Sprint 39 P1).

The gold snapshot is the current-state materialisation of the sim's gold event
streams (bed.state_changed / encounter.* / discharge.scored) — the same shape the
app Live toggle reads. This maps it into the SimState so the evidence harness (and
the Plan 2 operational loop) run on REAL simulator data: a captured deterministic
snapshot for CI, live SIT gold at runtime. PHI-free: synthetic ids only."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.sim_state import Bed, DischargeBarrier, Patient, SimState, Stage, Ward

# encounter status -> journey stage
_STATUS_STAGE = {
    "arrived": Stage.ARRIVAL,
    "triaged": Stage.TRIAGE,
    "admitted": Stage.ADMIT,
    "in-progress": Stage.INPATIENT,
    "inpatient": Stage.INPATIENT,
    "discharge-ready": Stage.DISCHARGE_READY,
    "finished": Stage.DISCHARGED,
    "discharged": Stage.DISCHARGED,
}

# a discharge-readiness score at/above this promotes an inpatient to DISCHARGE_READY
_READY_SCORE = 0.8


def seed_sim_state_from_gold(gold: Dict[str, Any]) -> SimState:
    """Map a materialized gold snapshot into a SimState. Ids are taken verbatim
    (synthetic); a bed's ``patientId`` is expected to match an encounter's
    ``encounterId`` and a barrier's ``encounterId`` for the discharge cascade."""
    state = SimState(hospital_id=gold["hospital_id"])

    for w in gold.get("wards", []):
        state.wards[w["wardId"]] = Ward(
            ward_id=w["wardId"],
            specialty=w.get("specialty", ""),
            staffed_capacity=int(w["bedCapacity"]),
        )

    scores = {s["encounterId"]: float(s["score"]) for s in gold.get("discharge_scores", [])}
    for enc in gold.get("encounters", []):
        pid = enc["encounterId"]
        stage = _STATUS_STAGE.get(str(enc.get("status", "inpatient")).lower(), Stage.INPATIENT)
        if stage == Stage.INPATIENT and scores.get(pid, 0.0) >= _READY_SCORE:
            stage = Stage.DISCHARGE_READY
        state.patients[pid] = Patient(
            patient_id=pid,
            acuity=int(enc.get("acuity", 2)),
            specialty=enc.get("specialty", ""),
            journey_stage=stage,
        )

    for b in gold.get("beds", []):
        state.beds[b["bedId"]] = Bed(
            bed_id=b["bedId"],
            ward_id=b["wardId"],
            state=b["state"],
            patient_id=b.get("patientId"),
        )

    for br in gold.get("barriers", []):
        state.barriers[br["barrierId"]] = DischargeBarrier(
            barrier_id=br["barrierId"],
            patient_id=br["encounterId"],
            barrier_type=br["barrierType"],
            status=br.get("status", "open"),
            aged_h=int(br.get("agedH", 0)),
        )

    return state
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_gold_seed.py -q`
Expected: PASS (4 passed)

- [ ] **Step 6: Commit**

```bash
git add apps/sim-capacity/src/closedloop/gold_seed.py apps/sim-capacity/tests/fixtures/gold-snapshot-usz.json apps/sim-capacity/tests/test_gold_seed.py
git commit -m "feat(evidence): seed SimState from a materialized EPIC gold snapshot (Sprint 39 P1)"
```

## Task 3: `evidence` harness — accept + deny traces on real gold

**Files:**

- Create: `apps/sim-capacity/src/closedloop/evidence.py`
- Test: `apps/sim-capacity/tests/test_evidence.py`

The harness seeds a SimState from the gold snapshot, then walks `CANONICAL_JOURNEY` via the **real** decision tier (`plan_runtime.propose_action` → `approve_action` on the accept branch, no approve on the deny branch) + `ActuationConsumer` + `build_sim_outcome`, capturing one `DC-EVIDENCE-TRACE-v1` step per journey step. It builds `gold` for `compute_expected_impact` from the seeded SimState occupancy so the recommendation is grounded on the real snapshot.

- [ ] **Step 1: Write the failing test**

```python
# apps/sim-capacity/tests/test_evidence.py
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SIM_SRC = ROOT / "apps" / "sim-capacity" / "src"
DEC_SRC = ROOT / "data-platform" / "decision"
for p in (SIM_SRC, DEC_SRC):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.evidence import build_evidence_trace

_GOLD = json.loads((Path(__file__).parent / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))
_SCHEMA = json.loads((ROOT / "data" / "synthetic" / "schema" / "dc-evidence-trace-v1.schema.json").read_text(encoding="utf-8"))
_PHI = re.compile(r"\b\d{3}[-.]?\d{2}[-.]?\d{4}\b")


def test_accept_branch_frees_beds_and_records_outcome():
    trace = build_evidence_trace(_GOLD, branch="accept")
    assert trace["contract"] == "DC-EVIDENCE-TRACE-v1"
    assert trace["branch"] == "accept"
    dca = next(s for s in trace["steps"] if s["role"] == "dca")
    assert dca["copilot"]["decision"] == "accept"
    assert dca["action"]["status"] == "applied"
    assert dca["outcome"]["realised_impact"]["value"] >= 1


def test_deny_branch_changes_nothing():
    trace = build_evidence_trace(_GOLD, branch="deny")
    dca = next(s for s in trace["steps"] if s["role"] == "dca")
    assert dca["copilot"]["decision"] == "deny"
    assert dca["action"]["status"] == "denied"
    assert dca["outcome"]["realised_impact"]["value"] == 0


def test_trace_is_schema_valid_and_threaded():
    trace = build_evidence_trace(_GOLD, branch="accept")
    for key in _SCHEMA["required"]:
        assert key in trace
    assert trace["golden_thread"]
    assert all(s.get("epic_input", {}).get("provenance") in ("simulated", "live") for s in trace["steps"])


def test_trace_is_phi_free():
    trace = build_evidence_trace(_GOLD, branch="accept")
    assert not _PHI.search(json.dumps(trace))
    assert trace["patient"]["provenance"] in ("simulated", "live")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd apps/sim-capacity; python -m pytest tests/test_evidence.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'closedloop.evidence'`

- [ ] **Step 3: Write the implementation**

```python
# apps/sim-capacity/src/closedloop/evidence.py
"""Evidence-trace harness (Sprint 39 P1, design §4/§6).

Seeds a SimState from a materialized EPIC gold snapshot and walks
CANONICAL_JOURNEY through the REAL decision tier + Sprint 38 closed-loop engine,
emitting a DC-EVIDENCE-TRACE-v1 with an accept branch (approve every step -> apply
-> outcome) and a deny branch (withhold approval -> no apply -> breach persists).
Deterministic (fixed `now`), PHI-free. Live SIT gold backs it at runtime; a
captured snapshot backs CI. Requires both apps/sim-capacity/src and
data-platform/decision on sys.path (the test adds them)."""
from __future__ import annotations

from typing import Any, Dict, List

from closedloop.actuation import ActuationConsumer
from closedloop.gold_seed import seed_sim_state_from_gold
from closedloop.journey import CANONICAL_JOURNEY
from coordination import plan_runtime
from coordination.store import InMemoryStore

_NOW = "1970-01-01T00:00:00Z"

# The one lever with a Sprint 38 effect; the effect the ActuationConsumer applies.
_EFFECT = {
    "applies_to": "DischargeBarrier", "mutation": "set_status",
    "from": "open", "to": "cleared", "select_by": "barrier_type",
    "cascade": [{"when": "patient_all_barriers_cleared", "set": "Patient.stage=DISCHARGED"}],
}
_CATALOG = [{"lever_id": "DCA-UNBLOCK-BARRIER", "owner_role": "dca", "impact_formula_ref": "unblock_barrier_beds"}]
# lever -> the agent that owns it (for the evidence step's `agent` label)
_AGENT_BY_LEVER = {"DCA-UNBLOCK-BARRIER": "dca-agent"}


def _gold_for_impact(state, ward: str, horizon_h: int = 72) -> Dict[str, Any]:
    return {"forecast": [{
        "wardId": ward, "horizonH": horizon_h,
        "bedCapacity": state.ward(ward).staffed_capacity,
        "forecastOccupiedBeds": state.occupancy(ward),
    }]}


def build_evidence_trace(gold: Dict[str, Any], branch: str = "accept") -> Dict[str, Any]:
    """Build a DC-EVIDENCE-TRACE-v1 for ``branch`` in {"accept","deny"}."""
    if branch not in ("accept", "deny"):
        raise ValueError(f"branch must be 'accept' or 'deny', got {branch!r}")

    state = seed_sim_state_from_gold(gold)
    provenance = gold.get("provenance", "simulated")
    ward = next(iter(sorted(state.wards)))
    store = InMemoryStore()
    plan = plan_runtime.open_plan(
        store, episode_key="ev1", ward=ward,
        bed_capacity=state.ward(ward).staffed_capacity,
        baseline_occupied_beds=state.occupancy(ward), target_pct=90,
    )
    consumer = ActuationConsumer(store, {"DCA-UNBLOCK-BARRIER": _EFFECT})
    golden_thread = f"gt-{plan['id']}"

    steps: List[Dict[str, Any]] = []
    for js in CANONICAL_JOURNEY:
        impact_gold = _gold_for_impact(state, ward)
        occupied_before = state.occupancy(ward)
        params = {**js.params, "ward": ward}
        action = plan_runtime.propose_action(
            store, plan_id=plan["id"], role=js.role, lever_id=js.lever_id,
            params=params, gold=impact_gold, catalog=_CATALOG, proposed_by=js.role, now=_NOW,
        )
        predicted = int(action["expected_impact"]["delta"])

        if branch == "accept":
            plan_runtime.approve_action(
                store, action_id=action["id"], approver=js.approver,
                gold=impact_gold, catalog=_CATALOG, now=_NOW,
            )
            outcomes = consumer.apply_approved(plan["id"], state, now=_NOW)
            outcome = outcomes[-1] if outcomes else _noop_outcome(action, provenance)
            decision, status = "accept", "applied"
        else:
            outcome = _noop_outcome(action, provenance)
            decision, status = "deny", "denied"

        steps.append({
            "role": js.role,
            "agent": _AGENT_BY_LEVER.get(js.lever_id, f"{js.role}-agent"),
            "journey_stage": "DISCHARGE_READY",
            "epic_input": {
                "wardId": ward,
                "occupiedBeds": occupied_before,
                "bedCapacity": state.ward(ward).staffed_capacity,
                "citations": ["gold.fact_occupancy_forecast", "gold.bed_assignment"],
                "provenance": provenance,
            },
            "agent_read": {"signal": f"{js.params.get('n')} discharge-ready blocked by {js.params.get('barrier_type')} barriers on {ward}"},
            "recommendation": {
                "lever_id": js.lever_id, "params": params,
                "predicted_impact": {"metric": "beds", "value": predicted},
                "insight_text": f"Resolve {js.params.get('n')} {js.params.get('barrier_type')} barriers to free beds on {ward}",
            },
            "copilot": {"requiresApproval": True, "decision": decision, "approver": js.approver, "decision_ts": _NOW},
            "action": {"cosmos_id": action["id"], "status": status},
            "outcome": outcome,
        })

    return {
        "contract": "DC-EVIDENCE-TRACE-v1",
        "golden_thread": golden_thread,
        "patient": {"synthetic_id": "PT-0001", "specialty": gold.get("wards", [{}])[0].get("specialty", ""), "provenance": provenance},
        "branch": branch,
        "generated_ts": _NOW,
        "steps": steps,
    }


def _noop_outcome(action: Dict[str, Any], provenance: str) -> Dict[str, Any]:
    return {
        "contract": "DC-SIM-OUTCOME-v1", "cosmos_id": action["id"], "plan_id": action["plan_id"],
        "golden_thread": f"gt-{action['plan_id']}", "lever_id": action["lever_id"], "applied_ts": _NOW,
        "predicted_impact": {"metric": "beds", "value": int(action["expected_impact"]["delta"])},
        "realised_impact": {"metric": "beds_freed", "value": 0},
        "state_delta": {"beds_freed": [], "patients_discharged": [], "patients_promoted": []},
        "divergence": round(abs(int(action["expected_impact"]["delta"]) - 0) / max(int(action["expected_impact"]["delta"]), 1), 4),
        "provenance": provenance,
    }
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd apps/sim-capacity; python -m pytest tests/test_evidence.py -q`
Expected: PASS (4 passed). If `coordination`/`impact` import fails, confirm `DEC_SRC` = `data-platform/decision` (its `coordination/` and `impact/` packages have `__init__.py`).

- [ ] **Step 5: Run the whole closedloop suite (no regressions)**

Run: `cd apps/sim-capacity; python -m pytest tests/test_sim_state.py tests/test_state_store.py tests/test_system_adapter.py tests/test_tick.py tests/test_effect.py tests/test_outcome.py tests/test_actuation.py tests/test_e2e_closed_loop.py tests/test_gold_seed.py tests/test_evidence.py -q`
Expected: PASS (all)

- [ ] **Step 6: Commit**

```bash
git add apps/sim-capacity/src/closedloop/evidence.py apps/sim-capacity/tests/test_evidence.py
git commit -m "feat(evidence): add DC-EVIDENCE-TRACE-v1 harness on real gold (accept + deny) (Sprint 39 P1)"
```

## Task 4: Score the evidence outcomes via the M5 calibration gate

**Files:**

- Create: `evals/lib/tests/test_evidence_scoring.py`

The accept-branch outcomes are `DC-SIM-OUTCOME-v1` records; they must pass the Sprint 38 M5 calibration gate and score zero divergence (predicted == realised on the deterministic snapshot).

- [ ] **Step 1: Write the failing test**

```python
# evals/lib/tests/test_evidence_scoring.py
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
for p in (ROOT / "apps" / "sim-capacity" / "src", ROOT / "data-platform" / "decision"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.evidence import build_evidence_trace
from lib.sim_outcome_eval import run_calibration_gate, outcome_divergence

_GOLD = json.loads((ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))


def test_accept_outcomes_pass_the_calibration_gate():
    trace = build_evidence_trace(_GOLD, branch="accept")
    outcomes = [s["outcome"] for s in trace["steps"] if s["action"]["status"] == "applied"]
    assert outcomes, "accept branch produced at least one applied outcome"
    report = run_calibration_gate(outcomes)
    assert report["passed"]
    assert all(outcome_divergence(o).passed for o in outcomes)
```

- [ ] **Step 2: Run test to verify it fails, then passes**

Run: `cd ../..` (repo root) then `python -m pytest evals/lib/tests/test_evidence_scoring.py -q`
Expected: PASS (1 passed). If it fails on divergence, the seeded occupancy makes `compute_expected_impact` predict more beds than the 2 barriers free — confirm the fixture has exactly 2 open `transport` barriers and the journey's first step requests `n=2`.

- [ ] **Step 3: Commit**

```bash
git add evals/lib/tests/test_evidence_scoring.py
git commit -m "test(evidence): evidence outcomes pass the M5 calibration gate (Sprint 39 P1)"
```

## Task 5: Register the contract, ADR, and requirements

**Files:**

- Modify: `docs/DATA.md`
- Create: `docs/adr/0059-evidence-trace-and-surface.md`
- Modify: `docs/PRD.md`

- [ ] **Step 1: Register `DC-EVIDENCE-TRACE-v1` in `docs/DATA.md`**

Add a row to the data-contract table near the `DC-SIM-OUTCOME-v1` row:

```markdown
| Evidence-trace contract | DC-EVIDENCE-TRACE-v1 | Per-role end-to-end proof for one synthetic patient journey (EPIC input -> read -> recommendation -> copilot accept/deny -> outcome), accept + deny branches, PHI-free, `golden_thread`-linked; a derived view of the operational loop (Sprint 39). |
```

Bump the `docs/DATA.md` version MINOR (additive), update **Previous Version** + **Date** = 2026-08-01, per §9.

- [ ] **Step 2: Write ADR-0059**

```markdown
# ADR-0059: Evidence-trace contract and per-role evidence surface

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-08-01 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 39 design](../superpowers/specs/2026-08-01-epic-closed-loop-sit-evidence-e2e-design.md), [ADR-0058](0058-sim-outcome-and-effect-schema.md), [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), `NFR-AI-001` |

## Context

Sprint 39 proves the closed loop end-to-end per role on real EPIC-simulator data,
shown as a demo E2E flow and per-role interaction. The proof needs a stable,
PHI-free contract and a provenance discipline.

## Decision

1. **`DC-EVIDENCE-TRACE-v1` (ratified).** One PHI-free record per synthetic
   patient journey; an ordered array of per-role steps (EPIC input, read,
   recommendation, copilot accept/deny, action, outcome), `golden_thread`-linked;
   accept + deny branches. Validated by `data/synthetic/schema/dc-evidence-trace-v1.schema.json`.
2. **Real-gold, seeded, human-gated.** Read/recommendation run on real SIT gold
   (a captured snapshot backs CI); apply/outcome run on an in-host `SimState`
   seeded from that gold. Only a human accept fires an apply (`NFR-AI-001`); deny
   changes nothing. No live write-back to the running sim this sprint.
3. **Provenance honesty.** Every part is badged `simulated` or `live`; a
   `simulated` part is never rendered as `live`. The evidence trace is a derived
   view of the same operational-loop records (validation == user experience).

## Consequences

The per-role evidence surface (Plan 2) renders these records; the operational loop
(Plan 2) produces them. No PHI, no autonomous action, no deploy this sprint.
```

- [ ] **Step 3: Add requirements to `docs/PRD.md`**

Add a new FR family block with `FR-EVD-001`, `FR-EVD-002` and `NFR-EVD-001`, `NFR-EVD-002` copied verbatim from the design spec §14 (the app-facing `FR-EVD-003/004/005` + `FR-UXL-*` land in Plan 2). Add a §7 traceability row referencing the Sprint 39 design + ADR-0059. Bump `docs/PRD.md` MINOR, update **Previous Version** + **Date**.

- [ ] **Step 4: Run the doc gates**

Run from repo root: `python scripts/lint/check_mojibake.py docs/DATA.md docs/PRD.md docs/adr/0059-evidence-trace-and-surface.md; npx --yes markdownlint-cli2 "docs/DATA.md" "docs/PRD.md" "docs/adr/0059-evidence-trace-and-surface.md"`
Expected: `OK: no mojibake` + `Summary: 0 issues`.

- [ ] **Step 5: Commit**

```bash
git add docs/DATA.md docs/PRD.md docs/adr/0059-evidence-trace-and-surface.md
git commit -m "docs: register DC-EVIDENCE-TRACE-v1, ADR-0059, FR-EVD (Sprint 39 P1)"
```

---

## Self-review checklist (run after implementing)

- [ ] **Spec coverage:** Task 1 (contract), Task 2 (real-gold seed), Task 3 (accept+deny harness on real gold), Task 4 (scored), Task 5 (docs/ADR). App surface + operational loop are **Plan 2**.
- [ ] **Real data:** the harness runs on the gold snapshot (real-sim-shaped); at runtime the same seeder reads live SIT gold. No fabricated bed/patient data beyond the captured snapshot.
- [ ] **`NFR-AI-001`:** accept applies, deny is a no-op; the harness uses the real `approve_action` (bot/self refused). Deny branch's `realised_impact.value == 0`.
- [ ] **Determinism + PHI-free:** fixed `now`, seeded snapshot; `test_trace_is_phi_free` + `provenance` on every part.
- [ ] **Type consistency:** `build_evidence_trace(gold, branch)` and `seed_sim_state_from_gold(gold)` signatures match their callers; the outcome dict shape matches `DC-SIM-OUTCOME-v1` (`realised_impact.value`).

---

## Follow-on: Plan 2 (its own file, after the app walk)

`docs/superpowers/plans/2026-08-DD-sprint-39-p2-operational-ux-surface.md`:

- Agent-host `GET /agents/{role}/worklist` (real gold -> observations + recommendations) + `POST /agents/{role}/decisions` (accept/deny -> in-host SimState apply -> `DC-SIM-OUTCOME-v1`), HITL evidence = app user oid.
- App: per-role evidence panel + **demo E2E patient-flow walk** (mode a); live per-role worklist + **copilot act-to-proceed** + outcome feedback (mode b); accept/deny **side-by-side** (routed to `ux-design-agent` with Playwright a11y/visual verification).
- The evidence trace becomes the derived view of the operational loop (validation == UX). Realises `FR-EVD-003/004/005`, `FR-UXL-001..004`.
- Requires a **live app walk** to pin the worklist/copilot selectors before authoring the UI tasks.
