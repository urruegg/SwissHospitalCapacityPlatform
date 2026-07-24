# Sprint 19 — Full PROD Deployment in eastus2 (Fresh from Scratch)

| Field | Value |
| ----- | ----- |
| **Version** | 2.0.0 |
| **Date** | 2026-07-24 |
| **Author** | @urruegg |
| **Status** | Superseded — PROD pivoted to Switzerland North (ADR-0037); extended by the SIT↔PROD parity plan (2026-07-24) |
| **Previous Version** | 1.0.0 (eastus2 charter; region reversed to Switzerland North per ADR-0037) |

> **⚠️ Superseded / extended (2026-07-24).** The `eastus2` target in this charter was
> **reversed to Switzerland North** ([ADR-0037](../adr/0037-prod-region-switzerland-north-greenfield.md));
> the greenfield rebuild is complete and evidenced in
> [`sprint-19/prod-evidence-switzerlandnorth.md`](sprint-19/prod-evidence-switzerlandnorth.md)
> (11/11 Definition-of-Done ✅). Remaining SIT↔PROD end-to-end parity, all-levels evidence,
> and the Curavias product-documentation refresh are driven by the
> **[Sprint 19 Extension — SIT↔PROD parity plan (2026-07-24)](../superpowers/plans/2026-07-24-sprint-19-sit-prod-parity-extension.md)**.
> This file is retained for history; read the extension plan for current scope.

<!-- -->

> **Sprint theme.** Deploy the entire PROD environment from scratch in eastus2 — all resources collocated in a single region — using Bicep-first IaC. Eliminates cross-region latency, simplifies network topology, and delivers a production-ready demo surface with full Foundry Agent Service capability.

---

## 1. Sprint goal

Deliver a complete, collocated PROD environment in eastus2 with all 25 resources deployed via Bicep, 8 agents registered and operational, custom domain `app.curavias.ch` live with TLS, Fabric PROD workspace connected, and end-to-end demo flow verified.

**Success shape:**

- `rg-ihzhhpf-prod-eastus2` with 25+ resources all `Succeeded`.
- Container Apps: agent-host (7 agents loaded), app-fluent (custom domain + TLS), sim-capacity.
- Cosmos DB: 2 accounts (CSA + platform), AAD-only, PE-connected, vector search on CSA.
- AI Services + Foundry: 3 models + 8 agents registered and functional.
- Fabric: F2 capacity + PROD workspace with Gold lakehouse.
- DNS: `app.curavias.ch` → PROD with valid TLS.
- End-to-end demo flow: sign-in → app → agent → data → response.

---

## 2. Source baseline

1. [Sprint 18 (must be complete)](sprint-18-foundry-eastus2-control-plane.md) — Foundry proven in eastus2
2. [Sprint 19 Design Spec](../superpowers/specs/2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md)
3. [Sprint 19 Implementation Plan](../superpowers/plans/2026-07-17-sprint-19-prod-eastus2-full-deployment-plan.md)
4. [SIT Evidence (2026-07-17)](sit-evidence-2026-07-17.md) — resource patterns to replicate
5. [Sprint 17: Fabric Git Integration](../superpowers/specs/2026-07-10-sprint-17-fabric-git-cicd-and-lakehouse-schema-design.md)
6. [ADR-0013: Temporary US Region Demo Scope](../adr/0013-temporary-us-region-demo-scope.md)

---

## 3. Sprint scope

| Phase | Tasks | Key deliverables |
|-------|-------|-----------------|
| P1: IaC | T1 (Bicep modules) | `infra/prod-eastus2/main.bicep` + 15 modules |
| P2: Foundation | T2–T6 (VNet, KV, Storage, Log, ACR) | Network + observability + registry |
| P3: Compute | T7 (CAE + 3 Container Apps) | Agent-host + App + Sim running |
| P4: Data | T8–T10, T15 (Cosmos ×2, EVH, SB, PEs) | Data layer + private networking |
| P5: AI/Foundry | T11–T13 (AI + models + agents) | Full agent roster in PROD |
| P6: Fabric | T16 (capacity + workspace) | F2 + workspace + data |
| P7: Integration | T17–T19 (DNS, Logic, Entra) | Custom domain live + auth |
| P8: Verification | T20–T22 (E2E test, evidence) | Demo flow green + docs |

---

## 4. Key decisions

| # | Decision | Rationale |
|---|----------|-----------|
| D1 | Fresh deploy (not migration) | Synthetic data only; no state to preserve. Cleaner + lower risk than migration. |
| D2 | All resources in eastus2 | Zero cross-region latency. All 22 types confirmed GA. |
| D3 | Bicep-first IaC | Reproducible; `what-if` before apply; version-controlled. |
| D4 | SIT unchanged in westus2 | Keeps fallback; decommission deferred to future sprint. |
| D5 | Serverless/Consumption tier for data | Cost-appropriate for demo; scale later if needed. |

---

## 5. Definition of Done

- [ ] `infra/prod-eastus2/main.bicep` passes `az bicep build`
- [ ] `what-if` produces expected resource set (≥25 resources)
- [ ] All resources deployed with `Succeeded` provisioningState
- [ ] Cosmos DB: AAD-only, PE-connected, vector search enabled (CSA)
- [ ] AI Services + 3 models + 8 agents all operational
- [ ] Container Apps: 3 apps healthy, agent-host returns 7 agents
- [ ] `app.curavias.ch` resolves with valid TLS to PROD app
- [ ] Fabric F2 active + PROD workspace created
- [ ] E2E demo flow verified (sign-in → agent → data → response)
- [ ] `docs/sprints/prod-evidence-eastus2.md` committed
- [ ] All CI checks pass (markdown lint, link check, Bicep build)
- [ ] SIT in westus2 remains functional (no regression)

---

## 6. Risk register

| Risk | Mitigation |
|------|------------|
| Bicep module failure | Deploy module-by-module; `what-if` gates |
| DNS propagation delay | 24h buffer; pre-validate with dig |
| Fabric Git integration unavailable in eastus2 | Fall back to REST publish |
| Cost overrun | All Serverless/Consumption; weekly cost review |

---

## 7. References

- Design: [`2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md`](../superpowers/specs/2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md)
- Plan: [`2026-07-17-sprint-19-prod-eastus2-full-deployment-plan.md`](../superpowers/plans/2026-07-17-sprint-19-prod-eastus2-full-deployment-plan.md)
- **Extension plan (2026-07-24):** [`2026-07-24-sprint-19-sit-prod-parity-extension.md`](../superpowers/plans/2026-07-24-sprint-19-sit-prod-parity-extension.md)
- **PROD Switzerland North evidence:** [`sprint-19/prod-evidence-switzerlandnorth.md`](sprint-19/prod-evidence-switzerlandnorth.md)
- **Region pivot:** [ADR-0037](../adr/0037-prod-region-switzerland-north-greenfield.md)
- Issue: [#239](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/239)
