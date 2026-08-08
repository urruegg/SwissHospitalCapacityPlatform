# Sprint 28 - Curavias Product Owner Agent: Frozen Interface Contracts

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-08-08 |
| **Author** | Urs Rueegg (with Copilot) |
| **Status** | Frozen |
| **Previous Version** | 1.0.0 (initial version, WS-G0 task G0.2); this bump adds §6 the Sprint 41 HTTP service contract (WS-0 task 0.2) |
| **Sprint** | Sprint 28 - Curavias Product Owner Agent full build |
| **Issue** | [#377](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/377) |
| **Owned by** | WS-G0 (task G0.2) |
| **Extends** | [Sprint 28 design spec Section 7](2026-07-25-sprint-28-product-owner-agent-design.md) |
| **Governed by** | [ADR-0043](../../adr/0043-product-owner-agent-foundry-iq-domain.md) |

> **For agentic workers:** this document is the **single source of truth** for the
> shared interface every Sprint 28 workstream builds against. It is published by
> **WS-G0 before** the Wave-2 workstreams (WS-A / WS-B / WS-C / WS-D / WS-X) and
> Wave-3 (WS-RT) start, so they integrate in parallel against a frozen contract
> (design risk R6). **Do not change the shapes below without a version bump here
> and a matching update to
> [`data/synthetic/schema/grounded-chunk-v1.schema.json`](../../../data/synthetic/schema/grounded-chunk-v1.schema.json)
> and the fixtures under
> [`evals/product-owner-agent/fixtures/`](../../../evals/product-owner-agent/fixtures/).**

---

## 1. Scope

The Curavias Product Owner Agent answers product questions grounded on **four
knowledge-source classes** (A corpus, B live-proof, C cost, D ontology). Each
class is a **typed, read-only tool** the orchestrator calls at answer time; each
returns a uniform **`GroundedChunk`** the citation layer renders identically. The
orchestrator composes chunks into a cited answer under a grounded-answer
contract. These five signatures plus the `GroundedChunk` shape are **frozen** for
Sprint 28.

## 2. `GroundedChunk` (frozen)

```text
GroundedChunk {
  classId:      "A" | "B" | "C" | "D"     # knowledge class that produced the chunk
  text:         string                     # the retrieved / computed content (non-empty)
  citation:     {
                  sourceRef:   string      # mandatory provenance handle (see per-class rules)
                  anchor?:     string      # optional in-source anchor (heading / line / ADR id / cell)
                  conceptRef?: string      # Class D only, REQUIRED for D: ontology concept
                  goldBinding?: string     # Class D only, REQUIRED for D: gold-layer binding
                }
  asOf:         ISO-8601                    # freshness stamp (date-time)
  liveness:     "live" | "snapshot"         # snapshot = degraded to a stored value on probe failure
  status:       "verified" | "partial" | "requires-validation"
  confidence:   number 0.0 .. 1.0
  language:     "de" | "en"                 # source language of the chunk (DE/EN parity)
}
```

**Invariants** (enforced by the JSON Schema + the WS-G0 conformance test):

- Every chunk carries a non-empty `citation.sourceRef` - no uncited chunk may
  ever be emitted (`NFR-POA-001`).
- `classId == "D"` **requires** `citation.conceptRef` **and** `citation.goldBinding`.
- `confidence` is bounded to `[0.0, 1.0]`; `additionalProperties` is `false` at
  both object levels (no ad-hoc fields).
- `liveness == "snapshot"` signals a degraded live-proof / cost / ontology probe;
  the answer card must surface it (`NFR-POA-004` transparency).

The machine-checkable form is
[`data/synthetic/schema/grounded-chunk-v1.schema.json`](../../../data/synthetic/schema/grounded-chunk-v1.schema.json)
(JSON Schema draft-07). One example fixture per class lives under
[`evals/product-owner-agent/fixtures/`](../../../evals/product-owner-agent/fixtures/)
and is validated by
[`evals/product-owner-agent/tests/test_grounded_chunk_schema.py`](../../../evals/product-owner-agent/tests/test_grounded_chunk_schema.py).

## 3. Class tool signatures (frozen)

| Class | Signature | Grounding source | `citation.sourceRef` convention | Notes |
| ----- | --------- | ---------------- | ------------------------------- | ----- |
| **A** corpus | `retrieveCorpus(query: string, roleScope: string, lang: "de" \| "en") -> GroundedChunk[]` | Foundry IQ knowledge-base retrieve over the OneLake corpus knowledge source | doc path + commit | `liveness` always `live` (daily refresh); PHI-excluded; interviews first-order. |
| **B** live-proof | `liveProof(question: string, subscriptionScope: string) -> GroundedChunk[]` | read-only Resource Graph / Fabric REST / Foundry Agent API | feed + as-of | Reconciled against `docs/bom.yaml` / `docs/region-availability.yaml` / `AGENTS.md`; degrades to `snapshot` + flags drift on mismatch. |
| **C** cost | `costAnswer(question: string) -> GroundedChunk[]` | Cost Management (PROD) + GitHub Copilot token cost + BVA baseline ([ADR-0025](../../adr/0025-bva-kpi-catalog.md)) | cost feed + BVA baseline + as-of | Ranges-with-assumptions within BVA +/- 30%; refuses extrapolation beyond the feed window. |
| **D** ontology | `ontologyQuery(question: string) -> GroundedChunk[]` | `da_hospital_capacity` Fabric Data Agent (read-only) | data-agent artefact ref | `citation.conceptRef` + `citation.goldBinding` REQUIRED; Preview feature-flagged; degrades to `snapshot`. |

## 4. Orchestrator signature (frozen)

```text
answer(question: string, caller: CallerContext) -> {
  answer:     string
  chunks:     GroundedChunk[]
  status:     "verified" | "partial" | "requires-validation"
  confidence: number 0.0 .. 1.0
  language:   "de" | "en"
}
```

Contract:

- Routes to one or more of Class A/B/C/D; grounds; synthesises an **advisory-only**
  answer; cites every claim.
- Enforces the **grounded-answer contract**: emit an answer only when at least `N`
  chunks clear the confidence threshold, otherwise degrade to a **transparent
  partial** (`status: "partial"`) - never an uncited claim (`NFR-POA-001`).
- Applies an **authorisation-aware filter** by caller entitlement + domain,
  including the partner tier which never sees internal cost/security detail
  (`FR-POA-009`).
- Answers in **DE or EN** with source-language transparency (`FR-POA-008`).
- Logs the full bundle (question -> chunks -> citations -> confidence -> caller)
  to the Cosmos audit store (`NFR-POA-002`).

## 6. HTTP service contract (Sprint 41, WS-0 task 0.2)

`po-agent-service` (the FastAPI wrapper around `orchestrator.answer()`,
Sprint 41 WS-SVC) exposes exactly two routes. No other routes exist; no
mutation is possible over this contract.

### `POST /answer`

Request body:

```json
{
  "question": "string",
  "caller": { "persona": "string", "tier": "internal" },
  "language": "en"
}
```

- `caller.tier` is `"internal"` or `"partner"` and drives the existing
  `authz.filter_chunks` partner-tier redaction unchanged - the HTTP layer
  must not bypass it.
- `language` is `"en"` or `"de"`.

Response body - the frozen frontend `GroundedReco` shape
(`apps/hcc-app-fluent/src/copilot-rail/reco.ts`), field-for-field:

```json
{
  "agentLabel": "product-owner-agent",
  "contextChip": { "subject": "string", "tone": "signal" },
  "read": "string",
  "levers": [],
  "citations": ["string"],
  "provenance": "live",
  "refused": false
}
```

`refused: true` on the grounded-refusal path (fewer than `N` chunks cleared
the confidence threshold) - the response still carries `read` as the
transparent-partial text per the existing orchestrator contract; it never
omits the field.

### `GET /healthz`

`{"status": "ok"}`, no authentication, used by the Container App health
probe only. Carries no grounded content and is not rate-limited by the
authz layer.

## 5. Requirement traceability

| Contract element | Requirement |
| ---------------- | ----------- |
| `GroundedChunk.citation.sourceRef` mandatory; no uncited chunk | `FR-POA-001`, `NFR-POA-001` |
| Class A corpus signature | `FR-POA-004` |
| Class B live-proof signature | `FR-POA-005` |
| Class C cost signature | `FR-POA-006` |
| Class D ontology signature (`conceptRef` + `goldBinding`) | `FR-POA-007` |
| `language` field + orchestrator DE/EN | `FR-POA-008` |
| Orchestrator authz filter + partner tier | `FR-POA-009` |
| Orchestrator audit bundle | `NFR-POA-002` |
| Advisory-only, `snapshot` transparency | `NFR-POA-004` |

## 6. Change control

Any change to the `GroundedChunk` shape or the five signatures is a **breaking
change**: bump this document (MAJOR), bump the JSON Schema `$id` version, update
all four fixtures, and re-run the conformance test. Wave-2/Wave-3 workstreams
must re-integrate against the new version.
