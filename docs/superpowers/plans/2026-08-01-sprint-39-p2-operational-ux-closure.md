# Sprint 39 Plan 2 — Operational-UX Closure (App + Agent-Host) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax. **UI tasks (Part B) are owned by the `ux-design-agent`**, which implements the Fluent UI changes and verifies with Playwright (visual + `@axe-core` a11y) per the app Scope Guard.

**Goal:** Close the operational loop in the live UX: each role sees its **live** observations + recommendations worklist, **acts** on an actionable insight via the copilot (**accept/deny**), and the **outcome flows back** into the worklist — driven by the agent-host hosting the closed-loop engine **in-process** on **real EPIC-sim gold** (seeded snapshot; no deploy, no live write-back). The evidence trace (Plan 1) becomes the derived proof view of this same loop.

**Architecture:** Add two agent-host endpoints — `GET /agents/{role}/worklist` (real-gold observations + `DC-INSIGHT`-style recommendations) and `POST /agents/{role}/decisions` (accept/deny → real `plan_runtime.approve_action` HITL → in-host `SimState.apply` via `ActuationConsumer` → `DC-SIM-OUTCOME-v1`). The in-host `SimState` is seeded from a gold snapshot via `gold_seed` (Plan 1). The app wires the **existing** worklist components + the `copilot-rail`/`copilot-drawer` `requiresApproval` CTA to these endpoints through the single IQ gateway, adds a **deny** affordance + a **side-by-side accept/deny** outcome view, reflects the returned outcome in the worklist, and adds a **per-role evidence panel** + a **demo E2E patient-flow walk** rendering the Plan 1 `DC-EVIDENCE-TRACE-v1`.

**Tech Stack:** Python 3.11 / FastAPI (agent-host), reuse `closedloop/{gold_seed,sim_state,actuation,outcome}.py` + `coordination.plan_runtime`; React 18 + Fluent UI v9 + TypeScript + Vitest + Playwright (app), reuse `iq-client.ts`, `copilot-rail/RecoPanel.tsx`, the worklist tables, and the Live/Simulated toggle.

**Scope note:** This is **Plan 2** of Sprint 39 (design [§3.5](../specs/2026-08-01-epic-closed-loop-sit-evidence-e2e-design.md)). It realises `FR-UXL-001..004`, `FR-EVD-003/004/005`, `NFR-UXL-001`. **Part A (agent-host)** is code-complete + TDD here. **Part B (app UI)** specifies tasks + acceptance; the `ux-design-agent` authors the Fluent implementation and verifies against the live app (`localhost:5173/main/discharge` etc.). **No deploy in this plan** — enabling in SIT is the gated image-tag bump (`agentHostImage`/`appFluentImage` in `infra/environments/sit.bicepparam` → `cd-infra-deploy-sit` → `cd-infra-deploy-prod`, `approved-to-apply`), done as a separate step after review.

**Working dirs:** agent-host tests `apps/hcc-agent-host` (`python -m pytest`); app tests `apps/hcc-app-fluent` (`npm run test`, `npm run test:e2e`). PowerShell: chain with `;`.

---

## Live-app grounding (from the 2026-08-01 walk)

| Surface | Where (live) | Plan 2 change |
|---------|--------------|---------------|
| Role boards | `/main/{belegung,bettenmanagement,op-steuerung,personal,entlassung,szenario}` = ooa/bmca/orsa/sba/dca/csa | unchanged layout; worklist + copilot get live wiring |
| Discharge worklist (observations) | `Entlass-Arbeitsliste` table, row buttons open the copilot | rows fed by `GET /agents/dca/worklist` when Live |
| Copilot act surface | `complementary "Agent"` panel — read + levers (`+N beds`) + primaryCta + projection + citations + follow-ups | add **accept/deny** per lever → `POST /decisions`; keep handoff |
| Data source | header `switch "Data source"` = Simulated/Live | Live routes worklist/reco to the agent-host on real gold |
| Golden thread | "carried from ooa-agent" handoff chip | evidence panel shows the `golden_thread` across roles |

---

## Part A — Agent-host operational loop (backend, code-complete + TDD)

### Task A1: In-host SimState registry + gold seeding

**Files:**

- Create: `apps/hcc-agent-host/src/loop/__init__.py`
- Create: `apps/hcc-agent-host/src/loop/sim_registry.py`
- Test: `apps/hcc-agent-host/tests/unit/test_sim_registry.py`

The agent-host hosts one in-memory `SimState` per hospital, seeded from a gold snapshot via the Plan 1 `gold_seed`. It imports the sim-capacity `closedloop` package (add `apps/sim-capacity/src` + `data-platform/decision` to the host's path — the host already composes multiple src roots; mirror that).

- [ ] **Step 1: Write the failing test**

```python
# apps/hcc-agent-host/tests/unit/test_sim_registry.py
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
for p in (ROOT / "apps" / "hcc-agent-host" / "src", ROOT / "apps" / "sim-capacity" / "src", ROOT / "data-platform" / "decision"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from loop.sim_registry import SimRegistry

_GOLD = json.loads((ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))


def test_registry_seeds_and_returns_state():
    reg = SimRegistry()
    state = reg.get_or_seed("USZ", _GOLD)
    assert state.hospital_id == "USZ"
    assert state.occupancy("C3") == 6
    # same hospital returns the same (stateful) instance
    assert reg.get_or_seed("USZ", _GOLD) is state


def test_reset_reseeds():
    reg = SimRegistry()
    first = reg.get_or_seed("USZ", _GOLD)
    reg.reset("USZ")
    second = reg.get_or_seed("USZ", _GOLD)
    assert second is not first
    assert second.snapshot() == first.snapshot()
```

- [ ] **Step 2: Run → fail** (`ModuleNotFoundError: loop.sim_registry`)

Run: `cd apps/hcc-agent-host; python -m pytest tests/unit/test_sim_registry.py -q`

- [ ] **Step 3: Implement**

```python
# apps/hcc-agent-host/src/loop/__init__.py
"""Sprint 39 P2 — in-host operational closed loop (worklist + decisions)."""
```

```python
# apps/hcc-agent-host/src/loop/sim_registry.py
"""In-host SimState registry (Sprint 39 P2). One stateful SimState per hospital,
seeded from a materialized gold snapshot via the sim-capacity gold_seed. In-memory
only (snapshot, not live write-back to the running sim). Reuses closedloop; no new
Azure resource."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.gold_seed import seed_sim_state_from_gold
from closedloop.sim_state import SimState


class SimRegistry:
    def __init__(self) -> None:
        self._by_hospital: Dict[str, SimState] = {}

    def get_or_seed(self, hospital_id: str, gold: Dict[str, Any]) -> SimState:
        if hospital_id not in self._by_hospital:
            self._by_hospital[hospital_id] = seed_sim_state_from_gold(gold)
        return self._by_hospital[hospital_id]

    def reset(self, hospital_id: str) -> None:
        self._by_hospital.pop(hospital_id, None)
```

- [ ] **Step 4: Run → pass; Commit**

```bash
git add apps/hcc-agent-host/src/loop/ apps/hcc-agent-host/tests/unit/test_sim_registry.py
git commit -m "feat(agent-host): in-host SimState registry seeded from gold (Sprint 39 P2)"
```

### Task A2: `GET /agents/{role}/worklist` — live observations + recommendations

**Files:**

- Create: `apps/hcc-agent-host/src/loop/worklist.py`
- Modify: `apps/hcc-agent-host/src/api/app.py` (add the route)
- Test: `apps/hcc-agent-host/tests/unit/test_worklist.py`, `apps/hcc-agent-host/tests/integration/test_worklist_api.py`

`build_worklist(role, state)` returns the role's observations (from `SimState`) + a `DC-INSIGHT`-shaped recommendation (lever + params + predicted impact via `compute_expected_impact` on the seeded occupancy). For `dca`: discharge-ready patients with open barriers + the `DCA-UNBLOCK-BARRIER` lever. The route reads gold via the existing golden-source seam (or the Plan 1 fixture in Simulated), seeds the registry, and returns the worklist.

- [ ] **Step 1: Write the failing unit test**

```python
# apps/hcc-agent-host/tests/unit/test_worklist.py
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
for p in (ROOT / "apps" / "hcc-agent-host" / "src", ROOT / "apps" / "sim-capacity" / "src", ROOT / "data-platform" / "decision"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from closedloop.gold_seed import seed_sim_state_from_gold
from loop.worklist import build_worklist

_GOLD = json.loads((ROOT / "apps" / "sim-capacity" / "tests" / "fixtures" / "gold-snapshot-usz.json").read_text(encoding="utf-8"))


def test_dca_worklist_lists_open_barrier_candidates_and_a_recommendation():
    state = seed_sim_state_from_gold(_GOLD)
    wl = build_worklist("dca", state, provenance="live")
    assert wl["role"] == "dca"
    assert len(wl["observations"]) == 3          # 3 open transport barriers
    assert all(o["provenance"] == "live" for o in wl["observations"])
    rec = wl["recommendation"]
    assert rec["lever_id"] == "DCA-UNBLOCK-BARRIER"
    assert rec["predicted_impact"]["value"] >= 1
    assert rec["citations"]
```

- [ ] **Step 2: Run → fail. Step 3: Implement**

```python
# apps/hcc-agent-host/src/loop/worklist.py
"""Role worklist builder (Sprint 39 P2). Turns the in-host SimState into a role's
observations + one grounded DC-INSIGHT-style recommendation. Deterministic; the
impact is the deterministic compute_expected_impact on the seeded occupancy (never
an LLM guess). MVP implements dca (the walking skeleton); other roles list
observations + a placeholder recommendation until their effect lands."""
from __future__ import annotations

from typing import Any, Dict

from closedloop.sim_state import SimState, Stage
from impact.compute_expected_impact import compute_expected_impact

_CATALOG = [{"lever_id": "DCA-UNBLOCK-BARRIER", "owner_role": "dca", "impact_formula_ref": "unblock_barrier_beds"}]


def _ward_of(state: SimState) -> str:
    return next(iter(sorted(state.wards)))


def build_worklist(role: str, state: SimState, provenance: str = "live") -> Dict[str, Any]:
    ward = _ward_of(state)
    citations = ["gold.discharge_candidates", "gold.fact_capacity_baseline"]
    if role == "dca":
        barriers = sorted(state.open_barriers("transport"), key=lambda b: b.barrier_id)
        observations = [
            {
                "patient": b.patient_id, "ward": ward, "readiness": "BLOCKED",
                "barrier": b.barrier_type, "aged_h": b.aged_h, "provenance": provenance,
            }
            for b in barriers
        ]
        n = len(barriers)
        gold_impact = {"forecast": [{"wardId": ward, "horizonH": 72,
                                     "bedCapacity": state.ward(ward).staffed_capacity,
                                     "forecastOccupiedBeds": state.occupancy(ward)}]}
        params = {"barrier_type": "transport", "n": n, "ward": ward}
        impact = compute_expected_impact("DCA-UNBLOCK-BARRIER", params, gold_impact, catalog=_CATALOG)
        recommendation = {
            "lever_id": "DCA-UNBLOCK-BARRIER", "params": params,
            "predicted_impact": {"metric": "beds", "value": int(impact["delta"])},
            "insight_text": f"Resolve {n} transport barriers to free {impact['delta']} beds on {ward}",
            "citations": citations,
        }
        return {"role": role, "ward": ward, "observations": observations,
                "recommendation": recommendation, "provenance": provenance}
    # Non-DCA roles: observations + advisory placeholder (full effect is follow-on).
    ready = [p.patient_id for p in state.patients_in_stage(Stage.DISCHARGE_READY)]
    return {"role": role, "ward": ward,
            "observations": [{"patient": p, "ward": ward, "readiness": "READY", "provenance": provenance} for p in ready],
            "recommendation": {"lever_id": None, "insight_text": "role effect pending (S38 multi-agent enrichment)", "citations": citations},
            "provenance": provenance}
```

Add the route in `apps/hcc-agent-host/src/api/app.py` inside `create_app()` (near the other `@app.get` routes). It loads the gold snapshot (the Plan 1 fixture when the host runs in Simulated; the live golden-source read when Live — reuse the existing `/golden` seam), seeds the registry on `state`, and returns `build_worklist`:

```python
    @app.get("/agents/{name}/worklist")
    def worklist(name: str, hospital: str = "USZ", x_user_oid: str = Header(default="")) -> dict[str, Any]:
        gold = state.load_gold_snapshot(hospital)         # golden-source seam (live) or Plan 1 fixture (simulated)
        sim = state.sim_registry.get_or_seed(hospital, gold)
        from loop.worklist import build_worklist
        return build_worklist(name, sim, provenance=gold.get("provenance", "simulated"))
```

(Wire `state.sim_registry = SimRegistry()` and a `load_gold_snapshot` helper on `HostState` — the integration test pins their contract.)

- [ ] **Step 4: Integration test + run + commit**

```python
# apps/hcc-agent-host/tests/integration/test_worklist_api.py
# Build the app with a stub gold loader returning the Plan 1 fixture; GET /agents/dca/worklist;
# assert 200 + 3 observations + the DCA-UNBLOCK-BARRIER recommendation.
```

```bash
git add apps/hcc-agent-host/src/loop/worklist.py apps/hcc-agent-host/src/api/app.py apps/hcc-agent-host/tests/unit/test_worklist.py apps/hcc-agent-host/tests/integration/test_worklist_api.py
git commit -m "feat(agent-host): GET /agents/{role}/worklist on real gold (Sprint 39 P2)"
```

### Task A3: `POST /agents/{role}/decisions` — accept/deny → apply → outcome

**Files:**

- Create: `apps/hcc-agent-host/src/loop/decisions.py`
- Modify: `apps/hcc-agent-host/src/api/app.py`
- Test: `apps/hcc-agent-host/tests/unit/test_decisions.py`, `apps/hcc-agent-host/tests/integration/test_decisions_api.py`

`decide(role, decision, approver, state, sim)` runs the real `plan_runtime.propose_action` → (accept) `approve_action(approver=user_oid)` → `ActuationConsumer.apply_approved` → `DC-SIM-OUTCOME-v1`; (deny) records a no-op. `NFR-AI-001`/`NFR-UXL-001`: the approver is the app user's Entra oid; bot/self is refused by `approve_action`; deny changes nothing.

- [ ] **Step 1: failing unit test** — accept frees beds + returns outcome `value >= 1`; deny returns `value == 0` and no state change; a bot approver raises/denies. (Mirror `apps/sim-capacity/tests/test_actuation.py` + the Plan 1 `test_evidence.py` accept/deny asserts.)
- [ ] **Step 2: implement** `decisions.py` reusing `plan_runtime` + `ActuationConsumer` + `build_sim_outcome` (the exact wiring from `closedloop/evidence.py`, but a single step driven by the request's `action_id`/lever, and applied to the registry's live `SimState`). Add the route:

```python
    @app.post("/agents/{name}/decisions")
    def decisions(name: str, req: DecisionRequest, x_user_oid: str = Header(default="")) -> dict[str, Any]:
        if not x_user_oid:
            raise HTTPException(status_code=401, detail="human approver (x-user-oid) required")
        sim = state.sim_registry.get_or_seed(req.hospital, state.load_gold_snapshot(req.hospital))
        from loop.decisions import decide
        return decide(name, req.decision, approver=x_user_oid, state=state, sim=sim, params=req.params)
```

- [ ] **Step 3: integration test** (accept applies + worklist shrinks on re-GET; deny no-op; missing `x-user-oid` → 401) + commit:

```bash
git commit -m "feat(agent-host): POST /agents/{role}/decisions - HITL accept/deny drives in-host apply->outcome (Sprint 39 P2)"
```

### Task A4: Agent-host suite green + docs

- [ ] Run `cd apps/hcc-agent-host; python -m pytest -q` — all green (no regressions).
- [ ] Register the two endpoints in `docs/ARCHITECTURE.md` / the agent-host README; note the in-host-SimState + no-deploy posture and the `approved-to-apply` gate for enabling in SIT. Doc gates + commit.

---

## Part B — App UI (owned by `ux-design-agent`; Playwright-verified)

> Dispatch these to the `ux-design-agent`. It implements the Fluent UI changes and **verifies against the live app** (`localhost:5173`) with Playwright (visual) + `@axe-core/playwright` (a11y). Each task keeps the existing layout; it wires data + adds the accept/deny + evidence surfaces.

### Task B1: Live worklist wiring (`FR-UXL-001`)

- The role worklist components (`DischargeWorklistTable`, `BedManagerBoard` placement worklist, `OrCaseScheduleTable`, `CoverageWorklistTable`, occupancy) read observations from `GET /agents/{role}/worklist` through the single IQ gateway (`iq-client.ts`) when **Live**; **Simulated** keeps today's fixtures. Provenance badge per row (`live`/`simulated`) reusing the existing badge.
- **Acceptance:** on `/main/entlassung` with Data source = Live, the `Entlass-Arbeitsliste` rows come from the endpoint; row count + barriers match `build_worklist("dca")`; Simulated is unchanged. Playwright test drives Live and asserts a row renders from the endpoint (mock the gateway response in test).

### Task B2: Copilot act-to-proceed — accept/deny (`FR-UXL-002/003`, `FR-EVD-004`)

- In the copilot "Agent" panel (`copilot-rail/RecoPanel.tsx`), add an **Accept** and a **Deny** control on the recommendation (the `requiresApproval` CTA becomes **Accept**; add a sibling **Deny**). On click, call `POST /agents/{role}/decisions` with the user oid. Render the returned outcome **side-by-side** (accept → beds freed + divergence; deny → breach persists), per the confirmed decision.
- On accept, **reflect the outcome in the worklist/board** (resolved candidate removed / bed freed / metric moved) by re-fetching the worklist.
- **`NFR-UXL-001`:** the app never applies directly; it only submits the human decision; the agent-host enforces the HITL gate. Keep the "advisory only / human decides" disclaimer already present.
- **Acceptance:** clicking Accept on the DCA reco frees beds and the worklist updates; Deny leaves it unchanged; both outcomes visible side-by-side. Playwright e2e covers accept + deny; axe a11y clean.

### Task B3: Per-role evidence panel + demo E2E walk (`FR-EVD-003/005`)

- A dedicated **"Closed-Loop Evidence"** surface (per-role) renders the Plan 1 `DC-EVIDENCE-TRACE-v1` five-part proof (EPIC input → read → recommendation → copilot accept/deny → outcome), `golden_thread` visible, per-part provenance. A **demo walk** steps one synthetic patient OOA→DCA→BMCA→ORSA (the canonical order), highlighting each role's evidence. Loads the trace via `iq-client` (Simulated = the Plan 1 fixture trace; Live = derived from the operational-loop records).
- **Acceptance:** the evidence panel shows the accept trace's 5 parts with the shared `golden_thread`; a branch toggle shows the deny trace; provenance badges correct. Playwright visual + axe a11y clean.

### Task B4: Validation == UX unification (`FR-UXL-004`)

- Ensure the evidence panel's records are the **same** `proposed_action` + `DC-SIM-OUTCOME-v1` the operational loop produced (not a separate replay): when Live, the evidence trace is assembled from the decisions the role actually made.
- **Acceptance:** a decision made in B2 appears in the B3 evidence panel for that role/`golden_thread`.

---

## Self-review checklist (after implementing)

- [ ] **Spec coverage:** A1-A3 = `FR-UXL-001/002/003` backend; B1-B4 = the app surfaces + `FR-EVD-003/004/005`, `FR-UXL-004`.
- [ ] **Real gold:** worklist + reco grounded on the seeded gold; `compute_expected_impact` on real occupancy.
- [ ] **`NFR-AI-001`/`NFR-UXL-001`:** only a human accept (with oid) fires an apply; bot/self refused; deny no-op; app never applies directly; missing oid → 401.
- [ ] **Provenance honesty:** every worklist/reco/outcome part badged `live`/`simulated`; never mislabeled.
- [ ] **No deploy:** this plan changes code only; enabling in SIT is the gated image-tag bump (separate, `approved-to-apply`).

---

## Enablement (separate, gated — after Plan 2 review)

To run Plan 2 live in SIT: bump `agentHostImage` + `appFluentImage` in `infra/environments/sit.bicepparam` to the new CI SHAs → triggers `cd-infra-deploy-sit` (approval-gated) → `cd-infra-deploy-prod` (`approved-to-apply`). No new Azure resources. PROD requires the explicit `approved-to-apply` confirm. Do NOT do this autonomously.
