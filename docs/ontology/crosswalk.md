# Ontology Crosswalk — Reference Layer ↔ Fabric IQ Operational Layer ↔ Data Contract

| Field | Value |
| ----- | ----- |
| **Version** | 0.1.0 |
| **Date** | 2026-07-02 |
| **Author** | Urs Rüegg |
| **Status** | Draft — Sprint 09 skeleton (RB-11) |
| **Previous Version** | — (new file) |
| **Governance** | Every PR that touches [reference-layer.ttl](reference-layer.ttl) OR the operational-layer semantic model MUST update this file in the same PR. Reviewed by semantic / ontology owner per [FR-GOV-ONT-002](../PRD.md#h-semantic-ontology). |
| **Enforcement** | Manual review today; CI conformance check delivered by follow-up PR (RB-08) per [FR-GOV-ONT-003](../PRD.md#h-semantic-ontology). |

## Purpose

Single source of truth for the mapping between the **three artefact planes** the ontology spans:

1. **Reference layer** — classes in [reference-layer.ttl](reference-layer.ttl) (OWL/RDF).
2. **Operational layer** — entity types in the Fabric IQ operational ontology (generated from the Sprint-09 Power BI semantic model per [AMA §11.2](../reviews/2026-07-01-ama-hcc-northstar-review.md#112-mvo-scope-for-sprint-09-proposed)).
3. **Data contract layer** — versioned contracts in [`docs/DATA.md`](../DATA.md) and the `DC-*` family.

## Crosswalk (MVO scope per ADR-0014 §3)

| Reference-layer class | Fabric IQ entity type | Data contract(s) | Time-series binding | Notes |
| --- | --- | --- | --- | --- |
| `hcp:Bed` | `Bed` | `DC-MASTER-07` *(dim_ward_capacityunit — bed rollup, Sprint 9 baseline)*; future `DC-BED-STATE-v1` for the eventhouse feed | **`bed-state` (eventhouse, first target)** — occupied / available / blocked / cleaning per [ADR-0014 §3](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#3-sprint-09-delivers-the-minimum-viable-ontology-mvo) | Sprint 09 delivers this first (MVO gate G-A). |
| `hcp:ORSlot` | `ORSlot` | [`DC-OR-SCHEDULE-v1`](../../data/synthetic/schema/dc-or-schedule-v1.schema.json) *(drafted 2026-07-02, RB-10; ingestion in Sprint 10 per AMA H-07)*; [`DC-OR-CASE-v1`](../../data/synthetic/schema/dc-or-case-v1.schema.json) *(drafted 2026-07-02, RB-10)* | Deferred to Sprint 10/11 (OR-status feed) | New entity in MVO; the OR steering anchor per AMA F-A-06. |
| `hcp:Room` | `Room` | *(no contract yet — inferred from `dim_ward_capacityunit`)* | Deferred to Sprint 10/11 (`DC-ROOM-STATE-v1`) | Ontological placement pending Phase 3 (`omrse` facility part-of alignment). |
| `hcp:StaffShift` | `StaffShift` *(deferred)* | Future `DC-STAFF-ROSTER-v1` + `DC-STAFF-DEMAND-v1` per AMA §5.3 | Deferred to Sprint 10/11 | Not in Sprint 09 MVO — reserved slot only. |
| `hcp:Device` | `Device` *(deferred)* | Future `DC-DEVICE-STATE-v1` per AMA §5.4 | Deferred to Sprint 10/11 (monitoring-device feed) | Not in Sprint 09 MVO — reserved slot only. |

### Reference-layer relations mapped to Fabric IQ relationships

| Reference relation | Fabric IQ relationship type | Notes |
| --- | --- | --- |
| `hcp:isPartOf` (Bed ⊑ Room ⊑ Ward ⊑ Hospital) | `is_part_of` | Compositional; MVO uses ward→hospital hierarchy from `dim_hospital` / `dim_ward_capacityunit`. |
| `hcp:hasState` (CapacityUnit → CapacityState) | `has_state` | Bound to time-series data via the eventhouse binding (Sprint 09: bed-state only). |

### Facility hierarchy (reused from AMA §11.2)

| MVO entity type | Reference-layer class | Data contract |
| --- | --- | --- |
| `Hospital` | *(from OOSTT — organisational structure, not yet subclassed under `hcp:`)* | `DC-MASTER-01` (`dim_hospital`) |
| `Specialty` | *(from OMRSE — role/function, not yet subclassed)* | `DC-MASTER-02` (`dim_specialty`) |
| `HospitalService` | *(from OMRSE / OOSTT)* | `DC-MASTER-03` (`dim_hospital_service`) |
| `Ward` | *(pending Phase 3 placement under omrse:hospital-part-of)* | `DC-MASTER-07` (`dim_ward_capacityunit` — ward rollup) |
| `Encounter` | *(from OGMS — clinical-encounter class)* | `DC-DEMAND-ENCOUNTER-v1` |
| `Patient` role | *(from OGMS — patient role class)* | *(attached to `Encounter`; pseudonymised)* |
| `CareTeam` | *(KTH pattern — object aggregate of health workers)* | *(new; deferred to Sprint 10)* |
| `Equipment` | `hcp:Device` *(same subtype as MVO device)* | *(from `dim_device` extension in AMA §5.4)* |

## Reference-layer-exempt entities

None yet. Future PRs adding an operational-layer entity without a reference-layer class MUST list it here with a justification (per FR-GOV-ONT-003 escape hatch).

## Governance

- **Add rule.** A new row is added on any PR that introduces a new reference-layer class or a new Fabric IQ entity type. Both PR author and semantic / ontology owner must approve.
- **Modify rule.** Any change to the *class*, *entity type*, *contract* or *binding* columns is a semantic change per [FR-GOV-ONT-002](../PRD.md#h-semantic-ontology) — follow the change workflow.
- **Deprecation.** Rows are not deleted — they are annotated with `deprecated-YYYY-MM-DD` in the Notes column, and both `reference-layer.ttl` and the operational layer must retain the class/entity for one release cycle.
- **CI check (RB-08 follow-up).** Will parse this file to enumerate `(reference, operational, contract)` triples and fail on:
  - Reference class not present in [reference-layer.ttl](reference-layer.ttl).
  - Operational entity present in Fabric IQ but not in this file (or not annotated `reference-layer-exempt`).
  - Contract ID not present in [`docs/DATA.md`](../DATA.md) (or annotated `contract-pending-YYYY-Q<N>` for planned).

## Sources

- [ADR-0014 §1 — Two-layer ontology, one intent](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#1-two-layer-ontology-one-intent)
- [ADR-0014 §4 — Governance model (OBO-inspired)](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#4-governance-model-obo-inspired)
- [AMA §11.2 — MVO scope for Sprint 09](../reviews/2026-07-01-ama-hcc-northstar-review.md#112-mvo-scope-for-sprint-09-proposed)
- [PRD §H — Semantic Ontology](../PRD.md#h-semantic-ontology)
- [OPERATIONS.md — Semantic / Ontology Owner](../OPERATIONS.md#semantic--ontology-owner-new-role-per-adr-0014)
