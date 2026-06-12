# Sprint 07 Brainstorming - data-contract-baseline

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Slice

`[S07][brainstorming] data-contract-baseline` - Stage 1 Superpowers
brainstorming output for the first data-product data-contract baseline.

## Traceability

1. Parent sprint delegation issue: [#54](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/54)
2. Delivery issue: [#57](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/57)
3. Planned PR: pending
4. Requirements advanced:
   - `FR-DATA-003` (curated datasets unifying operational, planning, and model input data)
   - `FR-DATA-008` (source-to-consumption traceability for operational and AI-serving datasets)
   - `FR-GOV-001` (auditable traceability between source data and downstream consumption)
   - `NFR-DQ-001` (completeness and schema-validity quality checks)
   - `NFR-DQ-002` (lineage from source to serving views)
   - `NFR-DQ-003` (backward compatibility or controlled migration on model change)
   - `NFR-COMP-001` / `NFR-COMP-002` (Swiss DSG and cantonal governance)
   - `NFR-GOV-006` (every response requirement-traceable or an auditable refusal)

## Skill Applicability (Superpowers)

1. `brainstorming` - applies; this artifact is its output.
2. `writing-plans` - next stage; consumes the approved design brief here.
3. `test-driven-development` - applies at execution; contracts are validated
   test-first via the dependency-free validator pattern in
   [data/synthetic/validate_datasets.py](../../../data/synthetic/validate_datasets.py).
4. `systematic-debugging` - conditional; invoked on validation failures.
5. `verification-before-completion` - applies before closeout.

## Source Baseline Reviewed

1. [data-model-and-data-product.md](data-model-and-data-product.md) - episode-based model and first data-product scope.
2. [docs/DATA.md](../../DATA.md) - data architecture and lineage expectations.
3. [docs/COMPLIANCE.md](../../COMPLIANCE.md) - Swiss DSG and cantonal control mappings.
4. [data/synthetic/](../../../data/synthetic/) - Sprint 06 onboarding datasets,
   JSON Schema contracts, and `traceability.json` precedent.
5. [docs/reviews/2026-06-10-ama-sd-review.md](../../reviews/2026-06-10-ama-sd-review.md) and
   [docs/reviews/2026-06-09-ama-sd-review.md](../../reviews/2026-06-09-ama-sd-review.md) - AMA review constraints.

## 1. Design Brief

### Problem

The first data-product lane needs a baseline set of versioned, contract-first
data contracts with traceable ownership and explicit acceptance criteria. Today
the repository carries Sprint 06 onboarding schemas under `data/synthetic/` but
no consolidated, ownership-anchored contract baseline for the episode-based
planning product the AMA reviews mandate.

### Goal

Define a minimal but complete data-contract baseline that:

1. Models the planning domain around the **Hospitalisation Episode** control
   unit, not the patient.
2. Provides three contract-first schemas:
   - Episode demand metadata (the demand side of the match).
   - Bed or station supply metadata (the supply side of the match).
   - Match recommendation output with explainability fields.
3. Carries explicit per-contract ownership, version, residency, and purpose-tag
   metadata so every contract is auditable and requirement-traceable.
4. Reuses the established Sprint 06 contract pattern: JSON Schema (draft-07),
   a `traceability.json` map to `FR/NFR/CH/RV` controls, and a dependency-free
   Python validator with unit tests and a CI gate.

### Domain Boundaries

1. Control unit is the Hospitalisation Episode; patient is out of the planning
   layer.
2. Minimal-Invasive Data Architecture: no PII attributes in any planning
   contract; only pseudonymised identifiers.
3. Identity boundary separation: KIS/EHR identity layer is distinct from the
   planning metadata layer and is not in scope for these contracts.

### Contract Metadata Envelope (proposed common shape)

Each contract document carries an envelope plus a `records` array, mirroring the
Sprint 06 schemas:

1. `datasetId`, `contractId`, `contractVersion` (SemVer).
2. `classification` (for example `operational-confidential`).
3. `residency` fixed to `CH`.
4. `purposeTags` (for example `capacity-planning`, `discharge-planning`).
5. `owner` (accountable role/team) - **new** ownership field for the baseline.
6. Domain-specific `records` with required-field and range validation.

### Ownership Model

Ownership is expressed two ways and must agree:

1. An `owner` field inside each contract envelope (machine-readable).
2. A row in `traceability.json` (or a `contracts` registry) mapping each
   `contractId` to its owner, requirement IDs, and validation evidence path.

## 2. Alternatives and Recommendation

### Alternative A - Extend the Sprint 06 `data/synthetic/` pattern (recommended)

Reuse the proven `data/synthetic/` layout: add planning-product JSON Schemas,
extend `traceability.json` with the new contracts and an `owner` field, and
extend the dependency-free validator and unit tests under the existing CI gate
(`.github/workflows/data-contracts.yml`).

- Pros: zero new tooling; consistent with an established, tested, CI-gated
  pattern; dependency-free; immediate lineage and traceability reuse; lowest
  risk and fastest to acceptance.
- Cons: JSON Schema expressiveness is limited for cross-field semantics; the
  `synthetic` folder name is onboarding-flavoured rather than product-flavoured.

### Alternative B - Introduce a dedicated `data-platform/contracts/` lane

Create a new `data-platform/` lane (per `copilot-instructions.md`) and author
contracts there with a fresh registry and validator.

- Pros: cleaner long-term home aligned to the documented data lane; clearer
  product vs onboarding separation.
- Cons: new scaffolding, validator, and CI wiring duplicate working Sprint 06
  assets; higher risk and slower to first green; premature for a baseline slice.

### Alternative C - Adopt a heavier contract framework (for example a registry/SDK)

Use an external schema-registry or contract SDK (Avro/Protobuf, OpenAPI, or a
managed registry).

- Pros: rich evolution and compatibility tooling.
- Cons: violates the repo's dependency-light, Markdown + JSON + Python
  convention; adds runtime/build dependencies the platform explicitly avoids;
  out of proportion for a baseline.

### Recommendation

Adopt **Alternative A**. It maximises throughput and quality while preserving
governance, lineage, and the existing CI gate. Reserve **Alternative B** as a
follow-up refactor once more than one product lane exists, captured as an ADR if
pursued. Reject **Alternative C** for this baseline.

## 3. Acceptance Criteria

A delivery PR for this slice is acceptable when:

1. Three contract-first JSON Schemas exist for episode demand metadata, bed/station
   supply metadata, and match recommendation output with explainability fields.
2. Each contract envelope includes `contractId`, `contractVersion` (SemVer),
   `classification`, `residency` = `CH`, `purposeTags`, and an `owner` field.
3. No PII attributes appear in any contract; identifiers are pseudonymised and
   the pseudonymisation strategy is documented.
4. Each contract is registered in `traceability.json` (or an equivalent
   contracts registry) mapping it to its `owner` and to `FR/NFR/CH/RV` controls.
5. Data-quality checks cover required-field validation, completeness thresholds,
   and schema conformance, executed by the dependency-free validator.
6. Validation runs green locally
   (`python3 data/synthetic/validate_datasets.py`) and via unit tests
   (`python3 -m unittest discover -s data/synthetic/tests`), and the
   `data-contracts.yml` CI gate passes.
7. Backward-compatibility/migration intent is stated for the baseline
   (`contractVersion` starts at a documented baseline; future changes follow
   `NFR-DQ-003`).
8. Markdown lint and link check pass for every edited document, and edited docs
   follow §9 Document Versioning.
9. PR lists the advanced `FR-*`/`NFR-*` IDs and a security/compliance impact
   statement; no deploy/delete action is taken without `approved-to-apply`.

## 4. Risks and Assumptions

### Risks

1. **Schema-vs-sample drift**: contracts and any sample data can diverge.
   Mitigation: validator gate enforces conformance in CI.
2. **Ownership ambiguity**: `owner` in the envelope and in the registry could
   disagree. Mitigation: validator asserts they match.
3. **Scope creep into ingestion/serving**: the baseline is contracts only.
   Mitigation: explicit out-of-scope list below and separate sprint slices.
4. **Residency/PII regression**: a future field could leak PII. Mitigation:
   `additionalProperties: false`, no-PII assertion in tests, compliance review.
5. **Premature lane move**: forcing a `data-platform/` migration now adds risk.
   Mitigation: defer to a follow-up ADR (Alternative B).

### Assumptions

1. The Sprint 06 `data/synthetic/` validator and CI gate remain the sanctioned
   data-contract validation mechanism.
2. The episode-based, metadata-only model from
   [data-model-and-data-product.md](data-model-and-data-product.md) is approved.
3. Synthetic, non-production datasets are sufficient for SIT; no live provider
   data is in scope.
4. `NFR-GOV-006` traceability is satisfied by linking each contract to a
   requirement ID in the registry.

## Out of Scope

1. Ingestion pipeline implementation (separate Sprint 07 slice).
2. Serving/read-model and capacity-reporting views (separate slice).
3. Policy-gate enforcement changes beyond the data-contracts CI gate.
4. Any deploy/delete action or live-provider data onboarding.
5. Migrating contracts out of `data/synthetic/` into a new `data-platform/` lane
   (candidate follow-up via ADR).

## Stage 1 Gate

This design brief requires approval by the human owner before Stage 2
(`using-git-worktrees`) and Stage 3 (`writing-plans`) begin, per
[stage-runbook.md](stage-runbook.md).
