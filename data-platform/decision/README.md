# Decision lane

> **Sprint 26 Slice 1** (issue #335): the WS-B/C "actionable-insight" decision
> lane implementing the 5-beat `DC-INSIGHT-v1` contract for the OOA -> DCA
> golden thread (Medicine A / 102% -> 94% / 72h).

## Purpose

Through Sprint 25 the platform's copilots were descriptive-only. This lane
turns the OOA -> DCA pair **prescriptive**: every grounded answer is assembled
as a `signal` / `understanding` / `recommendation` / `action` / `coordination`
tuple plus `provenance` (the `DC-INSIGHT-v1` envelope), not a free-form
sentence. See
[ADR-0040](../../docs/adr/0040-prescriptive-decision-ontology-and-runtime-store.md)
and the
[design spec](../../docs/superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md)
§3.1-§3.5, §4 (WS-B/C/D) for the full rationale.

## Pieces

| Piece | Files | Role |
| ----- | ----- | ---- |
| **Contract** | [`data/synthetic/schema/dc-insight-v1.schema.json`](../../data/synthetic/schema/dc-insight-v1.schema.json) | The 5-beat + provenance JSON-schema envelope (draft-07, `additionalProperties:false`); see [`tests/test_contract_conformance.py`](tests/test_contract_conformance.py). |
| **Lever catalog** | [`levers/lever.schema.json`](levers/lever.schema.json) + [`levers/*.yaml`](levers/) | Governed response levers per role, **fully specified for all six roles**: OOA (`OOA-EXPEDITE-DISCHARGE`, `OOA-DIVERT-LOW-ACUITY`), DCA (`DCA-UNBLOCK-BARRIER`), BMCA (`BMCA-REBALANCE-CENSUS`), ORSA (`ORSA-DEFER-ELECTIVE`), SBA (`SBA-FLEX-STAFF-BEDS`), and CSA (`CSA-ACTIVATE-SURGE`). |
| **Impact tool** | [`impact/compute_expected_impact.py`](impact/compute_expected_impact.py) | `compute_expected_impact(lever_id, params, gold)` — a **pure, deterministic, forecast-grounded** function over WS-A gold occupancy-forecast/driver data. **Never an LLM estimate**: the number behind a ranked recommendation must be auditable and reproducible. |
| **Barrier model** | [`barriers/derive_barriers.py`](barriers/derive_barriers.py) + [`barriers/build_gold_barrier.py`](barriers/build_gold_barrier.py) | `derive_barriers(candidates)` — a pure, runtime-derived function that ranks/collapses discharge-barrier candidates for the DCA role. `build_gold_barrier.build_discharge_barriers(...)` materialises the same ranked barriers to the `gold.fact_discharge_barrier` Delta table (contract [`DC-DISCHARGE-BARRIER-v1`](../../data/synthetic/schema/dc-discharge-barrier-v1.schema.json); grounds `hcp:Barrier`), reusing `derive_barriers` verbatim — Spark I/O is Fabric-only, orchestrated by [`../notebooks/decision/run_decision_medallion.ipynb`](../notebooks/decision/run_decision_medallion.ipynb). |
| **Coordination runtime** | [`coordination/store.py`](coordination/store.py) + [`coordination/plan_runtime.py`](coordination/plan_runtime.py) + [`coordination/seed_slice1.py`](coordination/seed_slice1.py) + [`coordination/seed_fanout.py`](coordination/seed_fanout.py) | `open_plan` -> `propose_action` -> HITL `approve_action` -> deterministic recompute (102% -> 94%) -> OOA -> DCA handoff, over a `Store` protocol (in-memory for tests; Cosmos is a thin, gated implementation). `seed_fanout.py` extends the same shape to the four fan-out roles (BMCA/ORSA/SBA/CSA), each a self-owned golden thread. |
| **Live-apply tooling (WS-C)** | [`coordination/cosmos_store.py`](coordination/cosmos_store.py) + [`coordination/seed_live.py`](coordination/seed_live.py) + [`foundry/register_decision_tier.py`](foundry/register_decision_tier.py) + [`foundry/live_factory.py`](foundry/live_factory.py) | `CosmosStore(PlanStore)` (RBAC-only, no keys) over the `plans`/`proposed_actions` containers; a HITL-gated live seed replaying all six roles (`--action plan` dry run / `--action apply --approved-to-apply <handle>`); a Foundry decision-tier registration tool for the six agents; and `live_factory.py`, the concrete Foundry Agents (Assistants) REST factory the registration `apply` calls in-VNet. The SIT Cosmos account is private-endpoint only ([ADR-0029](../../docs/adr/0029-agent-host-cosmos-reachability.md)) and Foundry is eastus2 ([ADR-0032](../../docs/adr/0032-foundry-control-plane-eastus2.md)), so a real apply runs in-VNet via the `caj-decision-apply` Container Apps Job ([runbook](../../docs/runbooks/decision-tier-live-apply.md)), never from CI. |

## Responsibility split

The read-only **Fabric Data Agent** (`da_hospital_capacity`) stays a grounding
tool: it emits only the descriptive `signal`, `understanding`, and
`provenance` beats. The **agent-host** assembles `recommendation`, `action`,
and `coordination` at runtime for each copilot and mediates the Cosmos
`proposed_actions` / `plans` writes — so OOA and DCA keep their `write`
side-effect ceiling and need no `cosmos-mcp` grant of their own (see
[ADR-0029](../../docs/adr/0029-agent-host-cosmos-reachability.md)).

## Governance

Advisory-only, human-in-the-loop: an action may be `PROPOSED` autonomously but
is only `APPLIED` after a human posts the exact `approved-to-apply`
confirmation
([AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete)); the
runtime refuses self-approval and any bot-identity approver. All data is
synthetic / no-PHI; there is no source/EHR writeback.

## Running the tests

Runtime is `python` (**not** `python3`):

```bash
python -m unittest discover -s data-platform/decision -p "test_*.py" -v
```

## References

- [ADR-0040: Prescriptive Decision Ontology + Runtime Decision Store](../../docs/adr/0040-prescriptive-decision-ontology-and-runtime-store.md)
- [Sprint 26 decision-ontology design spec](../../docs/superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md)
