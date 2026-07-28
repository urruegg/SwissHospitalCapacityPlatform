# Ontology Crosswalk — Reference Layer ↔ Fabric IQ Operational Layer ↔ Data Contract

| Field | Value |
| ----- | ----- |
| **Version** | 0.8.0 |
| **Date** | 2026-07-27 |
| **Author** | Urs Rüegg |
| **Status** | Draft — Sprint 09 skeleton (RB-11); Sprint 23 org-spine + skills rows (#255); Sprint 26 WS-A Foresight tier + WS-B `hcp:Barrier` + WS-C `hcp:Recommendation`/`hcp:Lever` (#335); Sprint 32 certification/competency block (#454) |
| **Previous Version** | 0.7.0 (Sprint 26 WS-C prescriptive terms) |
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
| `hcp:Bed` | `Bed` | `DC-MASTER-07` *(dim_ward_capacityunit — bed rollup, Sprint 9 baseline)*; future DC-BED-STATE-v1 for the eventhouse feed | **`bed-state` (eventhouse, first target)** — occupied / available / blocked / cleaning per [ADR-0014 §3](../adr/0014-fabric-iq-ontology-target-backbone-ga-gated.md#3-sprint-09-delivers-the-minimum-viable-ontology-mvo) | Sprint 09 delivers this first (MVO gate G-A). |
| `hcp:ORSlot` | `ORSlot` | [`DC-OR-SCHEDULE-v1`](../../data/synthetic/schema/dc-or-schedule-v1.schema.json) *(drafted 2026-07-02, RB-10; ingestion in Sprint 10 per AMA H-07)*; [`DC-OR-CASE-v1`](../../data/synthetic/schema/dc-or-case-v1.schema.json) *(drafted 2026-07-02, RB-10)* | Deferred to Sprint 10/11 (OR-status feed) | New entity in MVO; the OR steering anchor per AMA F-A-06. |
| `hcp:Room` | `Room` | *(no contract yet — inferred from `dim_ward_capacityunit`)* | Deferred to Sprint 10/11 (DC-ROOM-STATE-v1) | Ontological placement pending Phase 3 (`omrse` facility part-of alignment). |
| `hcp:StaffShift` | `StaffShift` *(deferred)* | Future DC-STAFF-ROSTER-v1 + DC-STAFF-DEMAND-v1 per AMA §5.3 | Deferred to Sprint 10/11 | Not in Sprint 09 MVO — reserved slot only. |
| `hcp:Device` | `Device` *(deferred)* | Future DC-DEVICE-STATE-v1 per AMA §5.4 | Deferred to Sprint 10/11 (monitoring-device feed) | Not in Sprint 09 MVO — reserved slot only. |
| `hcp:Encounter` | `Encounter` | **[`DC-DEMAND-ENCOUNTER-v1`](../../data/synthetic/schema/dc-demand-encounter-v1.schema.json)** *(existing — reuse)* | Time-series binding on Encounter timeline (status transitions) | AMA SD Core Solution Pattern control unit; stub class added in T1.3 code-review fix. |
| `hcp:Specialty` | `Specialty` | `DC-MASTER-02` *(dim_specialty; no `.schema.json` file yet — see [Reference-layer-exempt entities](#reference-layer-exempt-entities))* | N/A (static reference) | Grounds MVO facility hierarchy per design spec §3.3; stub class added in T1.3 code-review fix. |
| `hcp:BedAssignment` | `BedAssignment` | **[`DC-MATCH-RECOMMENDATION-v1`](../../data/synthetic/schema/dc-match-recommendation-v1.schema.json)** *(existing — reuse)* | Time-series binding on assign/unassign events (eventhouse) | Matches AMA SD Core Solution Pattern; links Encounter ↔ Bed. |
| `hcp:DischargeReadinessScore` | `DischargeReadinessScore` | **new** `DC-DISCHARGE-SCORE-v1` *(T1.5)* | Time-series binding on Encounter timeline (hourly refresh) | Grounds `FR-DC-001`, `FR-DC-006`. |
| `hcp:DischargeRecommendation` | `DischargeRecommendation` | **new** `DC-DISCHARGE-RECOMMENDATION-v1` *(T1.5)* | Deferred | Grounds `FR-DC-002`, `FR-DC-003`, `FR-DC-005`. |
| `hcp:ForecastOutput` | `ForecastOutput` | **new** `DC-DEMAND-FORECAST-v1` *(T1.5)* | Time-series binding (hourly refresh per `NFR-PERF-002`) | Grounds `FR-FC-001..006`. |
| `hcp:TrustedSource` | `TrustedSource` *(GA-gated per ADR-0014)* | `DC-EXT-SIGNAL-v1` (`sourceId`, `sourceAuthority`, `trustTier`) | Static dimension (`gold.ext_dim_source`) | Grounds `FR-EXT-ONT-001`; Fabric IQ operational binding deferred per `NFR-EXT-ONT-001`. |
| `hcp:HazardType` | `HazardType` *(GA-gated per ADR-0014)* | `DC-EXT-SIGNAL-v1` (`hazardType`, severity / danger-level attributes) | Static dimension (`gold.ext_dim_hazard_type`) | Grounds hazard taxonomy for trusted external signals; operational binding deferred per `NFR-EXT-ONT-001`. |
| `hcp:ExternalSignal` | `ExternalSignal` *(GA-gated per ADR-0014)* | `DC-EXT-SIGNAL-v1` | **Dual: silver/gold Delta + Eventhouse** (`silver.ext_signal`, `gold.ext_fact_signal`, hot Eventhouse stream) | CAP-aligned authority signal; advisory trigger input only. |
| `hcp:HazardEvent` | `HazardEvent` *(GA-gated per ADR-0014)* | Derived from `DC-EXT-SIGNAL-v1` dedup key | Time-series trigger event (`gold.ext_fact_trigger_event`) | Deduplicated event-level object handed to CSA; records provenance and trigger audit. |
| `hcp:TriggerRule` | `TriggerRule` *(GA-gated per ADR-0014)* | `trigger_rules.yaml` derived from `DC-EXT-SIGNAL-v1` fields | Static rule set | Maps qualifying signals to `ScenarioTemplate` + `LageTier`; bridge/Activator execution remains advisory and HITL. |
| `hcp:AffectedRegion` | *(reuse Location; GA-gated operational region binding)* | `DC-EXT-SIGNAL-v1` (`region.cantons`, `region.nuts`, `region.geoPolygon`) | Region dimension (`gold.ext_dim_region`) | Reuses Location semantics for canton/NUTS/polygon targeting; operational binding deferred per `NFR-EXT-ONT-001`. |
| `hcp:Ward` | `Ward` | `DC-MASTER-07` *(dim_ward_capacityunit — ward rollup)* | Static reference (bed rollup) | Sprint 26 WS-A range target for `hcp:forWard`; full `omrse:hospital-part-of` placement is Phase 3. |
| `hcp:Forecast` | `Forecast` | **[`DC-OCCUPANCY-FORECAST-v1`](../../data/synthetic/schema/dc-occupancy-forecast-v1.schema.json)** *(Sprint 26 WS-A)* | Batch Gold Delta (`gold.fact_occupancy_forecast`) — deterministic synthetic, hourly horizons 0..72h | 72h occupancy forecast per ward; distinct from `hcp:ForecastOutput` (specialty demand). Deterministic generator with a real-model seam (design D2). |
| `hcp:Driver` | `Driver` | **[`DC-FORECAST-DRIVER-v1`](../../data/synthetic/schema/dc-forecast-driver-v1.schema.json)** *(Sprint 26 WS-A)* | Batch Gold Delta (`gold.fact_forecast_driver`) | Forecast decomposition ('why'); deltas reconcile to the net forecast change. Grounds beat 2 of the actionable-insight pattern. |
| `hcp:Barrier` | `Barrier` | **[`DC-DISCHARGE-BARRIER-v1`](../../data/synthetic/schema/dc-discharge-barrier-v1.schema.json)** *(Sprint 26 WS-B)* | Batch Gold Delta (`gold.fact_discharge_barrier`) — deterministic collapse of discharge-blocked candidates, ranked | Systemic discharge barrier (DCA 'N candidates → M barriers'); aggregate over opaque candidate keys + ward IDs (no PHI). Grounds beat 3 of the actionable-insight pattern. |
| `hcp:Recommendation` | `Recommendation` | **[`DC-INSIGHT-v1`](../../data/synthetic/schema/dc-insight-v1.schema.json)** *(Sprint 26 WS-C)* | Runtime tuple — the agent-host assembles the recommendation beat; no batch Gold binding | Ranked, owner-attributed lever recommendations carrying a **deterministic** `expected_impact` (never an LLM estimate; design D2/D4). Advisory/HITL only. Superclass of `hcp:DischargeRecommendation`. Grounds beat 4 (the actionable recommendation) of the actionable-insight pattern. |
| `hcp:Lever` | `Lever` *(git-owned catalog; no operational binding)* | *(no data contract — git-owned lever catalog `data-platform/decision/levers/<role>.yaml`, validated by [`lever.schema.json`](../../data-platform/decision/levers/lever.schema.json))* | N/A (config artefact, versioned in git) | Typed recommendation template dispatched by `lever_id` from the insight recommendation beat; carries preconditions, `params_schema`, `impact_formula_ref`, `owner_role` and `hitl=true`. |
| `hcp:Tenant` | `Tenant` *(folded 1:1 into Hospital)* | `DC-SUPPLY-ORGANIZATION-v1` | N/A (static reference; `gold.dim_hospital` re-branded to tenant, PR #332) | Sprint 23 T6/D6: CuraNova / Curalp / Vialta; `tenant_id = hospital_id`. Drops H_HSL (no tenant). |
| `hcp:OrgUnit` | `OrgUnit` | `DC-SUPPLY-ORGANIZATION-v1` | N/A (static reference; `gold.dim_org_unit`) | Sprint 23 T6; site / org-unit level under a Tenant. |
| `hcp:Department` | `Department` | `DC-SUPPLY-ORGANIZATION-v1` | N/A (static reference; `gold.dim_department`) | Sprint 23 T6; the demand / gap grain for skills. |
| `hcp:CareSetting` | `CareSetting` | `gold.dim_care_setting` *(contract-pending-2026-Q3)* | N/A (static reference; 2 rows: `bed` / `ops`) | Sprint 23 T14: bed = nursing, ops = doctors + specialised; splits demand / gap answers. |
| `hcp:Skill` | `Skill` | `gold.dim_skill` *(contract-pending-2026-Q3)*; referenced by `DC-SKILL-EVIDENCE-v1` | N/A (static reference; ESCO-aligned) | Sprint 23 T7; 66 skills across nursing + ops care settings. |
| `hcp:OccupationRole` | `OccupationRole` | `gold.dim_occupation_role` *(contract-pending-2026-Q3)* | N/A (static reference; ISCO-08 aligned) | Sprint 23 T7; occupation held by a HealthWorker. |
| `hcp:HealthWorker` | `HealthWorker` | `gold.dim_employee` (GLN key) *(contract-pending-2026-Q3)* | N/A (static reference; no PHI in binding) | Sprint 23 T7; GLN golden-thread identity (mod-10 validated at silver). |
| `hcp:Credential` | `Credential` | [`DC-REF-CERTIFICATION-v1`](../../data/synthetic/schema/dc-ref-certification-v1.schema.json) | *(GA-gated; deferred)* | Sprint 32 (#454); staff-PII, pseudonymised work-ID; feeds skills baseline. |
| `hcp:Certification` | `Certification` | [`DC-REF-CERTIFICATION-v1`](../../data/synthetic/schema/dc-ref-certification-v1.schema.json) | *(GA-gated; deferred)* | Sprint 32 (#454); subtype of Credential. |
| `hcp:Qualification` | `Qualification` | [`DC-REF-CERTIFICATION-v1`](../../data/synthetic/schema/dc-ref-certification-v1.schema.json) | *(GA-gated; deferred)* | Sprint 32 (#454); subtype of Credential (e.g. FMH title). |
| `hcp:Competency` | `Competency` | *(no data contract — derived competency codes)* | *(GA-gated; deferred)* | Sprint 32 (#454); certified by a Credential; qualifies staffing of a CapacityUnit; relates to hcp:Skill tags. |
| `hcp:IssuingAuthority` | `IssuingAuthority` | *(no data contract — reference dimension)* | N/A | Sprint 32 (#454); issues Credentials (NAREG / FMH). |
| `hcp:SkillAssertion` | `SkillAssertion` | `DC-SKILL-EVIDENCE-v1`; `gold.fact_skill_assertion` | Deferred to WS-B4 live gold run (assertion validity windows) | Sprint 23 T7; carries proficiency (1..5) + assurance (L0..L4). No-PII TMDL surface (PR #339). |
| `hcp:SkillDemand` | `SkillDemand` | `gold.fact_skill_demand` *(contract-pending-2026-Q3)* | Deferred to WS-B4 live gold run | Sprint 23 T7/T14; min proficiency + min assurance per Department + CareSetting. |
| `hcp:SkillGap` | `SkillGap` | `gold.fact_skill_gap` *(contract-pending-2026-Q3)* | Deferred to WS-B4 live gold run | Sprint 23 T14; demand − assurance-valid supply; grounds the gap measures (PR #339). |
| `hcp:WorkerUnitEligibility` | `WorkerUnitEligibility` | `gold.bridge_worker_unit_eligibility` *(contract-pending-2026-Q3)* | Deferred to WS-B4 live gold run | Sprint 23 T7; pre-computed assurance-gated can-staff bridge. No-PII TMDL surface (PR #339). |
| `hcp:RoleSkillTemplate` | `RoleSkillTemplate` | `gold.bridge_role_skill_demand_template` *(contract-pending-2026-Q3)* | N/A (static reference) | Sprint 23 T7; occupation → required-skills template driving demand + eligibility. |

### Reference-layer relations mapped to Fabric IQ relationships

| Reference relation | Fabric IQ relationship type | Notes |
| --- | --- | --- |
| `hcp:isPartOf` (Bed ⊑ Room ⊑ Ward ⊑ Hospital) | `is_part_of` | Compositional; MVO uses ward→hospital hierarchy from `dim_hospital` / `dim_ward_capacityunit`. |
| `hcp:hasState` (CapacityUnit → CapacityState) | `has_state` | Bound to time-series data via the eventhouse binding (Sprint 09: bed-state only). |
| `hcp:signalFromSource` (ExternalSignal → TrustedSource) | `signal_from_source` *(GA-gated)* | Maps normalized authority signals to source dimension rows from `DC-EXT-SIGNAL-v1`. |
| `hcp:signalIndicatesHazard` (ExternalSignal → HazardType) | `signal_indicates_hazard` *(GA-gated)* | Maps the signal hazard taxonomy to `gold.ext_dim_hazard_type`. |
| `hcp:signalAffectsRegion` (ExternalSignal → AffectedRegion) | `signal_affects_region` *(GA-gated)* | Maps canton/NUTS/polygon region blocks to the governed region dimension. |
| `hcp:triggerRuleMapsScenario` (TriggerRule → ScenarioTemplate) | `trigger_rule_maps_scenario` *(GA-gated)* | Maps trusted-signal rules to CSA scenario templates; advisory only. |
| `hcp:signalPreseeds` (ExternalSignal → LageTier) | `signal_preseeds` *(GA-gated)* | Captures the default Lage-tier pre-seed from the signal contract; CSA remains authoritative. |
| `hcp:forWard` (Forecast → Ward) | `for_ward` | Sprint 26 WS-A; binds `gold.fact_occupancy_forecast` to the ward rollup. |
| `hcp:explainedBy` (Forecast → Driver) | `explained_by` | Sprint 26 WS-A; forecast → decomposition rows in `gold.fact_forecast_driver`. |
| `hcp:evidencedBy` (Driver → ExternalSignal) | `evidenced_by` | Sprint 26 WS-A; links a driver (e.g. seasonality) to the Trust-A signal that evidences it. Advisory only. |
| `hcp:orgUnitOfTenant` (OrgUnit → Tenant) | `org_unit_of_tenant` | Sprint 23 T6 org-spine hierarchy; Tenant is folded 1:1 into the Hospital dimension. |
| `hcp:departmentOfOrgUnit` (Department → OrgUnit) | `department_of_org_unit` | Sprint 23 T6; department is the demand / gap grain. |
| `hcp:hasOccupationRole` (HealthWorker → OccupationRole) | `has_occupation_role` | Sprint 23 T7; ISCO-08 occupation held by a worker. |
| `hcp:holdsCredential` (HealthWorker → Credential) | `holds_credential` | Sprint 32 (#454); links pseudonymised worker records to staff-PII credentials. |
| `hcp:certifiesCompetency` (Credential → Competency) | `certifies_competency` | Sprint 32 (#454); maps verified credentials to derived competency codes. |
| `hcp:qualifiesForUnit` (Competency → CapacityUnit) | `qualifies_for_unit` | Sprint 32 (#454); supports skills-based staffing eligibility for units and tasks. |
| `hcp:issuedByAuthority` (Credential → IssuingAuthority) | `issued_by_authority` | Sprint 32 (#454); records NAREG / FMH or equivalent issuing authority provenance. |
| `hcp:assertsSkill` (SkillAssertion → Skill) | `asserts_skill` | Sprint 23 T7; evidence-backed skill claim with proficiency + assurance. |
| `hcp:assertedByWorker` (SkillAssertion → HealthWorker) | `asserted_by_worker` | Sprint 23 T7; GLN golden-thread link. |
| `hcp:demandsSkill` (SkillDemand → Skill) | `demands_skill` | Sprint 23 T7; required skill at min proficiency + min assurance. |
| `hcp:demandForCareSetting` (SkillDemand → CareSetting) | `demand_for_care_setting` | Sprint 23 T14; splits bed / ops demand. |
| `hcp:gapForCareSetting` (SkillGap → CareSetting) | `gap_for_care_setting` | Sprint 23 T14; splits bed / ops gap answers. |
| `hcp:roleRequiresSkill` (RoleSkillTemplate → Skill) | `role_requires_skill` | Sprint 23 T7; drives demand generation + eligibility. |
| `hcp:eligibleForUnit` (WorkerUnitEligibility → CapacityUnit) | `eligible_for_unit` | Sprint 23 T7; assurance-gated can-staff bridge. |

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

### Base-spec traceability

Anchors every MVO reference-layer class to a base-spec (PRD / AMA SD) requirement per design spec §3.4.

| Base-spec requirement | Ontology anchor |
| --- | --- |
| `FR-DATA-005` (governed semantic model) | Every MVO entity surfaces via semantic model with reference-layer grounding |
| `FR-FC-001` (72h demand forecast) | `hcp:ForecastOutput` |
| `FR-FC-002` (segmented by specialty × time window) | `hcp:ForecastOutput.covers=Specialty, .validFor=TimeWindow` |
| `FR-FC-005` (grounding for BM-Copilot) | `hcp:ForecastOutput` consumed by BM-Copilot |
| `FR-DC-001` (identify near-discharge inpatients) | `hcp:DischargeReadinessScore.appliesTo=Encounter` |
| `FR-DC-002` (ranked candidates + explanatory factors) | `hcp:DischargeRecommendation` with `hcp:hasExplanation` |
| `FR-DC-005` (discharge blockers surfaced) | `hcp:DischargeRecommendation.blockers[]` |
| `FR-CX-001..002` (copilot grounded answers) | Grounded on all above via BM-Copilot + Fabric Data Agent |
| AMA SD "Matching Demand↔Supply" | `hcp:BedAssignment` + `DC-MATCH-RECOMMENDATION-v1` |

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
