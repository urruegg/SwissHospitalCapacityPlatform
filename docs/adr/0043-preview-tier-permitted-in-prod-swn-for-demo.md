# ADR-0043: Preview-tier services permitted in PROD Switzerland North for the Curavias demo (GA-only gate reserved for real go-live cut-over)

| Field | Value |
|-------|-------|
| **Status** | Accepted |
| **Date** | 2026-07-25 |
| **Author** | Urs Rüegg |
| **Decision-makers** | @urruegg |
| **Refines** | [ADR-0006](0006-preview-features-non-production-rule.md) (its written Preview exception) and [ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md) (generalises the named-feature exception into a standing demo-scope posture). |
| **Related** | [ADR-0013](0013-temporary-us-region-demo-scope.md), [ADR-0016](0016-no-phi-in-mvp-demo-scope.md), [ADR-0037](0037-prod-region-switzerland-north-greenfield.md), [issue #255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255) |
| **Consulted** | Product-owner decision from @urruegg on 2026-07-25; [docs/region-availability.yaml](../region-availability.yaml); ADR-0042 evidence matrix |

## Context

[ADR-0042](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
granted a **standing Preview exception** for PROD Switzerland North, but scoped
it to two **named** Preview features (`fabric-iq-ontology`, `fabric-data-agent`).
Subsequent demo work needs the same latitude for other Preview-tier capabilities
(and for target-state transports such as the skills-events Event Hub → Eventstream
rail), without opening a new named-feature exception each time.

The product goal remains: demonstrate the full Curavias stack end-to-end **in
Switzerland**, to show **what the technology stack makes possible today**. The
platform runs synthetic-only data with no PID/PHI ([ADR-0016](0016-no-phi-in-mvp-demo-scope.md)),
so the regulated-data rationale behind [ADR-0006](0006-preview-features-non-production-rule.md)
does not bind the current demo scope.

The **skills-events near-real-time lane** (WS-A4, [issue #255](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255))
was previously recorded with its `sourceMode=EventHub` transport "parked until
Fabric Swiss GA". That framing was over-conservative: **Eventstream is GA in
Switzerland North** ([docs/region-availability.yaml](../region-availability.yaml),
asOf 2026-07-09), Azure Event Hubs is GA there, PROD Fabric (`fabricihzhhpfprod`)
already runs in Switzerland North, and the PROD Event Hubs namespace
(`evh-ihzhhpf-prod-i62t`) already exists in-region. The only real blocker is an
out-of-band Fabric-managed connection, not a GA milestone.

## Decision

1. **Preview-tier Azure/Fabric services are permitted in PROD Switzerland North**
   strictly to demonstrate the Curavias stack under **synthetic / no-PHI** scope.
   This generalises ADR-0042 from two named features to a standing demo-scope
   posture, and satisfies ADR-0006's written-exception requirement for that scope.
2. The **GA-only gate applies solely to a real go-live (real-PHI) cut-over.**
   Proving value and the art of the possible in **Preview in Switzerland is
   sufficient** for the demo; work must not be re-parked behind a GA milestone
   unless it targets a real go-live cut-over.
3. **The skills-events `sourceMode=EventHub` flip is un-parked.** It is in fact
   **GA in Switzerland North** (Eventstream + Event Hubs), so it does not even
   consume this Preview exception; the "parked until Swiss GA" gate on it is
   lifted. Its only remaining prerequisite is the out-of-band Fabric-managed
   connection (`POST /v1/connections`).
4. **Environment isolation is preserved.** SIT (westus2 / eastus2, per enabled
   capacity) and PROD (Switzerland North) **do not share input services** —
   separate Event Hubs namespaces, resource groups, and regions
   (`evh-ihzhhpf-sit-y26y` vs `evh-ihzhhpf-prod-i62t`). New input services follow
   the per-environment, per-functional-domain pattern (a **dedicated skills-events
   Event Hub**, not shared with the capacity `events` rail).

## Exception record (ADR-0006 compliance)

| Field | Exception record |
|-------|------------------|
| Owner | @urruegg |
| Scope | PROD Switzerland North, synthetic/no-PHI Curavias demo only. |
| Risk | Preview-tier services carry no production SLA and may change or deprecate. |
| Compensating controls | Synthetic-only data and no PHI per ADR-0013/ADR-0016; GA-core PROD stays independent of any Preview capability so a Preview failure never degrades the GA stack; IaC-reproducible; per-environment input isolation. |
| Rollback path | Disable the Preview/target-state module flag (for the skills lane: keep `skillsEventstreamSourceMode='CustomEndpoint'`) and redeploy. GA-core is unaffected. |
| Expiry / revisit | Whichever comes first: the relevant capability reaches GA in Switzerland North; or real-Swiss-PHI onboarding, then re-evaluate under full ADR-0006 regulated-data rules and the GA-only cut-over gate. |

## Consequences

**Positive:**

* Removes the recurring need for a named-feature exception per Preview capability
  in the demo scope.
* Un-parks the skills-events Event Hub flip and any comparable target-state work
  in PROD Switzerland North.
* Keeps a hard GA-only gate exactly where it matters — real go-live cut-over.

**Negative / risks:**

* Preview-tier services may regress with no SLA; mitigated by synthetic/no-PHI
  scope and GA-core independence.
* Broader latitude requires discipline: each use must still stay within the
  synthetic/no-PHI demo scope recorded here.

## Update (2026-07-26) — live EventHub bind deferred (platform gap)

**Decision.3 above (the `sourceMode=EventHub` flip) is un-parked from the GA gate but its live
bind is now DEFERRED for a different, newly-discovered reason** — a Fabric platform gap, not a GA
milestone. When the live bind was attempted (under `approved-to-apply`, 2026-07-26) it hit two
**mutually exclusive** constraints:

1. **Fabric Eventstream's Event Hubs source supports only Shared Access Key (SAS) auth.**
   Workspace-identity / AAD auth is **not yet GA** (on the Fabric roadmap); attempts return
   `DMTS_UntrustedEndpointForWorkspaceIdentity`. Confirmed by Microsoft Learn
   (*Add an Azure Event Hubs source to an Eventstream*) and a Microsoft employee on the Fabric
   community forum.
2. **The PROD namespace `evh-ihzhhpf-prod-i62t` runs `disableLocalAuth=true`** — SAS/local auth is
   **disabled** (AAD-only). This is enforced by a security-baseline **Azure Policy**, not by our
   Bicep (`infra/modules/data-foundation/eventhubs/main.bicep` never sets it). Every SAS/`Basic`
   connection attempt returned `AccessUnauthorized`. The EH design is **AAD/RBAC-only by intent**
   (the simulator publishes via the `Azure Event Hubs Data Sender` role, not a key).

Eventstream wants SAS; the namespace forbids SAS. The namespace allows AAD; Eventstream doesn't
support AAD yet. There is **no path through without a security-posture downgrade**
(`disableLocalAuth=false` + an Azure Policy exemption), which contradicts the AAD-only secretless
design and is out of scope for a demo.

**Decision (@urruegg, 2026-07-26): keep the AAD-only secretless posture and DEFER the live EH bind
until Fabric GAs workspace-identity auth for Event Hub sources.** Consequences:

* The dedicated `skills-events` Event Hub + `cg-skills-eventstream` consumer group + simulator
  `Data Sender` RBAC are **already deployed** (PR #393) and simply wait for that Fabric GA.
* The **`CustomEndpoint`** source (live in SIT, PR #379) remains the deployable demo transport for
  the skills-events lane. This is already the documented rollback path in the exception record above.
* **No COMPLIANCE amendment is required.** The namespace is genuinely AAD-only / secretless, so the
  existing "secretless" lineage claim is accurate — SAS was never used and every test artefact
  (two Listen SAS rules + a workspace-identity Data Receiver role) was rolled back; PROD is
  byte-for-byte unchanged.
* **Do not flip `disableLocalAuth`** to force SAS: it is a real security downgrade and is reverted
  by the enforcing policy. A future revisit is gated on Fabric workspace-identity GA (tracked as a
  remaining #255 follow-up), not on a namespace auth change.

This update refines Decision.3's "only remaining prerequisite is the out-of-band Fabric-managed
connection" statement, which is superseded by the constraint pair above.

## References

* [ADR-0006 — Preview features non-production rule](0006-preview-features-non-production-rule.md)
* [ADR-0042 — PROD Switzerland North GA target + standing Preview exception](0042-prod-switzerland-north-ga-target-standing-preview-exception.md)
* [ADR-0013 — Temporary US-region demo scope](0013-temporary-us-region-demo-scope.md)
* [ADR-0016 — No PHI in MVP demo scope](0016-no-phi-in-mvp-demo-scope.md)
* [ADR-0037 — PROD region pivot to Switzerland North](0037-prod-region-switzerland-north-greenfield.md)
* [docs/region-availability.yaml](../region-availability.yaml)
* [Issue #255 — Unified Curavias organisation spine + org/skills ontology](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/255)
