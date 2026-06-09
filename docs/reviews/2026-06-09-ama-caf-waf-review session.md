# AMA CAF/WAF Architecture Review Session

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-09 |
| **Author** | GitHub Copilot (CAF/WAF structured review) |
| **Status** | Reviewed |
| **Previous Version** | N/A |
| **Review Scope** | Azure CAF + Azure Well-Architected Framework + Zero Trust + Swiss public sector compliance |

## 1. Executive Summary

Overall maturity assessment: **Moderate (3/5)**.

The repository shows strong intent and directional alignment on governance-first delivery, Zero Trust controls, Swiss data-residency posture, and auditable HITL controls. The main maturity gap is **evidence completeness versus architecture intent**: many controls are documented but still marked as operational tasks or partial implementation.

### Key risks

1. Legal/regulatory fragmentation risk (federal vs cantonal applicability) is acknowledged but not yet operationalized in a canton-specific control annex.
2. Reliability strategy remains primarily single-region baseline with constrained failover for PHI and no fully defined multiregion DR target state.
3. Policy-as-code and control automation are not fully evidenced for all CH controls and release gates.
4. Data governance and DSR operations are defined at baseline level but not fully implemented as executable workflows.
5. Architecture pattern drift risk exists between application-hosted agent runtime choices and Foundry-hosted baseline patterns used as references.

### Top 5 recommendations

1. **High**: Create canton-specific legal applicability matrix and map to CH-C01..CH-C10 controls with named owners and evidence artifacts.
2. **High**: Define and validate reliability target state (RTO/RPO, zone redundancy, failover boundaries by data class, DR runbooks).
3. **High**: Implement policy-as-code enforcement for residency, deployment-type restrictions, and PHI transfer gates in CI/CD.
4. **Medium**: Formalize Azure landing zone governance evidence (management group hierarchy, policy assignments, RBAC boundaries) per CAF landing-zone design areas.
5. **Medium**: Add architecture decision note clarifying where Foundry baseline is adopted, adapted, or intentionally not used (to prevent pattern inconsistency).

## 2. Context Overview

### Inputs reviewed

1. AMA review output (cantonal perspective): `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`.
2. AMA session-derived architecture challenger source: `docs/reviews/raw/AGENT_SOLUTION_DESIGN_REVIEW.md`.
3. Current architecture/governance baseline:
   - `docs/PRD.md`
   - `docs/SD.md`
   - `docs/ARCHITECTURE.md`
   - `docs/SECURITY.md`
   - `docs/COMPLIANCE.md`
   - `docs/AI.md`
   - `docs/INFRASTRUCTURE.md`
   - `docs/ALM_PLAN.md`
   - `docs/TEST.md`
   - `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`
4. Azure Architecture Center references:
   - Dynamic AI Agents at Scale pattern (Microsoft Learn)
   - Baseline Microsoft Foundry Chat reference architecture (Microsoft Learn)

### Assumptions

1. This review uses repository artifacts as the implementation truth source.
2. When artifacts state "open", "partial", or "not yet operationalized", status is treated as **Requires validation** for architecture-governance closure.
3. No evidence was found in scope for finalized canton-by-canton legal annexes, completed DSR operations, or production DR game-day output.

## 3. Key Findings from Review Session

### 3.1 Key decisions extracted

1. Governance-first, Git-first operating model with explicit approval gates and evidence contract is established.
   - Evidence: `docs/ALM_PLAN.md`, `docs/TEST.md`, `AGENTS.md`.
2. PHI inference constrained to Swiss regions and approved deployment modes; Global/Data Zone/Developer disallowed for PHI-sensitive use.
   - Evidence: `docs/ARCHITECTURE.md` (`AR-D-003`, `AR-D-004`), `docs/AI.md`.
3. HITL controls are formalized as release-gating taxonomy (HITL-01..HITL-05).
   - Evidence: `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md`, `docs/TEST.md`.

### 3.2 Assumptions extracted

1. Single-provider deployment boundary is the current operating architecture assumption.
   - Evidence: `docs/PRD.md` (`FR-OM-001`, `FR-OM-002`), `docs/ARCHITECTURE.md`.
2. Architecture is designed as compliance-oriented baseline, not compliance-complete production proof.
   - Evidence: `docs/COMPLIANCE.md` gap statuses; `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`.

### 3.3 Open issues extracted

1. Canton-specific legal applicability mapping remains open.
   - Evidence: `docs/COMPLIANCE.md` (out-of-scope statement), `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`.
2. Reliability and DR details remain open in architecture decisions.
   - Evidence: `docs/ARCHITECTURE.md` (open-for-review items).
3. DSR operating model and privacy incident timing matrix remain implementation tasks.
   - Evidence: `docs/COMPLIANCE.md`, `docs/SECURITY.md` residual gaps.

### 3.4 Risks and conflicts extracted

1. Governance-vs-implementation abstraction mismatch was explicitly highlighted in AMA review.
   - Evidence: `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`.
2. Runtime pattern tension exists between:
   - Repo baseline: application-hosted agent runtime (`docs/AI.md`)
   - External reference: Foundry Agent Service baseline (Microsoft Learn Foundry architecture)
   - Status: Requires validation of intended target-state by workload class.

## 4. Deviation Analysis

### 4.1 CAF alignment/deviation

| CAF area | Best-practice expectation | Current state | Deviation status | Evidence |
| ----- | ----- | ----- | ----- | ----- |
| Landing zone governance | Explicit management group hierarchy, policy and RBAC at scale | Domain modules and env parameters exist; MG hierarchy details not explicit in reviewed docs | Partial alignment | `docs/INFRASTRUCTURE.md`, `infra/main.bicep`, `docs/ARCHITECTURE.md` |
| Platform operating model | Clear ownership, controls, promotion model | Strong Git-first ALM with approval gates and PR evidence contract | Aligned | `docs/ALM_PLAN.md`, `docs/TEST.md`, `AGENTS.md` |
| Security baseline at platform layer | Zero Trust + policy-as-code + identity-first | Well documented baseline; execution evidence still partial in several controls | Partial alignment | `docs/SECURITY.md`, `docs/COMPLIANCE.md` |
| Standardization and reusable patterns | Consistent architecture decisions and templates | ADR set and AR-D decisions are consistent; runtime reference pattern selection needs explicit scope guard | Partial alignment | `docs/ARCHITECTURE.md`, `docs/AI.md`, `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md` |

### 4.2 WAF alignment/deviation

| WAF pillar | Best-practice expectation | Current state | Deviation status | Evidence |
| ----- | ----- | ----- | ----- | ----- |
| Reliability | Zone redundancy, DR design, tested recovery | Reliability intent present; open decisions on failover/DR and PHI runbook gating remain | Partial alignment | `docs/ARCHITECTURE.md`, `docs/AI.md`, Microsoft Learn Foundry baseline (Reliability section) |
| Security | Identity perimeter + network isolation + private endpoints + auditability | Strong Zero Trust design intent and controls; some operational controls are still open | Partial alignment | `docs/SECURITY.md`, `docs/COMPLIANCE.md` |
| Cost Optimization | Cost governance, token/telemetry optimization, right-sizing | Initial sizing and metrics baseline defined; no full cost control evidence loop shown | Requires validation | `docs/AI.md`, `docs/BVA.md`, Microsoft Learn Dynamic Agents at Scale (Cost optimization) |
| Operational Excellence | CI/CD gates, runbooks, measurable operational controls | Strong ALM/testing artifacts and release gates; incident/DSR/privacy operations partially open | Partial alignment | `docs/ALM_PLAN.md`, `docs/TEST.md`, `docs/SECURITY.md`, `docs/COMPLIANCE.md` |
| Performance Efficiency | SLOs, scaling strategy, cache/queue split, load validation | Clear baseline targets and sizing assumptions, but explicitly provisional and pending SIT validation | Partial alignment | `docs/SD.md`, `docs/AI.md`, `docs/ARCHITECTURE.md` |

### 4.3 Zero Trust alignment/deviation

1. Aligned: explicit verify/least-privilege/assume-breach model and managed identity-first pattern.
   - Evidence: `docs/SECURITY.md`.
2. Aligned: PHI transfer default-deny and Swiss-region restrictions.
   - Evidence: `docs/AI.md`, `docs/ARCHITECTURE.md`.
3. Requires validation: full policy enforcement telemetry proving control effectiveness in PROD.
   - Evidence gap: no consolidated control effectiveness report artifact in reviewed scope.

## 5. New and Emerging Requirements

### 5.1 Newly surfaced requirements (from AMA and benchmark comparison)

1. Canton-specific legal applicability annex with control delta per canton.
2. Formal reliability profile by data class (including whether PHI failover is ever permitted and under which legal gate).
3. Architecture pattern decision matrix for agent runtime modes:
   - application-hosted agents
   - Foundry Agent Service prompt/hosted agents
   - hybrid model
4. Evidence automation for CH controls into repeatable release packs.
5. Formal control for architecture drift detection between ADRs and deployed IaC.

### 5.2 Implicit requirements not formally complete

1. Explicit subscription/management-group policy assignment traceability (CAF platform governance depth).
2. DR game-day and restore proof for memory/audit stores (especially Cosmos DB/Storage dependent patterns).
3. Production observability acceptance criteria for AI safety and HITL override patterns.

## 6. Risk Assessment

| Category | Risk | Impact | Likelihood | Mitigation recommendation | Evidence |
| ----- | ----- | ----- | ----- | ----- | ----- |
| Compliance/Regulatory | Federal baseline used without canton-specific legal operational mapping | High | High | Build canton annex, legal sign-off gate, control-to-law traceability update | `docs/COMPLIANCE.md`, `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md` |
| Technical | Reliability strategy incomplete for multiregion/DR under PHI constraints | High | Medium | Define RTO/RPO by domain, DR runbooks, backup/restore tests, failover policy gates | `docs/ARCHITECTURE.md`, Microsoft Learn Foundry baseline (DR guidance) |
| Technical | Runtime architecture drift (self-hosted vs Foundry-hosted patterns) | Medium | Medium | Add ADR clarifying approved pattern per workload and maturity stage | `docs/AI.md`, Microsoft Learn Foundry baseline |
| Operational | Policy controls documented but not fully automated as-code | High | Medium | Add CI policy conformance checks and release evidence bundle automation | `docs/COMPLIANCE.md`, `docs/SECURITY.md`, `docs/TEST.md` |
| Operational | DSR and privacy-incident process incomplete | High | Medium | Implement DSR and privacy incident runbooks with owner/SLA and evidence cycle | `docs/COMPLIANCE.md`, `docs/SECURITY.md` |
| Technical/Cost | Token, cache, and telemetry costs may rise with agent scale | Medium | Medium | Add FinOps dashboards and policy thresholds for token and telemetry budgets | `docs/AI.md`, Microsoft Learn Dynamic Agents at Scale (Cost optimization) |

## 7. Architecture and Governance Alignment Review

### Well-aligned areas

1. Governance-first ALM model with explicit gates and traceability expectations.
2. Security and compliance principles embedded in architecture decisions (AR-D series).
3. HITL gate formalization and release-gating integration across SD/TEST/OPERATIONS.

### Misalignments

1. CAF landing-zone governance evidence is weaker than architecture intent (policy assignment and MG-level governance not explicitly evidenced in reviewed docs).
2. Reliability design intent exists, but production-level DR and failover controls are not yet validated.
3. Pattern consistency gap between external Foundry reference architecture and chosen application-hosted runtime baseline.

### Areas requiring validation

1. Management group / subscription strategy evidence and policy assignment coverage.
2. DR readiness and tested restore/failover outcomes.
3. Control effectiveness metrics (security, AI safety, HITL compliance) in SIT/PROD.

## 8. Compliance Evaluation (Swiss Public Sector Context)

### Data residency

1. Strong baseline: Swiss-region-only PHI inference with explicit deployment-type restrictions.
2. Gap: formalized transfer-risk/legal exception workflow evidence is partial.

### Regulatory fragmentation (federal vs cantonal)

1. AMA evidence correctly identifies that cantonal applicability cannot be assumed from federal baseline.
2. Current repository still treats canton-specific legal analysis as out of scope in baseline compliance document.
3. Conclusion: **Requires validation** before public-sector production approval.

### Security and Zero Trust posture

1. Strong design-level alignment with Zero Trust principles.
2. Open operationalization items remain (DSR, incident timing matrix, EPR conformance pack where applicable).

## 9. Recommendations and Next Steps

### High priority

1. Create `docs/compliance/cantonal-annex.md` with control deltas and legal ownership by canton.
2. Add reliability addendum with RTO/RPO, DR architecture choice, and test schedule.
3. Implement policy-as-code checks in CI for residency, deployment-type, diagnostics, and identity controls.

### Medium priority

1. Publish landing-zone governance evidence document (MG hierarchy, policy assignment matrix, RBAC scopes).
2. Add ADR clarifying when Foundry-hosted architecture patterns are in-scope versus self-hosted runtime.
3. Implement operations evidence automation for CH-C03, CH-C05, CH-C10 monthly reporting.

### Low priority

1. Extend cost governance with AI token budget thresholds and telemetry sampling policy.
2. Add periodic architecture conformance review against external reference patterns.

### Quick wins (0-30 days)

1. Document explicit “requires validation” register in architecture and compliance docs.
2. Add control-owner column for all open CH controls.
3. Add DR test evidence placeholder section in release checklist.

### Strategic changes (30-120 days)

1. Complete canton-specific compliance annex and legal sign-off workflow.
2. Implement full control evidence pipeline integrated into release gates.
3. Validate reliability and failover controls through SIT and controlled PROD drills.

## 10. Traceability Matrix

| Requirement | Control | Architecture Decision | Source | Status |
| ------------ | --------- | ---------------------- | -------- | -------- |
| `FR-GOV-001` auditable traceability | `CH-C03` traceability | `AR-D-007` HITL and audit persistence baseline | `docs/PRD.md`, `docs/COMPLIANCE.md`, `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md` | Partial (implementation evidence required) |
| `NFR-COMP-004` residency controls | `CH-C05` cross-border restrictions | `AR-D-003`, `AR-D-004` Swiss PHI constraints | `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/AI.md` | Partial (exception workflow requires validation) |
| `NFR-AI-001` advisory AI only | `CH-C10` AI oversight | HITL gate taxonomy | `docs/PRD.md`, `docs/SD.md`, `docs/TEST.md`, `docs/adr/0007-mvp-agent-runtime-and-hitl-release-gates.md` | Aligned (test evidence cadence required) |
| `FR-GOV-003` promotion governance | Security/compliance release evidence controls | Git-first gated promotion model | `docs/PRD.md`, `docs/ALM_PLAN.md`, `docs/TEST.md`, `docs/INFRASTRUCTURE.md` | Aligned |
| `NFR-SEC-001` least privilege | `CH-C02` privacy by design and access minimization | Identity-first architecture baseline | `docs/PRD.md`, `docs/SECURITY.md`, `docs/ARCHITECTURE.md` | Partial (operational recertification evidence required) |
| `NFR-REL-003` graceful degradation | Reliability control baseline | Open DR/failover decisions | `docs/PRD.md`, `docs/ARCHITECTURE.md`, Microsoft Learn Foundry baseline reliability guidance | Requires validation |
| `NFR-MAINT-002` Git-first delivery | Governance evidence controls | ALM gate model | `docs/PRD.md`, `docs/ALM_PLAN.md`, `docs/TEST.md` | Aligned |

## Evidence Notes

- When a finding is based on AMA synthesis rather than direct verbatim transcript, the source is the structured review artifact:
  - `docs/reviews/2026-06-08-ama-review-session-csa-cantonal-full.md`
- When architecture benchmark findings are from external references, the source is the Microsoft Learn architecture documentation listed in Context.
- Any item marked **Requires validation** indicates missing implementation evidence in reviewed artifacts, not an assumed non-compliance conclusion.
