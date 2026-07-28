# ADR-0053: Signal Channel Lifecycle Governance

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-27 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | #454 |

## Context

Sprint 31 and Sprint 32 close the data-quality loop: the Data Quality Agent
(DQA) detects a `DC-DQ-GAP-v1` gap with `newSourceNeeded: true`, and the Signal
Agent (SGA) onboards the missing channel only when that demand signal exists.
SGA intake therefore has a hard dependency on the Sprint 31 `DC-DQ-GAP-v1` seam;
it does not discover or activate speculative channels without an accountable data
quality gap.

The flagship worked example is a certification-register lane: an official or
curated register is normalised to
[`DC-REF-CERTIFICATION-v1`](../../data/synthetic/schema/dc-ref-certification-v1.schema.json),
bound to the Credential/Competency ontology, evaluated through a sandbox channel
readiness scorecard, approved through a human-in-the-loop activation gate, and
then used to enrich the skills baseline by pseudonymised `WID-*` work-ID. This
Sprint 32 slice uses a curated sample feed only; live web-search discovery and
live registry availability are deferred.

## Decision

Adopt an explicit signal-channel lifecycle owned by the new `signal-agent`:
**discover -> classify -> adapter -> contract -> ontology-bind -> sandbox-test ->
HITL-activate -> monitor -> retire**. The runtime `signal-triage-agent` remains a
consumer of activated signals; it does not own discovery, onboarding, contract
registration, ontology binding, or lifecycle governance.

SGA classifies every candidate channel by domain family, signal type, data class,
and trust tier:

* **Trust A** - official or provider-owned source with stable provenance and a
  governed licence.
* **Trust B** - recognised institutional source requiring additional curation or
  reconciliation before use.
* **Trust C** - exploratory, sample, simulated, or manually curated source that
  can inform sandbox evaluation but cannot activate without explicit approval.

The adapter catalogue is bounded to these patterns: CAP/OASIS, FDSN, STAC/OGC,
DATEX II, CKAN/opendata.swiss, FHIR registry, webhook/Event-Grid, REST pull, and
file drop. Adapter selection is advisory until the data contract, ontology
binding, sandbox scorecard, and approval record are complete.

Activation is human-in-the-loop. The data owner and compliance/DPO jointly
approve channel activation and ontology changes by recording `approved-to-apply`
per [AGENTS.md §4](../../AGENTS.md#4-confirmation-rule-for-deploy--delete). SGA
is advisory-only and never activates autonomously, self-approves, or accepts a bot
approver.

Certification and skills data are staff-PII under nDSG. The lane uses only
pseudonymised `WID-*` work-IDs, never names or AHV numbers, and never treats
staff-PII as non-PHI-free operational data. This preserves the no-PHI demo scope
in [ADR-0016](0016-no-phi-in-mvp-demo-scope.md): patient PHI remains forbidden,
while staff-PII remains regulated and explicitly governed.

## Consequences

### Positive

* Channel onboarding becomes demand-driven, governed, and auditable: every intake
  starts from a DQA gap, carries provenance, and records the approval trail.
* The certification-register example proves the closed loop from `DC-DQ-GAP-v1`
  to `DC-REF-CERTIFICATION-v1`, ontology binding, sandbox scoring, HITL
  activation, and skills-baseline enrichment.
* The lifecycle reuses deterministic modules under `data-platform/signals/` for
  gap registration, credential-to-competency resolution, and sandbox scoring
  instead of relying on model-only judgement.
* Trust tier, licence, classification, pseudonymisation, and provenance become
  first-class evidence for every channel.

### Negative

* Registry availability and licensing remain open questions for live
  certification sources; the Sprint 32 implementation therefore proves a curated
  sample feed first.
* Live web-search discovery is deferred. Future search results are candidate
  identification only and must remain untrusted until classified, sandboxed, and
  approved.
* GA-gating can delay live activation where Fabric, Foundry, or source-system
  capabilities are not Swiss-region GA.

### Neutral

* This ADR does not change the trunk-based workflow in
  [ADR-0038](0038-trunk-based-parallel-sprint-workflow.md).
* This ADR extends, but does not replace, the human approval doctrine in
  [ADR-0007](0007-mvp-agent-runtime-and-hitl-release-gates.md).
* The runtime signal triage boundary from the Sprint 21 signal lane remains
  intact: triage acts on activated signals; SGA governs channel onboarding.

## Alternatives considered

| Alternative | Why rejected |
| ----------- | ------------ |
| Let `signal-triage-agent` own onboarding | Rejected because triage consumes activated signals at runtime; discovery, contracts, ontology binding, and lifecycle governance are a separate meta-agent responsibility. |
| Onboard channels from web search directly | Rejected for Sprint 32 because search results are untrusted candidate hints, not authoritative feeds; live discovery is deferred behind HITL and sandbox gates. |
| Treat certification data as non-PHI/no-risk | Rejected because staff certification data is staff-PII under nDSG even when it is not patient PHI. |
| Activate after a passing scorecard only | Rejected because schema/provenance quality is necessary but not sufficient; data-owner and compliance/DPO approval is mandatory. |

## Links

* [Sprint 31-32 SGA/DQA design](../superpowers/specs/2026-07-27-sprint-31-32-signal-and-data-quality-agents-design.md)
* [ADR-0007: MVP agent runtime and HITL release gates](0007-mvp-agent-runtime-and-hitl-release-gates.md)
* [ADR-0016: No PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
* [ADR-0038: Trunk-based parallel sprint workflow](0038-trunk-based-parallel-sprint-workflow.md)
* [`DC-REF-CERTIFICATION-v1` schema](../../data/synthetic/schema/dc-ref-certification-v1.schema.json)
* Issue #454
