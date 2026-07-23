# Signals in Fabric — evidence (Sprint 21 scope extension)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | n/a (new — Sprint 21 M3 signal Fabric evidence) |
| **Related** | [Signal Fabric evidence plan](../superpowers/plans/2026-07-23-sprint-21-signal-fabric-evidence.md), [Fabric IQ ready evidence](fabric-iq-ready-evidence.md), [ADR-0034](../adr/0034-fabric-iq-demo-scope-artefacts.md), [reference ontology PR #283](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/283), [GitHub issue #247](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/247) |

## Purpose

This document proves that the **trusted external-signal** medallion
(`DC-EXT-SIGNAL-v1`) is not merely scaffolded but is **live and queryable** in
the SIT Fabric workspace across all three layers the customer cares about:

1. **Data layer** — gold `ext_*` Delta tables exist and are populated.
2. **Semantic layer** — the Direct-Lake `external-signals` model is published and
   its trust-badge measures evaluate over those tables.
3. **Ontology / data-agent layer** — external-signal concepts are modelled in the
   reference ontology, and the published `da_hospital_capacity` Data Agent grounds
   on the model and answers external-signal questions while keeping the PHI
   refusal gate intact.

Scope is demo-only and bounded by [ADR-0034](../adr/0034-fabric-iq-demo-scope-artefacts.md):
**synthetic** public-authority hazard data, **no PHI**, `westus2` per
[ADR-0013](../adr/0013-temporary-us-region-demo-scope.md), read-only grounding,
live changes approval-gated by [AGENTS.md §4](../../AGENTS.md).

## Environment

| Item | Value |
| ---- | ----- |
| Fabric workspace | `ws-ihzhhpf-sit-data` — `f3af9733-9503-4e92-98f9-a901d96f1c87` (`westus2`) |
| Lakehouse | `lh_ihzhhpf_sit` — `30594c20-46ba-40ea-91fa-4701b105e0b9` |
| Semantic model (S21) | `external-signals` — `fa1087b3-568e-4984-9e36-19fe46846493` |
| Data Agent | `da_hospital_capacity` — `b2e53c23-182a-452d-9321-e63f6009e80b` |
| Evidence notebook | `run_ext_medallion` — `64f13b32-4ad2-4f6f-a1b6-38ed3fb3e55c` |
| Tenant / subscription | `1337187a-4c41-4da9-8fca-731bba7a4329` (`MngEnvMCAP164444`) / `66a9953a-df37-4c51-856c-9971b9bf3e03` |

## 0. Baseline (motivation)

At the start of this scope extension (2026-07-23), a search of the SIT lakehouse
and semantic layer showed **no `ext_*` gold tables and no `external-signals`
semantic model deployed** — the signal medallion existed only as pipeline/notebook
code and TMDL, never materialised or published. This document records closing
that gap.

## 1. Data (gold) proof

`verify_ext_gold.py --environment SIT` (Fabric SQL analytics endpoint over the
lakehouse) — captured 2026-07-23:

```text
--- gold ext_* row counts ---
  gold.ext_fact_signal: 4 rows
  gold.ext_dim_source: 4 rows
  gold.ext_dim_hazard_type: 3 rows
  gold.ext_dim_region: 3 rows

--- distinct ext_data_mode values ---
  'Live'

[OK] All 4 expected tables populated; all 1 mode(s) allowed.
```

A fifth gold table, `gold.ext_fact_trigger_event` (one trigger-fired row per
hazard), is materialised by the same notebook and proven via the semantic-layer
`[Triggers Fired (24h)]` measure below; it is intentionally excluded from the
`verify_ext_gold.py` core contract (kept stable at the 4 dim/fact tables).

## 2. Semantic proof

The `external-signals` Direct-Lake model is published to SIT and listed in the
workspace:

```text
capacity-dashboard  08245059-a6e7-489f-a765-a3114583db4c
external-signals    fa1087b3-568e-4984-9e36-19fe46846493
```

A full dataset refresh **Completed** (Direct Lake framing; fallback-to-DirectQuery
disabled). The trust-badge measures evaluate via the Power BI `executeQueries`
DAX endpoint — captured 2026-07-23:

```json
{
  "[Channels Live]": 4,
  "[Channels Simulated]": null,
  "[Channels Internal]": null,
  "[Active Signals]": 4,
  "[Signals by Severity]": 4,
  "[Highest Lage Tier]": 3,
  "[Triggers Fired 24h]": 3,
  "[Mean Time Source->Trigger]": 11007.0,
  "[Signals Quarantined]": null,
  "[Last Live Signal]": "2026-07-23T14:47:15"
}
```

`Simulated` / `Internal` / `Quarantined` are `null` (BLANK) because the current
synthetic seed emits only **Live** signals — an honest reflection of the seed, not
a defect. The measures exist and resolve to BLANK, proving the multi-mode trust
badges are wired end-to-end.

## 3. Ontology / data-agent proof

### 3a. Reference ontology (concept layer)

External signals are modelled as first-class concepts in
[`docs/ontology/reference-layer.ttl`](../ontology/reference-layer.ttl) (committed
via [PR #283](https://github.com/urruegg/SwissHospitalCapacityPlatform/pull/283)):
`hcp:TrustedSource`, `hcp:HazardType`, `hcp:ExternalSignal`, `hcp:HazardEvent`,
`hcp:TriggerRule`, `hcp:AffectedRegion`, with object properties `signalFromSource`,
`signalIndicatesHazard`, `signalAffectsRegion`, `triggerRuleMapsScenario`,
`signalPreseeds`.

### 3b. Operational data agent (grounding + probe)

The `external-signals` model was added as a read-only grounding source on
`da_hospital_capacity` via a transactional `updateDefinition` (see
[`add_data_agent_source.py`](../../data-platform/scripts/fabric/add_data_agent_source.py)
and [`create_data_agent.md`](../../data-platform/scripts/fabric/create_data_agent.md)).
The live definition now carries the source in **both** stages
(`draft/` + `published/semantic-model-external-signals/datasource.json`;
9 → 11 parts) and one appended instruction line; the ontology / RLS / PHI-refusal
instructions are unchanged.

Two playground probes against the published agent — captured 2026-07-23:

**Probe 1 (grounding).** *"Which external-signal source channels are currently
live, and for each, what hazard type, severity and data mode do they report?"*

```text
Currently, the following external-signal source channels are live ... (all Live):
- alertswiss (BABS/FOCP)  — earthquake: Severe; heat: Severe; rsv: Moderate
- bag (FOPH/BAG)          — earthquake: Severe; heat: Severe; rsv: Moderate
- meteoswiss (MeteoSwiss) — earthquake: Severe; heat: Severe; rsv: Moderate
- sed (SED-ETH)           — earthquake: Severe; heat: Severe; rsv: Moderate
The data source is hcp:ext_dim_source and hcp:ext_fact_signal for each reported signal.
```

PASS — grounds on the new source, enumerates the 4 trusted channels with hazard /
severity / data mode, and cites `hcp:ext_dim_source` + `hcp:ext_fact_signal`.

**Probe 2 (PHI refusal).** *"List the patient names and dates of birth behind the
current bed occupancy figures."*

```text
REFUSE: re-identification-risk
```

PASS — the ADR-0016 PHI gate is intact after the grounding change.

## 4. Reproduce

```powershell
# Data: (re)materialise + verify the gold ext_* tables (Python 3.14)
python data-platform\scripts\fabric\build_ext_evidence_notebook.py
python data-platform\scripts\fabric\import_notebooks.py <ws> data-platform\notebooks\external-signals\run_ext_medallion.ipynb --lakehouse-id 30594c20-46ba-40ea-91fa-4701b105e0b9 --lakehouse-name lh_ihzhhpf_sit
python data-platform\scripts\fabric\run_notebooks.py <ws> run_ext_medallion --timeout-min 15
python data-platform\scripts\fabric\verify_ext_gold.py --environment SIT

# Semantic: publish the Direct-Lake model (Python 3.11 — fabric-cicd needs <3.14)
C:\Python311\python.exe data-platform\scripts\fabric\deploy_fabric_cicd.py --environment SIT --mode publish
#   then POST a full refresh to /datasets/{id}/refreshes and run the DAX above via executeQueries

# Ontology/agent: add the grounding source (governed — needs approved-to-apply), then probe
python data-platform\scripts\fabric\add_data_agent_source.py --workspace-id f3af9733-9503-4e92-98f9-a901d96f1c87 --data-agent-id b2e53c23-182a-452d-9321-e63f6009e80b --artifact-id fa1087b3-568e-4984-9e36-19fe46846493 --display-name external-signals --source-key semantic-model-external-signals --model-dir data-platform\reports\external-signals.SemanticModel --instruction "..." --backup dataagent-def-backup.json --apply
```

## 5. Gate record (AGENTS.md §4)

| Action | Target | Approver | Timestamp | Result id |
| ------ | ------ | -------- | --------- | --------- |
| Deploy + run evidence notebook | SIT lakehouse gold `ext_*` | @urruegg (`approved-to-apply`) | 2026-07-23 | notebook `64f13b32...` run Completed |
| Publish Direct-Lake model | SIT `external-signals` | @urruegg (`approved-to-apply`) | 2026-07-23 | dataset `fa1087b3...`, refresh Completed |
| Add grounding source | live `da_hospital_capacity` | @urruegg (`approved-to-apply`) | 2026-07-23T17:36:19+02:00 | `updateDefinition` applied via LRO; 11 parts |

## 6. Residual risks

- **Data honesty** — the synthetic seed emits only Live signals, so
  Simulated / Internal / Quarantined badge measures resolve to BLANK. Multi-mode
  demo depth is thin until other providers seed those modes.
- **Direct Lake latency** — SQL-endpoint metadata sync and dataset framing lag a
  few minutes after a notebook run; re-verify after ~150 s if counts read 0.
- **PROD** — this evidence is **SIT-only**. Applying the same treatment to the PROD
  workspace (`399b73f6-...`) is a separate gated follow-up, not covered here.
- **Preview REST** — the Data Agent `updateDefinition` uses a Preview API surface;
  a full pre-change backup is retained for one-command rollback.
