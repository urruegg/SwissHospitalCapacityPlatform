# Sprint 19 — PROD Switzerland North: rebuild evidence (Definition of Done)

| Field | Value |
|-------|-------|
| **Version** | 1.1.0 |
| **Date** | 2026-07-23 |
| **Author** | Urs Rüegg |
| **Status** | Reviewed |
| **Previous Version** | 1.0.0 (added CD-variable repoint + eastus2 retirement, #311) |

Capstone evidence for the DR-style teardown + Switzerland North greenfield
rebuild of PROD
([ADR-0037](../../adr/0037-prod-region-switzerland-north-greenfield.md),
issue [#239](https://github.com/urruegg/SwissHospitalCapacityPlatform/issues/239)).
Runbook: [`sprint-19-prod-switzerland-north-dr-rebuild-runbook.md`](../../runbooks/sprint-19-prod-switzerland-north-dr-rebuild-runbook.md).

**Approval:** `approved-to-apply` granted in-session by repo OWNER @urruegg
(2026-07-23) for Phases 0–8. Per-phase evidence recorded on #239; phase execution
records under [`evidence/`](evidence/).

**Environment:** subscription `66a9953a-df37-4c51-856c-9971b9bf3e03`, tenant
`1337187a-4c41-4da9-8fca-731bba7a4329` (MngEnvMCAP164444), short name `ihzhhpf`,
region **switzerlandnorth**. Synthetic data only, no PHI
([ADR-0016](../../adr/0016-no-phi-in-mvp-demo-scope.md)).

## Definition of Done

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Phase 0 clean slate — no PROD in any US region; `ai-ihzhhpf-prod` purged | ✅ | Phase 0 record + `evidence/2026-07-23-pre-teardown-*.json` |
| 2 | `az bicep build` on `infra/main.bicep` with `prod-swn.bicepparam` passes | ✅ | Baseline execution record |
| 3 | `rg-ihzhhpf-prod` in switzerlandnorth, baseline slice `Succeeded` | ✅ | Baseline execution record |
| 4 | Cosmos (CSA + platform): AAD-only; vector search on CSA | ✅ | `cosmos-ihzhhpf-prod` + `cosmos-csa-ihzhhpf-prod` `disableLocalAuth=True`, swn; CSA `EnableNoSQLVectorSearch=True` |
| 5 | AI Services + 3 models + 8 agents operational in swn | ✅ | P5 evidence on #239 (gpt-5, gpt-5-mini, o3; 8 agents via v2 API) |
| 6 | Container Apps healthy; agent-host returns 7 agents | ✅ | Both CAs `Running`; `/agents` → 7 (bmca, csa, data-quality, dca, ooa, orsa, sba) |
| 7 | `app.curavias.ch` resolves with valid TLS to swn app | ✅ | CNAME → swn CA; managed cert `SniEnabled`; `GET /` → **200** |
| 8 | Fabric F2 active in swn + PROD workspace | ✅ | `fabricihzhhpfprod` F2 Active; `ws-ihzhhpf-prod-data`; 50 Delta tables; semantic models + report published (P6 record) |
| 9 | E2E demo flow green (sign-in → app → agent → data → response) | ✅ | app 200 + agent-host 7 agents + live Foundry inference `PROD-SWN-OK` (gpt-5-mini, finish=stop) |
| 10 | PROD evidence document committed | ✅ | This document |
| 11 | SIT (westus2 + eastus2) unchanged — no regression | ✅ | `appsit` CNAME still westus2; `rg-ihzhhpf-sit` Succeeded; SIT Fabric/Cosmos/CA untouched |

## Key resources (switzerlandnorth)

| Resource | Name / value |
|----------|--------------|
| Resource group | `rg-ihzhhpf-prod` |
| App (Fluent) CA | `ca-app-fluent-ihzhhpf-prod` (Running) |
| Agent-host CA | `ca-agent-host-ihzhhpf-prod` (Running, 7 agents) |
| Custom domain | `app.curavias.ch` → swn CA, managed cert `SniEnabled`, HTTP 200 |
| Foundry account/project | `ai-ihzhhpf-prod` / `ai-ihzhhpf-prod-project` |
| Models | gpt-5, gpt-5-mini, o3 (GlobalStandard) |
| Cosmos (platform) | `cosmos-ihzhhpf-prod` (AAD-only) |
| Cosmos (CSA) | `cosmos-csa-ihzhhpf-prod` (AAD-only, vector search) |
| Key Vault | `kv-ihzhhpf-prod-swn1` (name-collision override) |
| Fabric capacity | `fabricihzhhpfprod` (F2, Active) |
| Fabric workspace | `ws-ihzhhpf-prod-data` (`1c8408f4-6eb7-401f-aee9-77fe4c8a515e`) |
| Fabric lakehouse | `lh_ihzhhpf_prod` (`57bd6e02-5248-439c-9f31-16bf9ee83cb4`, schemas-enabled, 50 Delta tables) |

## Phase 7 (DNS + Entra) actions

+ DNS: CNAME `app` in shared zone `curavias.ch` (`rg-ihzhhpf-sit`) re-pointed
  from the old eastus2 CA to the swn CA. `asuid.app` TXT already matched the
  new app's `customDomainVerificationId` (subscription-scoped) — no change.
  `appsit` / `asuid.appsit` (SIT) untouched.
+ Managed cert: `az containerapp hostname add` + `bind --validation-method CNAME`
  on `ca-app-fluent-ihzhhpf-prod` → `mc-cae-app-fluent-app-curavias-ch-7452`,
  `SniEnabled`.
+ Entra: on app registration `ihzhhpf-app` (`52681a08-...`), the old eastus2
  PROD SPA redirect URI was replaced with the swn CA URI; `https://app.curavias.ch`,
  the SIT URIs, and `http://localhost:5173` were preserved.
+ Logic App: skipped for parity (SIT `logic-ihzhhpf-sit` is Disabled).

## Scope assertion

Only PROD resources (`rg-ihzhhpf-prod` and the single `app` DNS record + the
`ihzhhpf-app` PROD redirect URI in shared scope) were changed. All SIT resources
(`rg-ihzhhpf-sit`, SIT Fabric workspace `f3af9733-...`, SIT Cosmos, SIT CA,
`appsit` DNS) and all other shared resources remained untouched. No regression.

## CD-variable repoint + eastus2 retirement (#311)

After the manual DR rebuild, the automated `cd-infra-deploy-prod` pipeline still
targeted the decommissioned **eastus2** environment. Repointed the PROD CD
variables (repo-level + `prod` environment) so an automated PROD run deploys the
switzerlandnorth environment, not the torn-down eastus2 one:

| Variable | Old (eastus2) | New (switzerlandnorth) |
|----------|---------------|------------------------|
| `AZURE_RESOURCE_GROUP` | `rg-ihzhhpf-prod-eastus2` | `rg-ihzhhpf-prod` |
| `BICEP_PARAM_FILE` | `infra/environments/prod-eastus2.bicepparam` | `infra/environments/prod-swn.bicepparam` |
| `AZURE_LOCATION` | `eastus2` | `switzerlandnorth` |

SIT CD variables were left unchanged (`rg-ihzhhpf-sit`, `sit.bicepparam`,
`westus2`) - SIT was untouched by the rebuild.

Verified end-to-end: `cd-infra-deploy-prod` run `30029098577` deployed
`prod-swn.bicepparam` to `rg-ihzhhpf-prod` / switzerlandnorth (Deploy PROD +
Policy gate green) - no destructive drift against the manually-built resources.

Retired the stale eastus2 references so the wrong target cannot be selected again:

+ Deleted `infra/environments/prod-eastus2.bicepparam` (obsolete; not referenced
  by any workflow or the policy pack). `prod.bicepparam` is retained - it is the
  westus2 demo baseline still referenced by `policy/policy-pack.json`.
+ Repointed the SIT-to-PROD resource-parity job in
  `.github/workflows/ci-infra-validate.yml` from `rg-ihzhhpf-prod-eastus2`
  (which no longer exists) to `rg-ihzhhpf-prod`.
