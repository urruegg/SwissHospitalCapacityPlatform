# ADR-0052: App context envelope + per-agent threads + simulated per-user RLS

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-26 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Related** | [Sprint 29 design](../superpowers/specs/2026-07-26-sprint-29-foundry-iq-context-architecture-design.md), [Sprint 29 plan](../superpowers/plans/2026-07-26-sprint-29-foundry-iq-context-architecture.md), [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), [ADR-0032](0032-foundry-control-plane-eastus2.md), [ADR-0033](0033-fabric-data-agent-as-foundry-grounding-tool.md), [ADR-0044](0044-retire-public-website.md), [issue #399](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/399) |

## Context

Sprint 29 implements the Foundry IQ context architecture described by the
approved design v1.1 and governed by issue #399. Before this decision, the app's
three context tiers were inconsistent:

1. User context had no single per-request object that joined claims, active role,
   hospital scope, data source, target agent, and observation window.
2. Agent context used a shared chat turn list, so conversation state could bleed
   across board-agents.
3. Grounding context depended on a hard-coded default board and had no simulated
   per-user data scope at the app boundary.

The demo remains a westus2, synthetic-data showcase with no PHI, per ADR-0013
and ADR-0016. Sprint 29 therefore needed an auditable context contract that
keeps the live SIT path ready without provisioning new infrastructure during
this demo slice.

## Decision

Adopt **Approach A: app-side context architecture, endpoint-ready**, instead of
Approach B full live provisioning for this sprint.

1. Carry a single `ContextEnvelope`, built from signed-in claims and the active
   role lens, on every IQ read and agent turn.
2. Scope conversations per `(userOid × agent)`, giving each board-agent its own
   thread and resetting cleanly on sign-out.
3. Select the default board by the user's first role-eligible board, not by a
   hard-coded board id.
4. Propagate the envelope through the single IQ ingress as scoped headers and
   guard envelope-less calls before they can reach downstream grounding.
5. Add a config-gated `(user, agent) → threadId` Foundry thread map that can be
   seeded from the envelope.
6. Establish the OBO / simulated-RLS contract: user-triggered calls use **OBO**
   while app identity is reserved for autonomous jobs, and the Fabric semantic
   model enforces **RLS** by `hospitalScope`. This sprint mirrors that app-side
   through `applyRlsScope`, with live validation in SIT.

All live seams are config-gated so the westus2 simulated demo lifts to live SIT
with no code edits: config, not code.

## Consequences

Positive consequences:

* The user, agent, and grounding tiers are consistent by construction.
* Context and scope are auditable from one envelope per request.
* The demo remains safe for westus2 and synthetic data with no PHI.
* No new infrastructure provisioning is required in this sprint.
* The implementation is region-agnostic and can lift from simulated westus2 to
  live SIT by configuration.

Negative consequences and follow-up:

* OBO, Fabric semantic-model RLS, and Foundry thread persistence are simulated
  now.
* A SIT live-wiring follow-up for Approach B must:
  1. Wire `setContextEnvelope()` and the thread map into the send path.
  2. Enable `VITE_FOUNDRY_THREADS_ENABLED` and `VITE_GOLDEN_SOURCE_URL` against
     real endpoints.
  3. Validate live RLS and OBO.
* The thread map is not consumed in the send path yet.

## Alternatives considered

Approach B, full live integration, was rejected for this sprint. It requires
infra provisioning for Foundry threads, Fabric RLS, and OBO app-registration
wiring, which is outside the current westus2 synthetic-demo scope captured by
ADR-0013 and ADR-0016. It is also higher risk for the Sprint 29 delivery window.

Approach A is a strict subset of Approach B: it fixes the app-side contracts and
keeps every live seam config-gated so the follow-up can enable real endpoints
without code changes.
