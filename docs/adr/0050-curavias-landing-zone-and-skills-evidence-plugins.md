# ADR-0050: Curavias Landing Zone + Skills-Evidence Plugin Architecture + Hybrid Transport

| Field | Value |
| ----- | ----- |
| **Status** | Proposed |
| **Date** | 2026-07-23 |
| **Author** | Urs Rueegg |
| **Decision-makers** | @urruegg |
| **Related issue** | #255 |

> **Renumbered from ADR-0039 → ADR-0040 on 2026-07-24, then to ADR-0050 on 2026-07-26 (#378)** (number-collision resolution; see [ADR-0041](0041-adr-number-collision-resolution.md)).

## Context

Sprint 23 (#255, P1b) folds `dim_hospital` into the Curavias organisation spine
and adds the org/skills master-data domain as `gold.*` tables, extending the
semantic model, ontology, and Fabric IQ grounding. During the 2026-07-23
brainstorm four requirements arrived that the base plan (T1-T10) did not cover:

1. **MCAPS tenant restriction.** The MCAPS demo tenant cannot provision the
   sample users / workforce records in Microsoft Entra. The full synthetic
   Curavias master data (employees, skill assertions, org spine) therefore needs
   a **dedicated upload location** loaded **on demand** via a Data Pipeline
   (Bronze -> Silver -> Gold), rather than living in Entra.
2. **Skills-evidence sources as a plugin architecture.** Skills evidence must be
   gathered from external systems through a **plugin architecture** - real-API
   adapters where an API exists, **simulators** where none does - mirroring the
   Sprint 21 signal-provider pattern, each flagged **live-vs-simulated**.
3. **Mimic the key evidence systems.** No real system is in place yet; the
   platform mimics **SuccessFactors** (HRIS), an **LMS** (learning/cert store),
   and **Skills-Manager with Work-ID** (worker-owned skills passport) as
   simulated sources.
4. **Bed vs Ops demand split.** The semantic + ontology surface must express
   which skills are required on the **bed** side (Pflegepersonal / nursing) and
   on the **ops** side (doctors and specialised teams).

This design must preserve the regulated-platform guardrails already recorded in
[ADR-0013](0013-temporary-us-region-demo-scope.md),
[ADR-0016](0016-no-phi-in-mvp-demo-scope.md),
[ADR-0014](0014-fabric-iq-ontology-target-backbone-ga-gated.md), and the
Sprint 21 external-signal governance in
[ADR-0036](0036-external-trigger-governance.md). It refines the shared
master-data design of
[2026-07-19-curavias-shared-master-data-and-ontology-design.md](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md)
without reversing it: the earlier design assumed git-committed extracts, which
requirement #1 makes unworkable in the MCAPS tenant.

## Decision

Adopt the following architecture for the Curavias org/skills master-data domain.
These are the locked decisions D1-D6 from the Sprint 23 design.

* **D1 - Dedicated Azure landing zone (out-of-band upload), not git-committed
  extracts.** Synthetic extracts are uploaded to a landing zone and loaded on
  demand. Data validation moves from git-CI to the **pipeline silver gate**. The
  **generator stays git-owned** (`data/master-data/curavias-org-skills/`) for
  reproducibility; the generated extracts do not live in git.
* **D2 - Landing-zone surface = ADLS Gen2 container + OneLake shortcut,
  Bicep-provisioned.** Enterprise-realistic, decoupled from Fabric, uploadable
  via `az`/portal; the on-demand Fabric Data Pipeline reads it through a OneLake
  shortcut.
* **D3 - Skills-evidence plugin package mirrors Sprint 21**
  (`connectors/base_connector.py` + per-source adapters + `normalize.py` +
  `*_synth.py` + `tests/`). All four sources are **simulated now**; adapters are
  shaped so a real API can slot in without touching the ontology. The normalized
  contract is `DC-SKILL-EVIDENCE-v1`, carrying a **live-vs-simulated badge**
  (`sourceMode`) and a **trust tier** (`trustTier` A|B|C) per record.
* **D4 - Hybrid transport.** Batch extract drops to the ADLS landing zone for
  HRIS/LMS master data; an **Eventstream** lane covers only near-real-time
  skills events (credential expiry, consent grant/revoke, newly-confirmed
  assertions). Ingestion and simulation run as **Azure Container Apps**, publishing
  to Event Hub/Eventstream - never as GitHub workflows (Actions is CI-only).
* **D5 - Validation at the silver gate.** Because extracts are not in git, the
  `validate_master_data.py` logic (PK/FK, GLN mod-10, enum domains, load order)
  runs inside the pipeline against landed Bronze, quarantining bad rows in Silver.
* **D6 - Extend, don't replace.** The Step 1-4 ontology, schema, and connector
  design are reused verbatim. The atomic unit stays `fact_skill_assertion`; the
  two axes (proficiency 1-5, assurance L0-L4) and the GLN golden thread are
  unchanged; Gold stays deny-by-default.

Assurance derivation and consent remain governed: `self` evidence maps to L0 and
`employer_confirmed` to L1; the `worker_gln` promotion key and `consentScope` are
present only when Work-ID consent was granted, and Work-ID assertions are always
`self`-declared regardless of consent. The badge and trust tier travel through
Bronze/Silver and surface on `gold.fact_skill_assertion`; they are never invented
downstream.

## Consequences

### Positive

* Removes the hard dependency on Entra user provisioning in the MCAPS tenant; the
  synthetic workforce loads on demand from a governed landing zone.
* Reuses one proven pattern (Sprint 21 signal-provider plugin) for both signals
  and skills evidence, lowering cognitive load and review cost.
* Keeps the generator reproducible and git-owned while keeping bulk synthetic
  extracts out of git history.
* Makes live-vs-simulated status and trust tier first-class, auditable data that
  flows end-to-end to the semantic model and boards.
* Keeps long-running ingestion/simulation on Azure Container Apps, honouring the
  CI-boundary rule established in [ADR-0036](0036-external-trigger-governance.md).

### Negative

* Introduces a landing-zone + on-demand pipeline that must be provisioned and
  operated (Bicep, OneLake shortcut, silver gate) instead of a simple git commit.
* Validation moving to the silver gate means bad rows are detected at pipeline
  run time rather than at PR time; quarantine handling must be observable.
* Dual transport (batch + Eventstream) adds a second path to operate and test.

### Neutral

* This ADR does not approve PHI or real personal-data ingestion; all sources are
  synthetic and no-PHI per [ADR-0016](0016-no-phi-in-mvp-demo-scope.md).
* `demo-westus2` residency remains permitted only under
  [ADR-0013](0013-temporary-us-region-demo-scope.md).
* The ontology, proficiency/assurance axes, and GLN golden thread from the
  Step 1-4 idea pack remain the authority; this ADR does not alter them.

## Alternatives considered

| Alternative | Why rejected |
| ----------- | ------------ |
| Provision synthetic users in Entra | Requirement #1: the MCAPS tenant cannot provision them. |
| Keep git-committed CSV extracts (shared 2026-07-19 design) | Does not scale to full workforce extracts and cannot represent on-demand HRIS/LMS export cadence; validation belongs at the pipeline gate. |
| Single transport (batch only, or Eventstream only) | Batch-only cannot express near-real-time consent/expiry events; Eventstream-only misdescribes periodic HRIS/LMS master-data exports. |
| Bespoke per-source ingestion code | Rejected in favour of reusing the Sprint 21 plugin pattern (D3) for consistency and testability. |
| Run ingestion/simulation in GitHub Actions | Violates the standing CI-boundary rule; long-running polling/simulation belong on Container Apps. |

## Links

* [Sprint 23 org-skills refactor design](../superpowers/specs/2026-07-23-sprint-23-org-skills-refactor-design.md)
* [Sprint 23 implementation plan](../superpowers/plans/2026-07-23-sprint-23-org-skills-refactor-plan.md)
* [Sprint 23 sprint scope](../sprints/sprint-23-curavias-org-spine-and-skills-ontology.md)
* [Shared master-data + ontology design (2026-07-19)](../superpowers/specs/2026-07-19-curavias-shared-master-data-and-ontology-design.md)
* [DC-SKILL-EVIDENCE-v1 JSON Schema](../../data/synthetic/schema/dc-skill-evidence-v1.schema.json)
* [ADR-0013: Temporary US Region Demo Scope](0013-temporary-us-region-demo-scope.md)
* [ADR-0016: No PHI in MVP Demo Scope](0016-no-phi-in-mvp-demo-scope.md)
* [ADR-0014: Fabric IQ Ontology as target semantic backbone](0014-fabric-iq-ontology-target-backbone-ga-gated.md)
* [ADR-0036: External Trigger Governance](0036-external-trigger-governance.md)
* Issue #255
