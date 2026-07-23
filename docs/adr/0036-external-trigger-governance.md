# ADR-0036: External Trigger Governance

| Field | Value |
| ----- | ----- |
| **Status** | Accepted |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | #247 |

## Context

Sprint 21 introduces trusted external signals so Swiss public-authority hazard
feeds can inform the Crisis Scenario Agent (CSA) without weakening existing
human-in-the-loop controls. Candidate sources include public Swiss authority
feeds and synthetic fixtures only; no PHI or personal data is ingested. The
normalized data contract is `DC-EXT-SIGNAL-v1`, a CAP-Suisse-aligned envelope
for hazard type, severity, certainty, urgency, status, onset, and provenance.

The design must preserve the regulated-platform guardrails already recorded in
[ADR-0013](0013-temporary-us-region-demo-scope.md),
[ADR-0016](0016-no-phi-in-mvp-demo-scope.md),
[ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md),
[ADR-0024](0024-csa-tier-classifier-rules.md), and
[ADR-0026](0026-evidence-readiness-measure-ownership.md). External signals may
raise situational awareness and propose an advisory CSA handoff, but they must
not autonomously mutate hospital capacity, roster, bed, or patient-flow state.

## Decision

Adopt the following governance policy for external hazard-trigger signals:

* Trust-tier `A` public-authority signals may be auto-evaluated against trigger
  rules.
* Trust-tier `B` and `C` signals are human-curated only and do not auto-trigger
  CSA handoffs.
* Triggering uses a dual path: Fabric Activator/Reflex when GA-gated under
  [ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md), and a
  scheduled poller bridge until that GA gate is satisfied. Both paths converge
  on the same signal-triage contract.
* `Test`, `Exercise`, and `System` records are quarantined and never trigger CSA.
  Only `Actual` records can proceed to threshold evaluation.
* Every ingested signal records source licence and attribution in
  `provenance.licence`, with raw-payload lineage in `provenance.rawHash` and
  connector evidence in `provenance.connectorVersion` and `provenance.ingestedAt`.
* External triggers remain advisory and HITL-preserving. The automatic action is
  limited to opening a CSA proposal or issue for human review; CSA Run remains
  gated by the existing `approved-to-apply` control.
* The demo scope remains non-PHI and synthetic where repository fixtures are
  used. `demo-westus2` residency is permitted only under
  [ADR-0013](0013-temporary-us-region-demo-scope.md) and
  [ADR-0016](0016-no-phi-in-mvp-demo-scope.md).
* Forecast-overlay uplift is incremental over the seasonal baseline already in
  `gold.forecast_output`; multiple qualifying signals combine multiplicatively
  under the documented clamp, and every adjusted row must retain signal
  attribution and provenance.

## Consequences

### Positive

* Adds a governed, auditable path from trusted public hazard signals to CSA
  advisory preparation.
* Keeps trigger semantics deterministic: trust tier, status, severity,
  certainty, and threshold checks are inspectable before any CSA handoff.
* Preserves human authority over operational decisions and CSA execution.
* Makes licence, attribution, connector version, ingestion time, and raw-payload
  hash mandatory evidence for every ingested signal and forecast adjustment.
* Supports future Activator/Reflex adoption without redesign once GA gates are
  satisfied.

### Negative

* Trust-tier `B` and `C` sources require manual curation before they can affect
  operational workflows.
* Dual-path operation adds temporary bridge complexity until Activator/Reflex is
  GA-approved for the relevant environment.
* False-negative risk remains when a public-authority signal is below threshold;
  these events must still be logged as evaluated without trigger.

### Neutral

* This ADR does not approve PHI ingestion, external partner platform access, or
  autonomous changes to operational capacity state.
* Existing CSA tier classification in
  [ADR-0024](0024-csa-tier-classifier-rules.md) remains the authority for Lage
  tier interpretation.
* Existing evidence ownership in
  [ADR-0026](0026-evidence-readiness-measure-ownership.md) remains unchanged.

## Alternatives considered

| Alternative | Why rejected |
| ----------- | ------------ |
| Auto-trigger CSA from any external source | Would bypass trust-tier governance and increase false-trigger risk. |
| Wait for Fabric Activator/Reflex GA before implementing the contract | Would delay offline-testable normalization, provenance, and advisory workflows that can be safely built now. |
| Treat external signals as direct operational commands | Violates the platform's advisory-only and HITL model. |
| Ingest broader non-authority or personal data feeds | Outside Sprint 21 scope and conflicts with the no-PHI demo boundary. |

## Links

* [Sprint 21 trusted external signals design](../superpowers/specs/2026-07-17-sprint-21-trusted-external-signals-fabric-design.md)
* [DC-EXT-SIGNAL-v1 JSON Schema](../../data/synthetic/schema/dc-ext-signal-v1.schema.json)
* [ADR-0013: Temporary US Region Demo Scope](0013-temporary-us-region-demo-scope.md)
* [ADR-0014: Fabric IQ Ontology as target semantic backbone](0014-fabric-iq-ontology-target-backbone-ga-gated.md)
* [ADR-0016: No PHI in MVP Demo Scope](0016-no-phi-in-mvp-demo-scope.md)
* [ADR-0024: CSA Tier Classifier Rules](0024-csa-tier-classifier-rules.md)
* [ADR-0026: Evidence Readiness Measure Ownership](0026-evidence-readiness-measure-ownership.md)
* Issue #247

## Addendum: Provider-Plugin Architecture Decisions (Sprint 21 Refactor)

The following decisions extend this ADR to record the provider-plugin
architecture refactor approved in the Sprint 21 signal-provider refactor
workstream. The original governance decisions above remain in effect unchanged.
Cross-reference: [Sprint 21 signal-provider plugin architecture design](../superpowers/specs/2026-07-23-sprint-21-signal-provider-plugin-architecture-design.md).

### Decision A: Manifest-driven provider-plugin architecture

External signal sources are onboarded as manifest-driven provider plugins.
Each plugin declares its binding configuration in a versioned manifest file.
Bindings are swappable at deploy time:

* `LiveBinding` - real API adapter for confirmed-ready channels (SED, Alertswiss).
* `SimulatorBinding` - deterministic fixture replay for channels without a confirmed API.
* `InternalBinding` - derived from platform gold tables (see Decision D).

A live-to-simulated fallback is supported: when a LiveBinding call fails, the
runner automatically promotes the SimulatorBinding for that channel and records
`provenance.fellBackFrom = "live"` on every produced record. A schema-invalid
manifest fails CI and is excluded from the runtime catalogue (fail-closed,
NFR-EXT-PLG-002). Live bindings are always mocked in CI; no external network
calls occur in GitHub Actions (NFR-EXT-PLG-001).

### Decision B: 3-state trust-badge data contract

A data-driven trust badge flows end-to-end through the platform using three
possible states (`live`, `simulated`, `internal`) carried in `provenance.activeBinding`
on each `DC-EXT-SIGNAL-v1` record. The propagation chain is:

`provenance.activeBinding` -> `ext_dim_source.dataMode` -> semantic-model measures -> board cards.

The `ext_dim_source` dimension table exposes `dataMode`, `trustTier`,
`lastLiveAt`, and `fellBackFrom` columns. Semantic-model measures read these
columns to drive per-channel trust badges on CSA and OCA board cards (FR-EXT-019).
This contract is defined in `DC-EXT-SIGNAL-v1` and the `ext_dim_source` badge
columns documented in `docs/DATA.md`.

### Decision C: Ingestion and simulation hosted on Azure Container Apps

The provider-runner service (ingestion + simulation) is hosted on Azure Container
Apps, NOT in GitHub Actions. Actions is CI-only. The Container Apps service
publishes normalized `DC-EXT-SIGNAL-v1` records to Event Hub/Eventstream.
This preserves the CI boundary rule (NFR-EXT-PLG-001) and keeps long-running
polling and simulation workloads out of short-lived workflow runners.

### Decision D: Internal signal channels are first-class providers

Internal signal channels derived from platform gold tables are supported as
first-class provider plugins with `channelKind = internal`. They use an
`InternalBinding` that queries gold Delta tables directly rather than calling
an external API. Internal channels participate in the same manifest registry,
trust-badge pipeline, and deduplication logic as external channels, but are
classified separately (`provenance.channelKind = "internal"`).
