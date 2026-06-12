# Sprint 07 Brainstorming - Ingestion Pipeline Slice

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Proposed |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage

Superpowers Stage 1 `brainstorming` output for the Sprint 07 ingestion pipeline
slice. The next stage is `writing-plans` (Template B in
[issue-body-templates.md](issue-body-templates.md)); this brief is the approved
design source for that plan.

## Traceability

| Field | Value |
| ----- | ----- |
| Slice | `ingestion-pipeline-slice` (synthetic source onboarding) |
| Brainstorming issue | #55 |
| Parent sprint delegation issue | #54 |
| Planned PR | pending |
| Parent sprint document | [sprint-07-data-platform-and-data-products-superpowers.md](../sprint-07-data-platform-and-data-products-superpowers.md) |

### Requirements in scope

| ID | Why it applies |
| -- | -------------- |
| `FR-DATA-001` | Ingest provider-internal operational signals (ED, ADT, bed-state, discharge) into the data platform flow. |
| `FR-DATA-003` | Land ingested signals into curated datasets that unify operational and model input data. |
| `FR-DATA-006` | Ingest from KIS/EHR, ED, bed management, and staffing/planning source classes (synthetic equivalents for this slice). |
| `FR-DATA-008` | Preserve source-to-consumption traceability for ingested datasets. |
| `FR-ONB-001` | Onboard using a minimum required metadata set only (no direct PII). |
| `NFR-DQ-001` | Apply completeness and schema-validity quality checks on ingested feeds. |
| `NFR-DQ-002` | Maintain lineage from source to curated/serving views. |
| `NFR-PERF-001` | Keep an ingestion shape compatible with near-real-time updates for the named signals. |
| `NFR-COMP-004` | Honour Swiss/permitted-jurisdiction data-residency constraints for each dataset class. |
| `NFR-GOV-006` | Provide command-level validation evidence for the PR output contract (per copilot-instructions §6). |

## Problem

Sprint 07 needs an ingestion pipeline slice that onboards synthetic source data
into the data platform flow (ingestion -> curation -> serving) without
introducing direct PII and without standing up deploy/delete infrastructure
ahead of approval. The slice must reuse the existing synthetic dataset and
contract assets rather than invent a parallel stack.

## Constraints

1. Swiss region and residency constraints apply to every dataset class
   (`NFR-COMP-004`).
2. No deploy/delete without an explicit `approved-to-apply` comment
   (AGENTS.md §4); this slice is plan-and-evidence only.
3. Metadata-only, pseudonymised identifiers; KIS identity layer stays outside
   the planning dataset (parent sprint review-driven constraints).
4. Reuse, do not duplicate, the Sprint 06 synthetic dataset and JSON Schema
   contracts under `data/synthetic/`.

## Out of Scope

1. Real source-system connectors or live KIS/EHR/FHIR integration.
2. Provisioning or deleting any Azure resource.
3. Forecasting, serving dashboards, or read-model slices (handled by separate
   Sprint 07 slices).

## 1) Design Brief

The ingestion pipeline slice is a dependency-free, evidence-producing pipeline
that takes synthetic source bundles and lands them as validated, lineage-tagged
curated datasets ready for downstream serving.

Pipeline stages:

1. **Ingest** - read synthetic source bundles (episode demand and bed/station
   supply metadata) from `data/synthetic/datasets/`.
2. **Validate** - run schema-conformance and completeness checks using the
   existing JSON Schema contracts in `data/synthetic/schema/`
   (`validate_datasets.py` is the reference validator).
3. **Curate** - normalise validated records into a curated layer with stable
   field names, pseudonymised identifiers, and ingestion run metadata
   (timestamp, source id, schema version).
4. **Trace** - emit a lineage/traceability record linking each curated dataset
   back to its source bundle, contract version, and validation result.
5. **Gate** - fail the run (non-zero exit) on any critical schema or
   completeness failure so CI can block on it.

Alignment:

- Builds on the Sprint 06 synthetic data gate (`data/synthetic/`) and the
  Sprint 07 sample data generator and data-product scope artifacts.
- Keeps the planning layer metadata-only; no PII attributes cross the ingestion
  boundary.
- Produces GitHub-native evidence (validation summary JSON + PR validation
  section) consistent with the repository's evidence model.

## 2) Alternatives and Recommendation

### Option A - Extend the existing `data/synthetic/` validator into a staged ingestion script (recommended)

Add a thin ingestion/curation step alongside the proven
`validate_datasets.py`, reusing its schema contracts and dependency-free,
exit-1-on-failure style, and emitting curated outputs plus a lineage record.

- Pros: minimal new surface, reuses verified contracts and CI pattern
  (`.github/workflows/data-contracts.yml`), dependency-free, fast to validate.
- Cons: still file-based (not a streaming engine), so near-real-time is modelled
  by run cadence rather than true streaming.

### Option B - Introduce a data-pipeline framework (e.g. orchestration/streaming engine)

Stand up a pipeline framework for ingestion.

- Pros: closer to a production near-real-time architecture.
- Cons: heavy new dependency and runtime, contradicts the repo's
  Markdown+Bicep+YAML shape, requires an ADR and likely deploy gates; excessive
  for a synthetic-source slice.

### Option C - Bicep/infra-first ingestion (UC1 output templates)

Model ingestion purely as landing-zone Bicep output.

- Pros: aligns with infra lane.
- Cons: needs `approved-to-apply` and a customer subscription; produces no
  runnable data-quality evidence for this slice; premature.

### Recommendation

Adopt **Option A**. It satisfies the in-scope requirements with the smallest
change, reuses verified assets, keeps the slice plan-and-evidence only (no
deploy/delete), and leaves a clean seam for Option B later if real-time
ingestion becomes a funded requirement (record that pivot via an ADR).

## 3) Acceptance Criteria

1. A documented ingestion pipeline slice produces curated, pseudonymised,
   metadata-only datasets from synthetic source bundles in
   `data/synthetic/datasets/` (`FR-DATA-001`, `FR-DATA-003`, `FR-ONB-001`).
2. Each ingestion run validates inputs against the existing JSON Schema
   contracts and fails (non-zero exit) on any critical schema or completeness
   violation (`NFR-DQ-001`).
3. Each curated dataset carries a lineage/traceability record linking it to its
   source bundle, contract version, and validation outcome (`FR-DATA-008`,
   `NFR-DQ-002`).
4. The pipeline is dependency-free (standard library only) and runnable via a
   single documented command, with results reproducible in deterministic mode.
5. A validation summary artifact (row counts, null/completeness checks, field
   coverage) is produced and referenceable as PR evidence (`NFR-GOV-006`).
6. No direct PII attributes appear in any ingested or curated dataset; KIS
   identity data stays outside the planning dataset (`NFR-COMP-004`, parent
   sprint constraints).
7. No deploy/delete action is taken; any future apply step requires an explicit
   `approved-to-apply` comment (AGENTS.md §4).
8. The ingestion shape is compatible with run-cadence near-real-time refresh of
   ED/ADT/bed-state/discharge signals (`NFR-PERF-001`).

## 4) Risks and Assumptions

### Assumptions

1. The Sprint 06 synthetic datasets and JSON Schema contracts under
   `data/synthetic/` are the canonical source bundles for this slice.
2. `python3` (standard library only) is the accepted runtime, matching the
   existing data-contracts validator and CI workflow.
3. Synthetic data is sufficient for Sprint 07; real connectors are out of scope.
4. Run-cadence refresh is an acceptable model of near-real-time for this slice.

### Risks

| Risk | Impact | Mitigation |
| ---- | ------ | ---------- |
| Synthetic schema drifts from real KIS/FHIR shapes | Curated model may need rework for real sources | Keep contracts versioned (`NFR-DQ-003`) and isolate normalisation logic. |
| Pseudonymisation strategy leaks linkable identifiers | DSG/residency breach | Enforce metadata-only fields and add an explicit no-PII check in validation. |
| File-based pipeline misread as production-ready | Operational misuse | State the synthetic/run-cadence boundary explicitly in the slice docs. |
| Scope creep into serving/forecasting slices | Sprint slippage | Hold the out-of-scope list; route extensions to their own slices/issues. |
| Lineage record incomplete | Loss of source-to-consumption traceability | Make the lineage/traceability record a hard, validated output of every run. |

## Next Stage Handoff

Once this brief is approved on issue #55, open the
`[S07][writing-plans] ingestion-pipeline-slice` issue (Template B) using this
artifact as the approved design source, then proceed to execution under the
Sprint 07 stage gates in [checkpoint-matrix.md](checkpoint-matrix.md).
