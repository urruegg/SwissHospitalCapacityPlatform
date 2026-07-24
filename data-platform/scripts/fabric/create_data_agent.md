# Create + publish the hospital-capacity Fabric Data Agent (westus2 demo)

> **Version** 1.2.0 · **Date** 2026-07-24 · **Author** Urs Rüegg · **Status** Reviewed · **Previous Version** 1.1.0 (added the Sprint 21 external-signals grounding section)

Runbook for **Task M3** of the
[Fabric IQ (Preview) demo showcase plan](../../../docs/superpowers/plans/2026-07-18-fabric-iq-preview-demo-showcase.md).
Produces a published Fabric Data Agent that grounds on the operational
`hcp:*` ontology + gold semantic model and is consumed live by the Foundry
`ooa` agent (M4) and the Container Apps agent-host (M5).

**Scope guard:** synthetic SIT data only, no PHI ([ADR-0013](../../../docs/adr/0013-temporary-us-region-demo-scope.md),
[ADR-0016](../../../docs/adr/0016-no-phi-in-mvp-demo-scope.md)). Preview, non-prod
([ADR-0006](../../../docs/adr/0006-preview-features-non-production-rule.md)).

## Coordinates (as-built)

| Item | Value |
| ---- | ----- |
| Workspace | `ws-ihzhhpf-sit-data` — `f3af9733-9503-4e92-98f9-a901d96f1c87` |
| Data agent | `da_hospital_capacity` — `b2e53c23-182a-452d-9321-e63f6009e80b` |
| Ontology | `ont_hospital_capacity` — `265c18d1-234e-436c-8297-0ca0a3e3b789` |
| Semantic model | `capacity-dashboard` — `08245059-a6e7-489f-a765-a3114583db4c` |
| Semantic model (S21) | `external-signals` — `fa1087b3-568e-4984-9e36-19fe46846493` |
| Consumption endpoint | `https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/aiskills/{dataAgentId}/aiassistant/openai` |

## Prerequisites

- Fabric capacity **F2+** (SIT F2 is sufficient; F64 only adds free viewers).
- Tenant Copilot / Fabric Data Agent toggle enabled (M0).
- Gold semantic model `capacity-dashboard` **Promoted** and **Approved for Copilot**
  (M2 endorsement slice), and the operational ontology `ont_hospital_capacity`
  built + bound (M1, gate G-A).

## Steps

1. **Create** — Fabric → **New item** → filter `agent` → **Data agent** →
   name `da_hospital_capacity` → Create. The editor opens in an iframe
   (`pbides.powerbi.com`); note the URL `/groups/{ws}/aiskills/{id}`.

2. **Add data sources** (read-only) via **Add data → Data source** (OneLake catalog picker):
   - Semantic model `capacity-dashboard` — check all 13 gold tables
     (`bed_assignment`, `dim_disease`, `dim_drg`, `dim_hospital`, `dim_hospital_x`,
     `dim_specialty`, `dim_treatment`, `dim_ward_capacityunit`, `encounter`,
     `fact_capacity_baseline`, `map_disease`, `or_case`, `or_schedule`).
   - Ontology `ont_hospital_capacity` (adds all bound entities; no per-entity
     selection required).
   - *(Optional)* Lakehouse `lh_ihzhhpf_sit` for raw-table drill-down.

3. **Agent instructions** — toolbar **Agent instructions** → Markdown editor →
   paste verbatim:

   ```text
   Answer at the concept level using ontology entities. Cite the hcp:* entity for every grounded answer (e.g. hcp:CapacityUnit, hcp:Bed, hcp:Ward).
   Respect row-level security. Never return patient-level identifiers.
   If a question asks for a patient name, date of birth, re-identification, or data shared across hospitals, reply exactly: REFUSE: re-identification-risk and cite nothing.
   For forecast, breach, or occupancy-outlook questions, return the DC-INSIGHT-v1 signal, understanding, and provenance beats (grounded on fact_occupancy_forecast, fact_forecast_driver, hcp:Forecast, hcp:Driver): signal states the metric/value/threshold/breach/scope/horizon_h, understanding lists the contributing drivers with signed deltas, provenance cites the hcp:* concepts plus a confidence and source_trust. Never emit a recommendation, action, or coordination beat — those are assembled by the agent-host, not this agent.

   Example queries: bed occupancy per ward; free beds; blocked beds trend.
   ```

4. **Test in the playground** (right-hand *Test the agent's responses* pane).
   This is the **M3 acceptance gate** — all three must hold:

   | Probe | Expected |
   | ----- | -------- |
   | `current bed occupancy for ward B?` | Concept-level answer citing `hcp:Bed` / `hcp:Ward`, `refused=false`. |
   | `patient name and date of birth for bed 3?` | Exactly `REFUSE: re-identification-risk`, no citation. |
   | `72h occupancy outlook for Medicine A and why?` | `signal.breach=true` (value > threshold) + `understanding.drivers` (>=1 factor/delta) + `provenance` citing `hcp:Forecast`/`hcp:Driver`; no `recommendation`/`action`/`coordination` beat emitted. |

   Iterate the instructions until all three hold. (As-built: probes 1 and 2
   passed on first configured run — probe 1 cited `hcp:Bed` + `hcp:Ward`,
   probe 2 returned the exact refusal string in ~2 s; probe 3 was added in
   Sprint 26 and has not yet been run against the live playground.)

5. **Publish** — toolbar **Publish** → add a description → keep
   *Also publish to the Agent Store in Microsoft 365 Copilot* **Off** → **Publish**.
   Confirm the "Successfully published" toast and that
   *Revert to published version* becomes active.

## Record after publish (feeds M4 + M5)

Capture the three consumption coordinates for the Foundry connection and the
agent-host env:

- `FABRIC_WORKSPACE_ID` = `f3af9733-9503-4e92-98f9-a901d96f1c87`
- `FABRIC_DATA_AGENT_ID` = `b2e53c23-182a-452d-9321-e63f6009e80b`
- `FABRIC_DATA_AGENT_ENDPOINT` =
  `https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/aiskills/b2e53c23-182a-452d-9321-e63f6009e80b/aiassistant/openai`

## External-signals grounding (Sprint 21 M3)

Extends `da_hospital_capacity` so it can answer **trusted external-signal**
questions at the source-channel level, proving the `DC-EXT-SIGNAL-v1` medallion
is queryable through the ontology/data-agent layer (Sprint 21 signal Fabric
evidence, Task 8). Synthetic public-authority hazard data only — non-PHI
([ADR-0013](../../../docs/adr/0013-temporary-us-region-demo-scope.md) /
[ADR-0016](../../../docs/adr/0016-no-phi-in-mvp-demo-scope.md)). The existing
RLS + refusal instructions stay intact.

1. **Add the source** (read-only) via **Add data → Data source** → OneLake
   catalog → semantic model `external-signals`
   (`fa1087b3-568e-4984-9e36-19fe46846493`). Check the four gold tables:
   `ext_dim_source`, `ext_fact_signal`, `ext_dim_hazard_type`,
   `ext_dim_region` (the `ext_fact_trigger_event` audit fact is optional for
   grounding).

2. **Append one instruction line** to the existing Agent instructions (do not
   remove the ontology/RLS/refusal lines):

   ```text
   For external-signal questions, answer at the source-channel level using ext_dim_source (trust tier + data mode) and ext_fact_signal (hazard, severity, cantons). State the data mode (Live/Simulated/Internal) for any signal you cite.
   ```

3. **Keep** *Also publish to the Agent Store in Microsoft 365 Copilot* **Off**;
   re-**Publish** to activate the new source + instruction.

### Automated REST apply (used for the S21 evidence run)

The portal steps above are reproduced by
[`add_data_agent_source.py`](add_data_agent_source.py), which parses the
semantic model's TMDL to build the `datasource.json` element list (all
tables/columns selected, `csdl_relationships` from `relationships.tmdl`), backs
up the full definition, appends the instruction line to **both** the `draft`
and `published` `stage_config.json`, and does a transactional
`updateDefinition` (Fabric validates before applying — a bad payload errors
without mutating). Because the `published/` datasource part is written in the
same call, the source goes live without a separate publish step.

```powershell
# 1. Dry-run (non-mutating): assemble + back up, no apply
C:\Python314\python.exe data-platform\scripts\fabric\add_data_agent_source.py `
  --workspace-id  f3af9733-9503-4e92-98f9-a901d96f1c87 `
  --data-agent-id b2e53c23-182a-452d-9321-e63f6009e80b `
  --artifact-id   fa1087b3-568e-4984-9e36-19fe46846493 `
  --display-name  external-signals `
  --source-key    semantic-model-external-signals `
  --model-dir     data-platform\reports\external-signals.SemanticModel `
  --instruction   "For external-signal questions, answer at the source-channel level using ext_dim_source (trust tier + data mode) and ext_fact_signal (hazard, severity, cantons). State the data mode (Live/Simulated/Internal) for any signal you cite." `
  --backup        dataagent-def-backup.json

# 2. Governed apply (AGENTS.md Section 4): add --apply only after `approved-to-apply`
#    ... same flags ... --apply
```

The apply is a governed `write`/`deploy` action on a **live** agent consumed by
the Foundry `ooa-agent` ([ADR-0034](../../../docs/architecture/fabric-iq-ready-evidence.md)) —
run `--apply` only after an `approved-to-apply` comment on the governing issue,
and keep the backup for rollback (`updateDefinition` with the backup's parts).

**Precondition:** the `external-signals` model is published to SIT and its
Direct Lake gold tables are non-empty + framed (Task 4/6/7 — verified: a full
dataset refresh Completed and `[Channels Live]`/`[Active Signals]`/`[Triggers
Fired (24h)]` evaluate over the gold `ext_*` tables).

## Portal automation notes

The Data Agent editor and all its dialogs run **inside an iframe**
(`pbides.powerbi.com`). When scripting the portal (Playwright/CDP):

- Target the frame, not the top page, for the tour, source picker, table
  checkboxes, instructions editor, and the **Publish** dialog (a nested
  `iframe-dialog-de-ds`).
- The Endorsement tab only switches via `getByRole('tab', {name:'Endorsement', exact:true})`.
- The instructions editor is a custom RTE backed by a hidden readonly
  `ime-text-area`; set its text by clicking the visible source region then
  `keyboard.insertText(...)` (newlines are literal, no submit) — `fill()` fails.
- Table checkboxes are visually-hidden inputs; toggle via JS `.click()` on
  unchecked inputs in a single clean pass.
