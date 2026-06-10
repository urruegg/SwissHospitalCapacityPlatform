# Sprint 6 MVP Agent Readiness Baseline (OOA / DCA / BMCA)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot |
| **Status** | Ready |
| **Previous Version** | N/A |

## Purpose

Baseline the **MVP Phase 1 agent readiness** for the three mandatory Sprint 6
agents â€” Operations Orchestrator Agent (OOA), Discharge Coordination Agent
(DCA), and Bed Management Copilot Agent (BMCA) â€” with explicit interfaces, data
contracts, and IaC component mapping. This is the Phase 1 (#45) readiness
deliverable for
[`docs/sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md`\](../sprints/sprint-06-minimal-data-onboarding-and-capacity-specialty.md)
"MVP Agent Scope for Sprint 6".

## Scope Lock

MVP Phase 1 scope is **locked to OOA, DCA, BMCA only**. The optional agents
(Demand Forecasting Agent, Integration Workflow Agent, Data Quality and Semantics
Agent, Compliance and Safety Agent, Explainability and Audit Agent) are
**deferred to Phase 3** (#47) and are non-blocking for Phase 1 kickoff. This
readiness baseline must not introduce optional-agent implementation work.

## Baseline References

1. `docs/reviews/2026-06-09-agent-solution-design-review.md` (MVP agent solution design)
2. `docs/SD.md` (onboarding lanes + deterministic-vs-agentic classification)
3. `docs/ARCHITECTURE.md` (Sprint 6 onboarding and data-platform overlay)
4. `docs/DATA.md` (Sprint 6 onboarding contracts)
5. `data/synthetic/README.md` (synthesized SIT datasets and validation)

## Agent Scope and Interfaces

| Agent | Primary responsibility | Inputs | Outputs | Classification (FR-ONB-004) |
| ----- | ----- | ----- | ----- | ----- |
| OOA | Plan construction, routing, guardrail application, HITL approval routing | User intent, capacity onboarding context, agent tool results | Execution plan, advisory response, approval routing | Agentic (advisory, HITL-gated) |
| DCA | Identify discharge candidates and produce ranked, explained list | Onboarded patient-minimum + capacity context, discharge signals | Ranked discharge candidates with factors; submitted to OOA for approval | Agentic (advisory, HITL-gated) |
| BMCA | Conversational copilot for bed/flow status and recommendations | Live capacity state, onboarded specialty-capacity data, discharge signals, conversation context | Grounded advisory answers with citations and timestamps | Agentic (advisory, HITL-gated) |

All three agents are **advisory-only and human-in-the-loop**; no autonomous
closed-loop clinical actuation (`NFR-AI-001`). Deterministic onboarding
ingestion and contract validation are **services**, not agents, per the
classification criterion in [`docs/SD.md`](../SD.md).

## Data Contracts Consumed

| Agent | Onboarding contracts consumed | Source |
| ----- | ----- | ----- |
| OOA | `DC-ONB-CAPACITY-v1` (+ provider extensions) | `data/synthetic/datasets/*capacity*.json` (SIT) |
| DCA | `DC-ONB-PATIENT-v1`, `DC-ONB-CAPACITY-v1` | `data/synthetic/datasets/patient-minimum-onboarding.json`, capacity datasets (SIT) |
| BMCA | `DC-ONB-CAPACITY-v1` (+ provider extensions) | capacity datasets (SIT) |

The patient lane is consumed only in its minimized, pseudonymous form; the
synthesized-data gate enforces re-identification minimization before any agent
flow consumes it (`NFR-COMP-011`, `CH-C01`).

## Agent-to-IaC Component Mapping

The MVP flows bootstrap from the IaC-first data-platform module. Phase 1
provisions the data-platform onboarding container; remaining runtime resources
are scaffolded module flags in [`infra/main.bicep`](../../infra/main.bicep)
enabled per environment in later phases.

| Agent | Primary Azure service(s) | IaC component |
| ----- | ----- | ----- |
| OOA | Azure Container Apps (HTTP API) | `infra/modules/api-runtime`, `infra/modules/data-platform` (onboarding container) |
| DCA | Container Apps + Azure Machine Learning | `infra/modules/ai-ml-foundation`, `infra/modules/data-platform` |
| BMCA | Container Apps + Azure OpenAI | `infra/modules/ai-platform`, `infra/modules/data-platform` |
| Shared bootstrap | Storage `onboarding` container for synthesized SIT data | `infra/modules/data-platform/main.bicep` (`onboardingContainerName` output) |

All MVP agent services are deployable through the IaC-first pipeline
(`NFR-MAINT-005`); the data-platform module output `onboardingContainerName`
is the synthesized-data bootstrap path consumed by SIT flows.

## Human-in-the-Loop Gates

| Gate | Trigger | Approver | Path |
| ----- | ----- | ----- | ----- |
| HITL-01 | Patient-affecting workflow trigger (discharge coordination) | Clinician | DCA -> OOA -> Human |
| HITL-02 | Bed transfer / resource reprioritization recommendation | Operations lead | BMCA -> OOA -> Human |

These mirror the MVP agent solution design and remain mandatory for Phase 1.

## Readiness Evidence Checklist

- [x] MVP scope locked to OOA/DCA/BMCA; optional agents deferred to Phase 3.
- [x] Onboarding data contracts defined and validated for SIT
      (`data/synthetic/validate_datasets.py`).
- [x] Agent-to-IaC component mapping documented with data-platform bootstrap path.
- [x] Deterministic-vs-agentic classification applied to onboarding flows.
- [x] Advisory-only + HITL gates confirmed for all three agents.
- [ ] Agent golden-task packs (`agents/<name>/`) â€” deferred to agent build phase.

## Change Control

Any change to MVP agent scope or the IaC mapping bumps this document's version
per `.github/copilot-instructions.md` Â§9 and must keep MVP Phase 1 scope locked
to OOA/DCA/BMCA.

