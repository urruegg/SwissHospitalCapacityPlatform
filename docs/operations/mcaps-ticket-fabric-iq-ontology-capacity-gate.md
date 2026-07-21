# Service Ticket — MCAPS: Fabric IQ Ontology creation blocked on PROD capacity

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-21 |
| **Author** | Urs Rüegg |
| **Status** | Ready to submit |
| **Previous Version** | n/a (new) |

> **Purpose:** Submit-ready **MCAPS product support** ticket reporting that
> Microsoft Fabric refuses to create a **Fabric IQ `Ontology`** item on one F2
> capacity (`fabricihzhhpfprod`) while an identical F2 capacity in the **same
> tenant and region** (`fabricihzhhpfsit`) succeeds. Copy the *Ticket fields*
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
| **Region** | westus2 |
| **Failing capacity** | `fabricihzhhpfprod` — capacityId `4b690244-a91e-4028-9d0e-6dc2260a3432` (F2) |
| **Failing workspace** | `ws-ihzhhpf-prod-data` — `399b73f6-4b1c-44da-b7f9-1b4a37525a2b` |
| **Working capacity (control)** | `fabricihzhhpfsit` — capacityId `23c32d0d-f5ab-430a-ac3f-97ec985e953f` (F2) |
| **Working workspace (control)** | `ws-ihzhhpf-sit-data` — `f3af9733-9503-4e92-98f9-a901d96f1c87` |
| **Sample failing requestId** | `6723372c-f19e-40a1-89ca-f7745140b5a1` |
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

Creating the Fabric IQ **`Ontology`** item on the PROD capacity fails with
`403 FeatureNotAvailable`, while the **identical** call on the SIT capacity (same
tenant, same region, same F2 SKU) succeeds. On the failing PROD capacity, the
sibling Fabric IQ item types **`DataAgent`** and **`GraphModel`** create without
error — so the gate is **specific to the `Ontology` item type on this capacity**.

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
| PROD `399b73f6-...` | `fabricihzhhpfprod` `4b690244-...` | **403 `FeatureNotAvailable`** |
| SIT `f3af9733-...` | `fabricihzhhpfsit` `23c32d0d-...` | **202 Accepted** (ontology created; probe deleted) |

Control probes on the **PROD** capacity (same endpoint, other Fabric IQ types):

| `type` | HTTP result on PROD capacity |
| ------ | ---------------------------- |
| `DataAgent` | **201 Created** (probe deleted) |
| `GraphModel` | **202 Accepted** (probe deleted) |
| `Ontology` | **403 `FeatureNotAvailable`** |

---

## 4. What we have ruled out

* **Not capacity state** — both capacities are `Active` (verified via Azure Resource Manager).
* **Not SKU** — both are **F2**.
* **Not region** — both are **westus2**.
* **Not a blanket Fabric IQ block** — `DataAgent` and `GraphModel` create on the same PROD capacity; only `Ontology` is refused.
* **Not a REST-only limitation** — the same REST call succeeds on the SIT capacity.

The remaining explanation is a **per-capacity / delegated tenant preview
enablement** for Fabric IQ **Ontology** items that is on for the SIT capacity and
off for the newer PROD capacity `fabricihzhhpfprod` (created 2026-07-19).

---

## 5. The ask

1. Identify the **tenant setting, delegated capacity setting, or preview
   enrolment** that controls Fabric IQ **`Ontology`** item creation.
2. Explain **how to enable it on capacity `fabricihzhhpfprod`
   (`4b690244-a91e-4028-9d0e-6dc2260a3432`)** so it matches `fabricihzhhpfsit`.
3. Confirm whether the setting is self-serviceable by a **Fabric Administrator /
   capacity admin**, or requires a backend/preview allow-list action.

---

## 6. Resolution path once the gate is lifted (no manual modelling needed)

The ontology can be replicated SIT → PROD entirely via REST because the SIT
ontology `getDefinition` round-trips cleanly:

1. `getDefinition` on SIT ontology `265c18d1-234e-436c-8297-0ca0a3e3b789`
   (10 EntityTypes + 11 RelationshipTypes + 10 DataBindings).
2. Swap only each DataBinding `sourceTableProperties`: `workspaceId`
   `f3af9733-...` → `399b73f6-...` and lakehouse `itemId` `30594c20-...` →
   `4f73c480-...` (schema `gold` and all table / entity / relationship / property
   identifiers are preserved verbatim).
3. `POST /items` with `type: Ontology` and the transformed definition
   (transform already written + validated: 32 parts, 20 GUID swaps, 0 residual
   SIT identifiers).
4. Create and publish `da_hospital_capacity` on PROD grounded on the semantic
   model and ontology, then endorse the PROD semantic model (Promote and
   Approve-for-Copilot).

---

## 7. Scope and guardrails

* **Environment:** westus2 demo / proof-of-technology under exception window
  `EX-2026-07-02-westus2-demo`; **synthetic data only, no PHI** (ADR-0013, ADR-0016).
* **Least privilege:** the request is limited to enabling one preview item type on
  one named capacity; no tenant-wide privilege change is required for this ticket.
* **No production data at risk:** the PROD workspace here is a demo PROD tier, not
  a patient-data production system.

---

## 8. References

* GitHub issue **#270** — PROD Fabric IQ ontology capacity gate (tracking).
* Sprint 19 (**#239**) — Full PROD deployment in eastus2 (Fabric placed in westus2).
* Sprint 21 (**#247**) — Fabric ingestion, ontology, semantic model.
* Related access ticket — `access-request-fabric-administrator.md` (Fabric
  Administrator role for the tenant-scoped **Domain / Data Product** governance
  lane; distinct from this capacity feature-gate issue).
