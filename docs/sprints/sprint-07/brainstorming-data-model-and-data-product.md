# Sprint 07 Brainstorming - Data Model and Data Product

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-06-12 |
| **Author** | GitHub Copilot |
| **Status** | Draft |
| **Previous Version** | 0.0.0 (new brainstorming artifact) |

## Stage and Traceability

| Field | Value |
| ----- | ----- |
| **Superpowers stage** | Stage 1 - `brainstorming` |
| **Slice** | `data-model-and-data-product` |
| **Sprint issue** | urruegg/SwissHospitalCapacityPlatform#59 |
| **Parent sprint delegation issue** | urruegg/SwissHospitalCapacityPlatform#54 |
| **Planned PR** | pending |
| **Requirements** | `FR-DATA-003`, `FR-DATA-005`, `FR-DATA-008`, `FR-DC-002`, `FR-GOV-001`, `NFR-DQ-001`, `NFR-DQ-002`, `NFR-DQ-003`, `NFR-COMP-001`, `NFR-COMP-004`, `NFR-COMP-005` |

## Source Inputs

1. [sprint-07-data-platform-and-data-products-superpowers.md](../sprint-07-data-platform-and-data-products-superpowers.md)
2. [data-model-and-data-product.md](data-model-and-data-product.md)
3. [docs/reviews/2026-06-10-ama-sd-review.md](../../reviews/2026-06-10-ama-sd-review.md)
4. [stage-runbook.md](stage-runbook.md) (Stage 1 entry/exit criteria)

---

## 1. Design Brief

### 1.1 Problem Statement

Sprint 07 must turn the AMA-reviewed "Hospitalisation-as-Unit" pattern into a
concrete, contract-first data model and a first data product. The planning
platform must match **demand** (episode metadata) against **supply** (bed or
station metadata) and emit an explainable **recommendation**, while keeping
the planning layer free of PII and strictly separated from the KIS identity
layer.

The review flagged metadata completeness as a single-point-of-failure risk and
governance as "principles, not executable controls". The brief therefore treats
schema contracts plus metadata quality controls as the core deliverable, not an
afterthought.

### 1.2 Goals

1. Define the episode-based control unit (Hospitalisation Episode) as the demand
   record, decoupled from patient identity.
2. Define a bed/station supply record carrying only planning metadata.
3. Define a match recommendation record with explainability fields
   (`FR-DC-002`, matching-engine explainability per review §5.5).
4. Embed metadata quality controls: required-field validation, completeness
   thresholds, and schema-conformance checks (`NFR-DQ-001`).
5. Keep the KIS identity layer separated from the planning metadata layer; only
   a pseudonymised episode identifier crosses the boundary.

### 1.3 Assumptions

1. Pseudonymisation happens **before** data enters the planning platform; the
   platform never receives or stores re-identification keys (review §5.3,
   `NFR-COMP-005`).
2. Metadata attributes are sufficient to describe clinical need for matching
   purposes (review §3.1 implicit assumption - tracked as a risk in §3).
3. Schema contracts will be expressed as JSON Schema (draft-07) to stay
   consistent with the existing `data/synthetic/schema/` contracts.
4. Even pseudonymised health-context metadata is treated as sensitive
   (`operational-confidential`) and residency-bound to `CH`
   (`NFR-COMP-001`, `NFR-COMP-004`, review §8).
5. The sample data generator slice
   ([sample-data-generator.md](sample-data-generator.md)) consumes these
   contracts; this brief defines the contract shape it must satisfy.

### 1.4 Alternatives Considered

| # | Option | Pros | Cons | Decision |
| - | ------ | ---- | ---- | -------- |
| A | Patient-centric record as control unit | Familiar clinical mental model | Re-introduces PII into planning layer; violates Minimal-Invasive Data Architecture and DSG minimisation | Rejected |
| B | Episode-based demand record with pseudonymised episode id, separate supply record, separate recommendation record (contract-first) | Matches AMA review; clean demand/supply separation; supports explainability; aligns with existing schema conventions | More contracts to maintain and version | **Recommended** |
| C | Single denormalised "match" table combining episode, bed, and decision | Simpler to query | Couples demand, supply, and decision lifecycles; weak lineage; harder to version independently | Rejected |
| D | Defer quality controls to a later sprint | Faster first cut | Leaves the review's top single-point-of-failure risk unmitigated | Rejected |

**Recommendation:** Option B - three independently versioned, contract-first
schemas (demand, supply, recommendation) with embedded quality controls and a
pseudonymised episode identifier as the only cross-boundary key.

### 1.5 Out of Scope (this brainstorming slice)

1. Implementing the matching/optimisation algorithm itself.
2. Building ingestion pipelines or the serving/read model.
3. Authoring the pseudonymisation service (design only; owned by security lane).
4. Production deployment or any `deploy`/`delete` action.
5. Final schema files under `data/synthetic/schema/` - those land in the
   `writing-plans` and execution stages via a separate PR.

---

## 2. Candidate Schema Contract Set

Contracts are draft proposals for review. Field naming and the
`classification` / `residency` / `purposeTags` envelope follow the existing
`data/synthetic/schema/` convention. **No PII fields appear in any contract.**

### 2.1 Episode Demand Metadata (`DC-EPISODE-DEMAND-v1`)

Demand side of the match. Control unit = Hospitalisation Episode.

| Field | Type | Notes |
| ----- | ---- | ----- |
| `episodePseudoId` | string | Pseudonymised episode identifier; **only** key crossing the KIS boundary. No name, DOB, or AHV number. |
| `providerId` | string | Originating provider (hospital). |
| `requestedSpecialty` | string | Specialty taxonomy reference (versioned). |
| `careLevel` | enum | e.g. `general`, `intermediate`, `intensive`. |
| `expectedAdmissionWindow` | object | `{ start, end }` ISO-8601 timestamps. |
| `expectedLengthOfStayBand` | enum | Banded (e.g. `short`, `medium`, `long`) - not exact, to avoid re-identification. |
| `isolationRequirement` | enum | `none`, `contact`, `droplet`, `airborne`. |
| `mobilityNeeds` | enum | Coarse-grained planning attribute. |
| `priorityScore` | number | Planning priority; no clinical diagnosis text. |
| `metadataCompleteness` | number | 0-1 completeness indicator (quality control). |

### 2.2 Bed / Station Supply Metadata (`DC-BED-SUPPLY-v1`)

Supply side of the match.

| Field | Type | Notes |
| ----- | ---- | ----- |
| `supplyRecordId` | string | Stable bed/station record id. |
| `providerId` | string | Owning provider. |
| `stationId` | string | Ward/station identifier. |
| `bedId` | string | Bed identifier (operational, non-personal). |
| `specialtyCapabilities` | array | Specialties the station can serve (versioned taxonomy). |
| `careLevelCapability` | enum | Max supported care level. |
| `isolationCapability` | array | Supported isolation modes. |
| `availabilityState` | enum | `available`, `reserved`, `occupied`, `blocked`. |
| `availableFrom` | string | ISO-8601 timestamp. |
| `metadataCompleteness` | number | 0-1 completeness indicator (quality control). |

### 2.3 Match Recommendation Output (`DC-MATCH-RECOMMENDATION-v1`)

Decision artifact with explainability (`FR-DC-002`, review §5.5).

| Field | Type | Notes |
| ----- | ---- | ----- |
| `recommendationId` | string | Stable recommendation id. |
| `episodePseudoId` | string | Links to demand record (pseudonymised). |
| `supplyRecordId` | string | Links to supply record. |
| `matchScore` | number | Overall match score. |
| `explanation` | array | Ordered contributing factors (e.g. specialty match, care-level fit, isolation fit, timing fit). Supports the "why was a bed assigned?" requirement. |
| `constraintsSatisfied` | array | Hard constraints met. |
| `constraintsViolated` | array | Soft constraints relaxed, if any. |
| `humanOverrideEligible` | boolean | Flags human-in-the-loop override path (review §5.5). |
| `generatedAt` | string | ISO-8601 timestamp for auditability (`FR-GOV-001`). |
| `modelRunId` | string | Run identifier for lineage/audit (`NFR-DQ-002`). |

### 2.4 Shared Contract Envelope and Quality Controls

All three contracts share an envelope and embedded quality controls:

1. `contractId`, `contractVersion` (SemVer) for controlled versioning
   (`NFR-DQ-003`).
2. `classification: operational-confidential` and `residency: CH`
   (`NFR-COMP-001`, `NFR-COMP-004`).
3. `purposeTags` (e.g. `capacity-planning`, `bed-management`) for processing
   inventory (`NFR-COMP-005`).
4. `additionalProperties: false` to reject unexpected/PII fields by default.
5. Required-field lists per record (validation rule).
6. Completeness thresholds enforced on `metadataCompleteness` (e.g. demand and
   supply records below threshold are rejected or quarantined).
7. Source-to-serving lineage keys (`providerId`, `modelRunId`) for traceability
   (`NFR-DQ-002`, `FR-DATA-008`).

---

## 3. Risks and Assumptions

| # | Risk | Impact | Likelihood | Mitigation |
| - | ---- | ------ | ---------- | ---------- |
| R1 | Metadata too sparse to drive correct matching (review's single-point-of-failure hypothesis) | High | High | Completeness thresholds + required-field validation as a hard gate before matching; reject/quarantine incomplete records. |
| R2 | Pseudonymised metadata still allows re-identification (rare specialty + timing + provider) | High | Medium | Band time/length-of-stay attributes; treat data as sensitive (`operational-confidential`); no free-text clinical fields; residency `CH`. |
| R3 | KIS-to-planning boundary leaks identifying fields | High | Medium | `additionalProperties: false`; only `episodePseudoId` crosses boundary; schema-conformance check rejects unknown fields. |
| R4 | Schema drift across providers breaks downstream consumers | Medium | Medium | SemVer `contractVersion` + backward-compatibility/migration rule (`NFR-DQ-003`). |
| R5 | Recommendation not explainable enough for human override | Medium | Medium | Mandatory ordered `explanation` and `constraints*` fields; `humanOverrideEligible` flag. |
| R6 | Missing lineage undermines audit (review §8) | Medium | Medium | `modelRunId`, `generatedAt`, provider keys carried end-to-end (`FR-GOV-001`, `NFR-DQ-002`). |

**Open questions for human owner (Stage 1 gate):**

1. Confirm the banded vs exact length-of-stay decision is acceptable for
   matching quality.
2. Confirm `episodePseudoId` is generated upstream of the platform and the
   platform never holds the mapping.
3. Confirm whether recommendation records require a retention/expiry attribute
   in this slice or a later one.

---

## 4. Acceptance Criteria

A subsequent `writing-plans` and execution slice for this track is acceptable
when:

1. Three contract-first JSON Schemas exist for demand, supply, and
   recommendation, each with `contractId` and SemVer `contractVersion`.
2. No contract contains PII attributes; `additionalProperties: false` is set on
   every record object.
3. Each demand and supply contract enforces required fields and a completeness
   threshold (`NFR-DQ-001`).
4. The recommendation contract includes explainability fields
   (`explanation`, `constraints*`, `humanOverrideEligible`) (`FR-DC-002`).
5. Each contract carries `classification`, `residency: CH`, and `purposeTags`
   (`NFR-COMP-001`, `NFR-COMP-004`, `NFR-COMP-005`).
6. Only the pseudonymised `episodePseudoId` crosses the KIS/planning boundary,
   and the separation is documented.
7. Schema-conformance validation runs in CI alongside the existing
   `data/synthetic` validator (`NFR-DQ-001`, `NFR-DQ-002`).
8. Every contract is traceable from requirement ID to schema to validation
   evidence (`FR-GOV-001`, `FR-DATA-008`).
9. A `systematic-debugging` record exists for any validation failure
   encountered during execution.

---

## 5. Planned PR Note

**Planned PR: pending.**

This artifact is the Stage 1 (`brainstorming`) output only. Per the
[stage-runbook](stage-runbook.md), the design brief must be approved by the
human owner before Stage 2 (`using-git-worktrees`) and Stage 3
(`writing-plans`) begin. The candidate schema contracts above are proposals,
not committed schema files; they are realised under `data/synthetic/schema/`
in a later, plan-driven PR linked back to issue #59.

## 6. Next Stage

On approval of this brief, proceed to `writing-plans` using
[issue-body-templates.md](issue-body-templates.md) Template B, and record the
gate outcome in [checkpoint-matrix.md](checkpoint-matrix.md).
