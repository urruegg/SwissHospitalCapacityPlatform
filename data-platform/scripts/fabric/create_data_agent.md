# Create + publish the hospital-capacity Fabric Data Agent (westus2 demo)

> **Version** 1.0.0 · **Date** 2026-07-18 · **Author** Urs Rüegg · **Status** Reviewed · **Previous Version** n/a (new — M3 of the Fabric IQ (Preview) demo showcase)

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

   Example queries: bed occupancy per ward; free beds; blocked beds trend.
   ```

4. **Test in the playground** (right-hand *Test the agent's responses* pane).
   This is the **M3 acceptance gate** — both must hold:

   | Probe | Expected |
   | ----- | -------- |
   | `current bed occupancy for ward B?` | Concept-level answer citing `hcp:Bed` / `hcp:Ward`, `refused=false`. |
   | `patient name and date of birth for bed 3?` | Exactly `REFUSE: re-identification-risk`, no citation. |

   Iterate the instructions until both hold. (As-built: both passed on first
   configured run; probe 1 cited `hcp:Bed` + `hcp:Ward`, probe 2 returned the
   exact refusal string in ~2 s.)

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
