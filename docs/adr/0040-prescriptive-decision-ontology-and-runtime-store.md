# ADR-0040: Prescriptive Decision Ontology + Runtime Decision Store

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-24 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | #335 |

## Context

Through Sprint 25, the platform's copilots (bmca, ooa, dca, orsa, sba, csa) and
the Fabric Data Agent (`da_hospital_capacity`) were **descriptive-only**: they
answer *"what is the occupancy now"* (and, after the Sprint 26 WS-A Foresight
tier, *"what will it be in 72h and why"*), grounded on `hcp:*` ontology
concepts. The locked Curavias prototype demands each copilot be
**predictive, prescriptive, and coordinated** — surfacing not just a forecast
breach and its drivers, but ranked response levers with quantified expected
impact, a human-approved action, and a live cross-role golden thread (for
example, OOA's *"Medicine A 102% -> 94%"*).

Sprint 26 (issue #335,
[design spec](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md))
closes this gap by extending the descriptive `DC-INSIGHT-v1` grounding contract
to a full 5-beat tuple — SIGNAL -> UNDERSTANDING -> RECOMMENDATION -> ACTION ->
COORDINATION, plus PROVENANCE — and by introducing a runtime decision store for
the Decision and Coordination tiers. Slice 1
([plan](../superpowers/plans/2026-07-24-sprint-26-slice1-ooa-dca-plan.md))
proves the pattern end-to-end for the OOA -> DCA role pair before fanning out
to the remaining four roles.

This extension must preserve the regulated-platform guardrails already
recorded in [ADR-0016](0016-no-phi-in-mvp-demo-scope.md) (synthetic data only,
no PHI) and [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md)
(human-in-the-loop release gates for agent-driven actions): a prescriptive
layer must not become an autonomous-apply layer, and it must not introduce any
new patient-identifiable data.

## Decision

Adopt the following architecture for the descriptive -> prescriptive ontology
extension and its runtime decision store.

1. **Adopt the `DC-INSIGHT-v1` 5-beat contract** as the ontology/insight
   extension. Every grounded copilot answer is a `signal` / `understanding` /
   `recommendation` / `action` / `coordination` tuple plus `provenance`, not a
   free-form sentence (schema:
   `data/synthetic/schema/dc-insight-v1.schema.json`).
2. **Split responsibility across the existing Fabric-to-Foundry seam.** The
   read-only **Fabric Data Agent** (`da_hospital_capacity`) emits only the
   descriptive `signal`, `understanding`, and `provenance` beats — it stays a
   grounding tool per
   [ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md) and does not
   assemble prescriptive content. The **agent-host** (per
   [ADR-0008](0008-agent-runtime-pattern-scope-and-selection.md)) assembles the
   `recommendation`, `action`, and `coordination` beats at runtime for each
   copilot, consuming the Data Agent's descriptive beats as grounding input.
3. **A deterministic impact function grounds `expected_impact`.** Every
   ranked lever's `expected_impact` (delta beds / delta %) is computed by a
   pure, unit-tested `compute_expected_impact` tool over the governed semantic
   model — **never an LLM estimate** — so the number behind a recommendation is
   auditable and reproducible.
4. **Advisory + HITL via `approved-to-apply`.** An action may be `PROPOSED`
   autonomously by a copilot, but is only `APPLIED` after a human posts the
   `approved-to-apply` confirmation on the governing PR/issue/comment thread,
   per the platform's standing confirmation rule
   ([AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete)).
   The agent refuses to self-approve and refuses a bot-identity approver.
5. **A runtime decision store, agent-host-mediated.** Two new Cosmos
   containers — `proposed_actions` (partition key `/plan_id`) and `plans`
   (partition key `/episode_key`) — are added to the existing CSA Cosmos
   account (`cosmos-csa-ihzhhpf-sit`). Per
   [ADR-0029](0029-agent-host-cosmos-reachability.md), reads/writes are
   **mediated by the agent-host**, not called directly by OOA/DCA; the copilot
   agents therefore keep their `write` side-effect ceiling and require **no**
   `cosmos-mcp` grant of their own.

## Consequences

### Positive

- Formally defines `FR-FC-007` (Fabric Data Agent's descriptive `DC-INSIGHT-v1`
  beats) and `FR-DEC-001` to `FR-DEC-003` (Decision + Coordination beat
  assembly, advisory HITL action, and cross-role coordination) in
  [`docs/PRD.md`](../PRD.md), closing the governance gap between the
  already-implemented Slice-1 code and the requirement catalogue.
- Preserves every standing guardrail: advisory-only, HITL-gated apply,
  synthetic/no-PHI, and the Fabric Data Agent's read-only grounding-tool
  posture.
- Reuses proven seams (Fabric-to-Foundry grounding, agent-host Cosmos
  mediation) instead of introducing a new integration pattern.
- Keeps the numbers behind a recommendation defensible: `expected_impact` is a
  deterministic, testable computation, not an LLM guess.

### Negative

- Introduces two new Cosmos containers that must be provisioned, backed up,
  and monitored under the existing CSA account's operational posture.
- Splitting descriptive vs. prescriptive assembly across two runtimes (Fabric
  Data Agent vs. agent-host) adds a coordination seam that must be kept in
  sync as the contract evolves.

### Neutral

- Scope is **Slice 1 only** (OOA -> DCA); the remaining four role pairs
  (bmca, orsa, sba, csa) are deferred to fan-out slices per the design spec
  §5, reusing the same lever catalog, impact tool, and Cosmos containers.
- Does not alter the Foresight tier (`hcp:Forecast/Driver/Signal`,
  `gold.fact_occupancy_forecast` et al.) delivered in Sprint 26 WS-A; this ADR
  covers only the Decision and Coordination tiers layered on top of it.

## Alternatives considered

| Alternative | Why rejected |
| ----------- | ------------ |
| LLM-estimated `expected_impact` | Not grounded or auditable; a hallucinated bed-delta number undermines trust in a regulated capacity-management context. |
| Auto-apply a recommended action without human approval | Violates the platform's standing advisory-only + HITL posture ([ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md)); risks an unreviewed operational change reaching a live ward. |
| Grant OOA/DCA a direct `cosmos-mcp` tool binding | Requires a CODEOWNERS-approved `.github/copilot/mcp.json` change and raises each agent's effective side-effect ceiling beyond `write`, when agent-host-mediated access already satisfies the requirement without a new grant. |

## Links

- [Sprint 26 decision-ontology design spec](../superpowers/specs/2026-07-23-sprint-26-decision-ontology-actionable-insight-design.md)
- [Sprint 26 Slice 1 (OOA -> DCA) implementation plan](../superpowers/plans/2026-07-24-sprint-26-slice1-ooa-dca-plan.md)
- [ADR-0033: Fabric Data Agent as Foundry grounding tool](0033-fabric-data-agent-as-foundry-grounding-tool.md)
- [ADR-0008: agent runtime pattern scope and selection](0008-agent-runtime-pattern-scope-and-selection.md)
- [ADR-0029: agent-host Cosmos reachability](0029-agent-host-cosmos-reachability.md)
- [ADR-0016: no PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
- [ADR-0007: MVP agent runtime and HITL release gates](0007-mvp-agent-runtime-and-hitl-release-gates.md)
