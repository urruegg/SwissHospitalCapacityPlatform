# Sprint 33 - Curavias BVA Agent: Frozen Interface Contracts

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-28 |
| **Author** | Urs Rüegg (with Copilot) |
| **Status** | **Frozen** |
| **Previous Version** | n/a (initial version) |
| **Sprint** | Sprint 33 - Curavias BVA Agent |
| **Issue** | [#490](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/490) |
| **Owned by** | WS-G0 (Plan Task 3) |
| **Extends** | [Sprint 33 BVA Agent design spec Sections 3, 6, 7, and 8][bva-design] |
| **Governed by** | A forthcoming BVA-Agent ADR (number assigned in the Sprint 33 governance close-out) |

> **For agentic workers:** this document is the **single source of truth** for the
> shared interface every Sprint 33 BVA workstream builds against. It is published
> by **WS-G0 before** WS-A / WS-B / WS-D / WS-C start, so they integrate in
> parallel against a frozen contract. **Do not change the shapes below without a
> version bump here and a matching update to
> [`data/synthetic/schema/bva-simulation-result-v1.schema.json`][bva-simulation-schema],
> [`data/synthetic/schema/bva-opportunity-v1.schema.json`][bva-opportunity-schema],
> the fixtures under [`evals/bva-agent/fixtures/`][bva-fixtures], and
> [`evals/bva-agent/tests/test_bva_schema_conformance.py`][bva-conformance-test].**

---

## 1. Scope

The Curavias BVA Agent freezes three Sprint 33 interface shapes before the
parallel workstreams begin:

* the deterministic `bva.simulate` result envelope, **`BvaSimulationResult`**;
* the Cosmos DB system-of-record **`Opportunity`** record; and
* the CHF cost-basis normalization contract used by the data product and calc
  engine.

The machine-checkable forms for the two JSON shapes are
[`data/synthetic/schema/bva-simulation-result-v1.schema.json`][bva-simulation-schema]
and [`data/synthetic/schema/bva-opportunity-v1.schema.json`][bva-opportunity-schema].
Their canonical examples are
[`evals/bva-agent/fixtures/bva-simulation-result-example.json`][bva-simulation-fixture]
and [`evals/bva-agent/fixtures/bva-opportunity-example.json`][bva-opportunity-fixture].
The CHF normalization rule is a prose contract in this document; it deliberately
has no separate JSON Schema.

## 2. `BvaSimulationResult` (frozen)

`bva.simulate` returns exactly one `BvaSimulationResult` object. The top-level
object has `additionalProperties: false` and requires `scenarioId`, `currency`,
`asOf`, `baseline`, `projection`, `metrics`, `sensitivity`, and `chunks`.

```text
BvaSimulationResult {
  scenarioId: string                         # non-empty; scenario id and Opportunity join key
  currency:   "CHF"                          # all monetary figures are normalized to CHF
  asOf:       ISO-8601 date-time              # gold snapshot / baseline freshness stamp

  baseline: {
    totalCostChf: number >= 0
    oneTimeChf:   number >= 0
    annualRunChf: number >= 0
    hospitals:    integer >= 1
  }

  projection: {
    hospitalName:          string             # non-empty
    archetype:             "acute" | "rehab" | "spitex"
    onboardingOneTimeChf:  number >= 0
    annualRunDeltaChf:     number >= 0
    annualBenefitChf:      number             # modelled benefit; may be provisional
  }

  metrics: {
    roiPct:        number
    paybackMonths: number >= 0
    tco3yChf:      number
    npvChf:        number
  }

  sensitivity: {
    low:  number                              # low roiPct band
    base: number                              # base roiPct band
    high: number                              # high roiPct band
  }

  chunks: GroundedChunk[]                     # minItems: 1; each item is Class C
}
```

The `chunks` array embeds the Sprint 28
[`GroundedChunk`][grounded-chunk-schema] field shape so the Product Owner (PO)
Agent citation layer can consume BVA output unchanged:

```text
GroundedChunk (inside BvaSimulationResult.chunks) {
  classId:    "C"                             # cost knowledge class
  text:       string                           # non-empty cited figure narrative
  citation:   {
                sourceRef:   string            # REQUIRED, non-empty
                anchor?:     string
                conceptRef?: string
                goldBinding?: string
              }
  asOf:       ISO-8601 date-time
  liveness:   "live" | "snapshot"
  status:     "verified" | "partial" | "requires-validation"
  confidence: number 0.0 .. 1.0
  language:   "de" | "en"
}
```

**Invariants** (enforced by the JSON Schema + WS-G0 conformance test):

* `currency` is always `CHF`.
* Every headline figure emitted to a user appears as a Class-C `GroundedChunk`
  with a non-empty `citation.sourceRef`.
* The LLM never performs arithmetic. The deterministic `bva.simulate` engine
  computes ROI, payback, 3-year TCO, NPV, and sensitivity bands before the
  agent narrates them.
* BVA chunks remain compatible with
  [`data/synthetic/schema/grounded-chunk-v1.schema.json`][grounded-chunk-schema]
  for PO Class-C evidence consumption.

## 3. `Opportunity` (frozen)

The `Opportunity` record is the Cosmos DB system-of-record for hospital
onboarding and value-assessment asks. The top-level object has
`additionalProperties: false` and requires `id`, `hospitalName`, `archetype`,
`createdAt`, `createdBy`, `status`, `askText`, `language`, and `history`.

```text
Opportunity {
  id:           string                         # non-empty
  hospitalName: string                         # non-empty
  archetype:    "acute" | "rehab" | "spitex"
  createdAt:    ISO-8601 date-time
  createdBy:    string                         # non-empty
  status:       "new" | "evaluating" | "qualified" | "disqualified" |
                "onboarding" | "won" | "lost"
  askText:      string                         # non-empty originating question
  language:     "de" | "en"

  bvaResult?:   object | null                  # BvaSimulationResult snapshot; null until first simulate

  poVerdict?:   {
                  verdict?:   "go" | "no-go" | "conditional"
                  rationale?: string
                  citations?: string[]
                } | null

  inputs?:      object | null                  # slot-filled deltas: beds, occupancy, case-mix, scope

  history:      HistoryEvent[]                 # append-only audit
}

HistoryEvent {
  at:    ISO-8601 date-time
  event: string                                # non-empty
  by?:   string
}
```

Lifecycle is frozen as:

```text
new -> evaluating -> qualified / disqualified -> onboarding -> won / lost
```

Contract:

* Agents may create or update opportunities through the app/orchestrator flow,
  but they never auto-advance a record past `qualified`.
* Human progression owns `onboarding`, `won`, and `lost`.
* Re-asks about the same hospital update the same `Opportunity` and append to
  `history`; they never fork a parallel record for the same ask lineage.
* `bvaResult` stores the cited `BvaSimulationResult` snapshot used for the
  answer; `poVerdict` stores PO's go / no-go / conditional decision, rationale,
  and citation handles.

## 4. Cost-basis normalization contract (frozen)

The Sprint 33 BVA cost basis is standardized in CHF before any ROI/TCO metric is
computed:

```text
teamCostChf = copilotCostChf + (humanElectiveHours * configuredRoleRateChf)
```

Where:

* `copilotCostChf` is derived from Copilot AIU/token spend in the BVA cost data
  product.
* `humanElectiveHours` and `configuredRoleRateChf` come from the explicit team
  effort input line, not from LLM inference.
* Azure and BOM actuals that arrive in USD are converted to CHF only through the
  explicit `bva_fx_rate.csv` line for the relevant period.
* Settling weeks are marked provisional and must surface as `partial` or
  `requires-validation` evidence until the cost period is closed.

This is a prose contract, not a third schema. Downstream schemas and fixtures may
reference the normalized CHF outputs, but they must not invent alternate
currency or rate fields.

## 5. PO <-> BVA hand-off

For onboarding/value questions, the app orchestrator fans out to BVA and PO as
peer typed sub-agents:

1. BVA slot-fills the required deltas, calls deterministic `bva.simulate`, and
   returns `BvaSimulationResult`.
2. PO consumes `BvaSimulationResult.chunks` as Class-C evidence, alongside its
   other grounded sources, and emits `poVerdict` (`go`, `no-go`, or
   `conditional`) with rationale and citation handles.
3. The orchestrator composes one cited answer: PO verdict first, BVA financials
   as supporting evidence, and all citations rendered through the shared
   citation layer.
4. The same answer bundle is written back to the `Opportunity` record: BVA output
   in `bvaResult`, PO output in `poVerdict`, and the interaction in `history`.

Pure financial questions may route to BVA alone; pure strategic questions may
route to PO alone. Onboarding/value-fit questions use the hand-off above.

## 6. Change control

Any change to `BvaSimulationResult`, `Opportunity`, or the CHF cost-basis
normalization contract is a contract change. No shape change is allowed without:

* a version bump in this document;
* matching updates to
  [`data/synthetic/schema/bva-simulation-result-v1.schema.json`][bva-simulation-schema]
  and [`data/synthetic/schema/bva-opportunity-v1.schema.json`][bva-opportunity-schema];
* matching updates to
  [`evals/bva-agent/fixtures/bva-simulation-result-example.json`][bva-simulation-fixture]
  and [`evals/bva-agent/fixtures/bva-opportunity-example.json`][bva-opportunity-fixture];
* a matching update to
  [`evals/bva-agent/tests/test_bva_schema_conformance.py`][bva-conformance-test];
  and
* a re-run of the conformance test and document gates before downstream
  workstreams re-integrate.

[bva-conformance-test]: ../../../evals/bva-agent/tests/test_bva_schema_conformance.py
[bva-design]: 2026-07-28-sprint-33-curavias-bva-agent-design.md
[bva-fixtures]: ../../../evals/bva-agent/fixtures/
[bva-opportunity-fixture]: ../../../evals/bva-agent/fixtures/bva-opportunity-example.json
[bva-opportunity-schema]: ../../../data/synthetic/schema/bva-opportunity-v1.schema.json
[bva-simulation-fixture]: ../../../evals/bva-agent/fixtures/bva-simulation-result-example.json
[bva-simulation-schema]: ../../../data/synthetic/schema/bva-simulation-result-v1.schema.json
[grounded-chunk-schema]: ../../../data/synthetic/schema/grounded-chunk-v1.schema.json
