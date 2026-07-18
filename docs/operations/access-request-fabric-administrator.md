# Service Ticket — Request: Fabric Administrator role (MCAPS SIT tenant)

| Field | Value |
| ----- | ----- |
| **Version** | 1.0.0 |
| **Date** | 2026-07-18 |
| **Author** | Urs Rüegg |
| **Status** | Ready to submit |
| **Previous Version** | n/a (new) |

> **Purpose:** Submit-ready service ticket for the **MCAPS service owner / tenant
> administrator** requesting the **Fabric Administrator** role for the Swiss
> Hospital Capacity Platform development identity. Copy the *Ticket fields* block
> into the ITSM/service request form; the sections below are the justification,
> the complete list of current blockers, and the guardrails that keep the request
> least-privilege and time-boxed.

---

## 1. Ticket fields (copy/paste into the service request)

| Field | Value |
| ----- | ----- |
| **Request type** | Privileged role assignment — Microsoft Entra / Microsoft Fabric |
| **Role requested** | **Fabric Administrator** (Entra directory role `Fabric Administrator`, formerly "Power BI Administrator") |
| **Assignment mode** | **PIM-eligible, time-boxed** (activate-on-demand); **not** standing/permanent |
| **Requested duration** | Through **2026-09-30** (aligned to the westus2 demo exception window `EX-2026-07-02-westus2-demo`), auto-expire thereafter |
| **Scope** | Tenant `MngEnvMCAP164444.onmicrosoft.com` (`1337187a-4c41-4da9-8fca-731bba7a4329`) — Fabric SIT capacity only |
| **Requestor / grantee** | `admin@mngenvmcap164444.onmicrosoft.com` |
| **Current role** | **Global Reader** (read-only) — insufficient for any Fabric tenant/governance write |
| **Subscription** | `66a9953a-df37-4c51-856c-9971b9bf3e03` |
| **Primary workspace** | `ws-ihzhhpf-sit-data` — `f3af9733-9503-4e92-98f9-a901d96f1c87` (region westus2) |
| **Data classification** | **Synthetic only, no PHI** (demo / proof-of-technology) |
| **Priority** | Medium-High — actively blocking the current development sprint |
| **Business sponsor** | Swiss Hospital Capacity Platform (Case Study 26) — @urruegg |

---

## 2. Summary of the request

We are building a regulated-healthcare **Fabric IQ (Preview)** demonstrator: a
Medallion lakehouse feeding an operational **ontology**, a **semantic data
model**, and a published **Fabric Data Agent** that upstream **Azure AI Foundry**
agents consume. The development identity currently holds only **Global Reader**,
which permits **workspace-scoped** writes (build the ontology, Promote items,
create + publish the Data Agent) but **denies every tenant-scoped Fabric
governance and configuration action**.

We request the **Fabric Administrator** role (the narrowest role that covers
Fabric tenant settings, Domains, and certification) — **not** Global
Administrator — assigned **PIM-eligible and time-boxed** to the demo window.

---

## 3. Why this is crucial during the development cycle

1. **The governance lane is the deliverable, and it is entirely Fabric-Admin-gated.**
   The "Fabric IQ ready" story requires a governed **Domain** + **Data Product**
   with endorsement and lineage. Everything up to that point (medallion →
   ontology → semantic model → Data Agent) is done and verified; the chain now
   **stops at the one step Global Reader cannot perform**.

2. **Round-trip latency breaks the autonomous agent development loop.**
   Each blocked step currently needs an out-of-band admin action. In an
   agent-driven, iterate-fast workflow this adds days per iteration and prevents
   end-to-end validation in a single working session.

3. **Three upcoming Fabric sprints all need tenant-setting changes — grant once, not repeatedly.**
   - **Sprint 17 — Fabric Git CI/CD & lakehouse schema design:** requires the
     tenant settings *"Service principals can use Fabric APIs"*, *"Users can
     create Fabric items"*, and *Git integration* — all Fabric Admin.
   - **Sprint 19 — prod eastus2 full deployment:** capacity assignment and
     region/storage tenant settings.
   - **Sprint 21 — trusted external signals:** external data-sharing / OneLake
     external-data tenant settings.
   A single time-boxed grant avoids a stream of individual tickets.

4. **Operational safety of the demo capacity.** Copilot currently runs on the SIT
   capacity, but we cannot *govern or verify* the tenant settings that keep it
   running (Copilot enablement scope, capacity designation, cross-geo
   processing/storage). Without admin visibility the demo capacity can silently
   lose Copilot with no way for us to diagnose or restore it.

---

## 4. Current blockers (as of 2026-07-18)

| # | Blocker | Fabric-Admin action needed | Impact today |
| - | ------- | -------------------------- | ------------ |
| **B1** | **Domain + Data Product creation** (governed "Hospital Capacity" domain grouping the lakehouse, semantic model, and ontology) | Admin portal → **Domains** → create + assign workspace; publish Data Product | **Hard-blocked.** Admin Domains API returns **403** for Global Reader. This is the missing final step of the Fabric IQ readiness story. |
| **B2** | **Tenant Copilot / AI + capacity governance** (scope Copilot to a security group; designate SIT F-capacity as Fabric Copilot capacity; cross-geo processing **and** storage) | Fabric Admin portal → **Tenant settings** + **Capacity settings** | Cannot verify or control the settings the Data Agent depends on; risk of unannounced Copilot loss on the demo capacity. |
| **B3** | **Certified endorsement** of the ontology + semantic model | Fabric Admin portal → **Certification** (tenant certifier list) | Can only **Promote** (workspace-scoped). "Certified" — the stronger trust signal for the demo — is unreachable. |
| **B4** | **Sprint 17 Git CI/CD enablement** (service-principal API access, item/workspace creation, Git integration) | Fabric Admin portal → **Tenant settings** | Blocks the planned automated Fabric deployment pipeline before it can start. |
| **B5** | **Sprint 19 eastus2 deployment** (capacity + region/storage settings) | Fabric Admin portal → **Capacity / Tenant settings** | Blocks the planned prod-region migration. |
| **B6** | **Sprint 21 external signals** (external data sharing / OneLake external data) | Fabric Admin portal → **Tenant settings** | Blocks the planned trusted-external-signals design. |

> **Note on what is *not* blocked:** ontology build + binding, item **Promotion**,
> and Data Agent create/configure/**publish** all succeed today under Global
> Reader (workspace-scoped). The demo's live agent path (Foundry → Data Agent) is
> **not** blocked — only the tenant-governance wrapper around it is. B1 is the
> only item on the current critical path; B2–B6 are near-term.

---

## 5. Guardrails (why this stays safe and least-privilege)

- **Least privilege:** requesting **Fabric Administrator**, the narrowest role
  covering Fabric tenant settings, Domains, and certification — **explicitly not
  Global Administrator**.
- **Time-boxed:** PIM-eligible, activate-on-demand, auto-expiring at the demo
  sunset (**2026-09-30**), consistent with exception `EX-2026-07-02-westus2-demo`.
- **Non-production, synthetic only:** demo / proof-of-technology scope,
  **no PHI** (ADR-0016), Preview features on non-prod (ADR-0006), temporary
  westus2 region under the approved exception (ADR-0013). Sunsets back to
  `switzerlandnorth` when target services reach Swiss GA.
- **Auditable:** all platform actions are GitHub-native (issues, PRs, commits);
  Fabric admin actions are logged in the tenant admin audit log.
- **Reversible:** remove the eligible assignment at demo end or on request; no
  standing privilege remains.

---

## 6. Acceptance / done criteria

- [ ] `Fabric Administrator` assigned to `admin@mngenvmcap164444.onmicrosoft.com`
      as **PIM-eligible**, expiry ≤ 2026-09-30.
- [ ] Requestor can open **Fabric Admin portal → Tenant settings** and
      **→ Domains** without a 403.
- [ ] Ticket references this document and the guardrail ADRs (0006, 0013, 0016).
- [ ] Removal reminder set for the expiry date.

---

## 7. References

- Runtime + tenant: [AGENTS.md](../../AGENTS.md) (tenant migration — Sprint 00),
  [ADR-0012](../adr/0012-tenant-migration-to-mcap164444.md).
- Region / data guardrails: [ADR-0013](../adr/0013-temporary-us-region-demo-scope.md),
  [ADR-0016](../adr/0016-no-phi-in-mvp-demo-scope.md),
  [ADR-0006](../adr/0006-preview-features-non-production-rule.md).
- Blocked work: [Fabric IQ (Preview) demo showcase plan](../superpowers/plans/2026-07-18-fabric-iq-preview-demo-showcase.md)
  (Task M0 tenant prerequisites; Task M2 Domain + Data Product).
- Data Agent runbook (unblocked path): [create_data_agent.md](../../data-platform/scripts/fabric/create_data_agent.md).
