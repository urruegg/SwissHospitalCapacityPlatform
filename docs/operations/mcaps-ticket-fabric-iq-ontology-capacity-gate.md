# Service Ticket — MCAPS: Fabric IQ Ontology creation blocked on PROD capacity

| Field | Value |
| ----- | ----- |
| **Version** | 1.1.0 |
| **Date** | 2026-07-24 |
| **Author** | Urs Rüegg |
| **Status** | Ready to submit |
| **Previous Version** | 1.0.0 (new westus2 PROD capacity-gate ticket) |

> **Purpose:** Submit-ready **MCAPS product support** ticket reporting that
> Microsoft Fabric refuses to create a **Fabric IQ `Ontology`** item on the
> rebuilt Switzerland North F2 PROD capacity (`fabricihzhhpfprod`), while the
> existing SIT F2 control (`fabricihzhhpfsit`) succeeds. Copy the *Ticket fields*
> block into the support form; the sections below are the evidence, the
> hypothesis, the exact ask, and the ready-to-run resolution once the gate is
> lifted. Tracked in GitHub issue **#270**.

---

## 1. Ticket fields (copy/paste into the support request)

| Field | Value |
| ----- | ----- |
| **Product / workload** | Microsoft Fabric — Fabric IQ / Ontology (Preview) |
| **Request type** | Product support — feature availability / capacity configuration |
| **Severity** | C — demo / proof-of-technology, synthetic data only, no PHI |
| **Tenant** | `MngEnvMCAP164444.onmicrosoft.com` (`1337187a-4c41-4da9-8fca-731bba7a4329`) |
| **Subscription** | `66a9953a-df37-4c51-856c-9971b9bf3e03` |
| **Region** | switzerlandnorth |
| **Failing capacity** | `fabricihzhhpfprod` — capacityId `59f0cacf-0516-4b19-bbb0-e760f239f4fd` (F2) |
| **Failing workspace** | `ws-ihzhhpf-prod-data` — `1c8408f4-6eb7-401f-aee9-77fe4c8a515e` |
| **Working capacity (control)** | `fabricihzhhpfsit` — capacityId `23c32d0d-f5ab-430a-ac3f-97ec985e953f` (F2) |
| **Working workspace (control)** | `ws-ihzhhpf-sit-data` — `f3af9733-9503-4e92-98f9-a901d96f1c87` |
| **Sample failing requestId** | `9b3676c1-cdc7-4b4f-adef-df00e89c12b4` |
| **Error** | `403 FeatureNotAvailable` — "The feature is not available" |
| **Data classification** | Synthetic only, no PHI |
| **Business sponsor** | Swiss Hospital Capacity Platform (Case Study 26) — @urruegg |

---

## 2. Summary

We are building a regulated-healthcare **Fabric IQ (Preview)** demonstrator: a
Medallion lakehouse feeding an operational **ontology**, a **semantic data
model**, and a published **Fabric Data Agent** consumed by upstream **Azure AI
Foundry** agents. The SIT environment is fully built and live. We are bringing
the PROD environment to parity.

Creating the Fabric IQ **`Ontology`** item on the rebuilt Switzerland North
PROD capacity fails with `403 FeatureNotAvailable`, while the same item type
continues to exist on the SIT F2 control workspace. This re-test is allowed by
[ADR-0042](../adr/0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
and is recorded as **availability-blocked (Microsoft-side Preview gate)**, not a
Curavias policy exclusion.

---

## 3. Reproduction

Call (identical for both workspaces):

```http
POST https://api.fabric.microsoft.com/v1/workspaces/{workspaceId}/items
Authorization: Bearer <Fabric AAD token>
Content-Type: application/json

{ "displayName": "ont_hospital_capacity", "type": "Ontology" }
```

Result:

| Workspace | Capacity | HTTP result |
| --------- | -------- | ----------- |
| PROD `1c8408f4-...` | `fabricihzhhpfprod` `59f0cacf-...` | **403 `FeatureNotAvailable`** |
| SIT `f3af9733-...` | `fabricihzhhpfsit` `23c32d0d-...` | **202 Accepted** (ontology created; probe deleted) |

Control probes on the rebuilt Switzerland North PROD capacity were **not**
re-run on 2026-07-24; only the `Ontology` gate was probed to avoid unnecessary
PROD item mutation. Earlier westus2 PROD probes showed `DataAgent` and
`GraphModel` creation was possible there, but those old capacity/workspace IDs
are stale for the current support ask.

---

## 4. What we have ruled out

* **Not capacity state** — the PROD capacity is `Active` (verified via Azure Resource Manager).
* **Not SKU** — the failing PROD capacity is **F2**, matching the SIT control SKU.
* **Not policy exclusion** — ADR-0042 explicitly permits this Preview item type
  for the Switzerland North PROD demo target.
* **Not a REST-only limitation** — the same item type exists in the SIT control
  workspace and the REST call previously succeeded there.

The remaining explanation is a Microsoft-side **per-region, per-capacity, or
delegated tenant preview availability gate** for Fabric IQ **Ontology** items on
the rebuilt PROD capacity `fabricihzhhpfprod` in Switzerland North.

---

## 5. The ask

1. Identify the **tenant setting, delegated capacity setting, or preview
   enrolment** that controls Fabric IQ **`Ontology`** item creation.
2. Explain **how to enable it on capacity `fabricihzhhpfprod`
   (`59f0cacf-0516-4b19-bbb0-e760f239f4fd`) in Switzerland North** so it matches `fabricihzhhpfsit`.
3. Confirm whether the setting is self-serviceable by a **Fabric Administrator /
   capacity admin**, or requires a backend/preview allow-list action.

---

## 6. Resolution path once the gate is lifted (no manual modelling needed)

The ontology can be replicated SIT → PROD entirely via REST because the SIT
ontology `getDefinition` round-trips cleanly:

1. `getDefinition` on SIT ontology `265c18d1-234e-436c-8297-0ca0a3e3b789`
   (10 EntityTypes + 11 RelationshipTypes + 10 DataBindings).
2. Swap only each DataBinding `sourceTableProperties`: `workspaceId`
   `f3af9733-9503-4e92-98f9-a901d96f1c87` →
   `1c8408f4-6eb7-401f-aee9-77fe4c8a515e` and lakehouse `itemId`
   `30594c20-46ba-40ea-91fa-4701b105e0b9` →
   `57bd6e02-5248-439c-9f31-16bf9ee83cb4` (schema `gold` and all table / entity /
   relationship / property identifiers are preserved verbatim).
3. `POST /items` with `type: Ontology` and the transformed definition
   (next run must validate 0 residual SIT identifiers after the new Switzerland
   North transform).
4. Create and publish `da_hospital_capacity` on PROD grounded on the semantic
   model and ontology, then endorse the PROD semantic model (Promote and
   Approve-for-Copilot).

---

## 7. Scope and guardrails

* **Environment:** Switzerland North demo / proof-of-technology PROD target;
  **synthetic data only, no PHI**. Fabric IQ `Ontology` and `DataAgent` remain
  Preview and are attempted under
  [ADR-0042](../adr/0042-prod-switzerland-north-ga-target-standing-preview-exception.md).
* **Least privilege:** the request is limited to enabling one preview item type on
  one named capacity; no tenant-wide privilege change is required for this ticket.
* **No production data at risk:** the PROD workspace here is a demo PROD tier, not
  a patient-data production system.

---

## 8. 2026-07-24 — Re-test on switzerlandnorth rebuild

The Sprint 19 rebuild created a new PROD Fabric target in Switzerland North. The
old westus2 PROD workspace and capacity IDs from the initial issue are stale for
current remediation.

| Field | Value |
| ----- | ----- |
| **Probe time** | 2026-07-24 |
| **Workspace** | `ws-ihzhhpf-prod-data` — `1c8408f4-6eb7-401f-aee9-77fe4c8a515e` |
| **Capacity** | `fabricihzhhpfprod` — capacityId `59f0cacf-0516-4b19-bbb0-e760f239f4fd` (F2) |
| **Capacity region** | Switzerland North (`switzerlandnorth`) |
| **Lakehouse target** | `lh_ihzhhpf_prod` — `57bd6e02-5248-439c-9f31-16bf9ee83cb4`, schema `gold` |
| **Probe request** | `POST /v1/workspaces/1c8408f4-6eb7-401f-aee9-77fe4c8a515e/items` with `{ "displayName": "ont_gate_probe", "type": "Ontology" }` |
| **HTTP result** | **403 `FeatureNotAvailable`** |
| **requestId** | `9b3676c1-cdc7-4b4f-adef-df00e89c12b4` |
| **Response body** | `{ "requestId": "9b3676c1-cdc7-4b4f-adef-df00e89c12b4", "errorCode": "FeatureNotAvailable", "message": "The feature is not available", "isRetriable": false }` |

Outcome: the Fabric IQ `Ontology` gate still blocks the rebuilt Switzerland
North PROD capacity. Under ADR-0042 this is **availability-blocked
(Microsoft-side Preview gate)**, not a Curavias policy exclusion. The SIT
ontology and data agent remain read-only controls; no SIT mutation was performed.

---

## 9. References

* GitHub issue **#270** — PROD Fabric IQ ontology capacity gate (tracking).
* Sprint 19 (**#239**) — Full PROD deployment in eastus2 (Fabric placed in westus2).
* Sprint 21 (**#247**) — Fabric ingestion, ontology, semantic model.
* Related access ticket — `access-request-fabric-administrator.md` (Fabric
  Administrator role for the tenant-scoped **Domain / Data Product** governance
  lane; distinct from this capacity feature-gate issue).
