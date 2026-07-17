# Sprint 19 — Full PROD Deployment in eastus2 — Implementation Plan

| Field | Value |
|-------|-------|
| **Version** | 1.0.0 |
| **Date** | 2026-07-17 |
| **Author** | Urs Rüeegg |
| **Status** | Pending (blocked on Sprint 18 completion) |
| **Previous Version** | n/a |
| **Design spec** | [2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md](../specs/2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md) |

---

## Execution phases

### Phase 1 — IaC Authoring (T1)

#### 1.1 Scaffold Bicep modules

Create `infra/prod-eastus2/` with the module structure defined in Design §7:

```bash
mkdir -p infra/prod-eastus2/modules infra/prod-eastus2/parameters
```

Each module follows:
- Input: environment name (`prod`), location (`eastus2`), resource name pattern
- Output: resource IDs for cross-module references
- Tags: `env=prod`, `owner=urruegg`, `costCenter=demo`, `workload=ihzhhpf`
- Diagnostic settings where applicable

#### 1.2 Author main.bicep orchestrator

```bicep
targetScope = 'resourceGroup'

param environment string = 'prod'
param location string = 'eastus2'
param solutionShortName string = 'ihzhhpf'

// Module invocations in dependency order:
// 1. identities → 2. network → 3. keyvault → 4. storage → 5. monitoring
// 6. container-registry → 7. cosmos-csa → 8. cosmos-platform
// 9. eventhubs → 10. servicebus → 11. container-apps
// 12. ai-services → 13. fabric → 14. logic-apps → 15. private-dns
```

#### 1.3 Author parameters file

```json
{
  "environment": { "value": "prod" },
  "location": { "value": "eastus2" },
  "solutionShortName": { "value": "ihzhhpf" },
  "fabricSkuName": { "value": "F2" },
  "cosmosDbConsistency": { "value": "Session" },
  "containerRegistrySku": { "value": "Basic" }
}
```

### Phase 2 — Foundation Deployment (T2–T6)

#### 2.1 Create resource group

```bash
az group create --name rg-ihzhhpf-prod-eastus2 --location eastus2 \
  --tags env=prod owner=urruegg costCenter=demo workload=ihzhhpf
```

#### 2.2 Deploy foundation modules

```bash
az deployment group what-if \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --template-file infra/prod-eastus2/main.bicep \
  --parameters infra/prod-eastus2/parameters/prod.parameters.json \
  --mode Incremental
```

Wait for `approved-to-apply`, then:

```bash
az deployment group create \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --template-file infra/prod-eastus2/main.bicep \
  --parameters infra/prod-eastus2/parameters/prod.parameters.json \
  --mode Incremental
```

### Phase 3 — Compute Layer (T7)

#### 3.1 Push container images to PROD ACR

```bash
# Option A: geo-replicate existing ACR
az acr replication create --registry cri75lbu5sj4hza --location eastus2

# Option B: create new PROD ACR and push
az acr create --name crihzhhpfprod --resource-group rg-ihzhhpf-prod-eastus2 \
  --location eastus2 --sku Basic --admin-enabled false

# Push images
az acr import --name crihzhhpfprod \
  --source cri75lbu5sj4hza.azurecr.io/agent-host:latest \
  --image agent-host:latest
az acr import --name crihzhhpfprod \
  --source cri75lbu5sj4hza.azurecr.io/app-fluent:latest \
  --image app-fluent:latest
az acr import --name crihzhhpfprod \
  --source cri75lbu5sj4hza.azurecr.io/sim-capacity:latest \
  --image sim-capacity:latest
```

#### 3.2 Verify Container Apps health

```bash
# Agent-host health
curl -s https://ca-agent-host-ihzhhpf-prod.<region>.azurecontainerapps.io/health

# App Fluent (after DNS)
curl -s https://ca-app-fluent-ihzhhpf-prod.<region>.azurecontainerapps.io/
```

### Phase 4 — Data Layer (T8–T10, T15)

#### 4.1 Verify Cosmos DB configuration

```bash
# Cosmos CSA: AAD-only, vector search, PE
az cosmosdb show --name cosmos-csa-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --query "{localAuth:disableLocalAuth, vectorSearch:capabilities}"

# Verify private endpoint connectivity
az network private-endpoint show --name pe-cosmos-csa-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --query "privateLinkServiceConnections[0].privateLinkServiceConnectionState.status"
```

#### 4.2 Seed CSA containers

Run the CSA seed notebook to create the 4 containers with vector embedding policies:
- `scenarios` (partition: `/scenarioId`)
- `simulation-runs` (partition: `/runId`)
- `agent-memory` (partition: `/threadId`)
- `response-levers` (partition: `/leverId`)

### Phase 5 — AI/Foundry Layer (T11–T13)

#### 5.1 Deploy models

Follow Sprint 18 pattern (already proven):
- gpt-5: GlobalStandard, 50 TPM
- gpt-5-mini: GlobalStandard, 100 TPM
- o3: GlobalStandard, 30 TPM

#### 5.2 Register 8 agents

Same registration flow as Sprint 18 but targeting PROD project endpoint:
```
https://ai-ihzhhpf-prod-eastus2.services.ai.azure.com/api/projects/ai-ihzhhpf-prod-eastus2-project/assistants
```

### Phase 6 — Fabric (T16)

#### 6.1 Create PROD Fabric capacity

```bash
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/.../resourceGroups/rg-ihzhhpf-prod-eastus2/providers/Microsoft.Fabric/capacities/fabricihzhhpfprod?api-version=2023-11-01" \
  --body '{"location":"eastus2","sku":{"name":"F2","tier":"Fabric"},"properties":{"administration":{"members":["admin@mngenvmcap164444.onmicrosoft.com"]}}}'
```

#### 6.2 Create PROD workspace and connect

- Create `ws-ihzhhpf-prod-data` workspace
- Assign to `fabricihzhhpfprod` capacity
- Connect via Fabric Git integration (Sprint 17 pattern) or REST publish

### Phase 7 — Integration (T17–T19)

#### 7.1 DNS cutover for PROD

```bash
# Add custom domain binding
az containerapp hostname add --name ca-app-fluent-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --hostname app.curavias.ch

# Bind managed certificate
az containerapp hostname bind --name ca-app-fluent-ihzhhpf-prod \
  --resource-group rg-ihzhhpf-prod-eastus2 \
  --hostname app.curavias.ch \
  --environment cae-ihzhhpf-prod

# Update DNS
az network dns record-set cname set-record \
  --resource-group rg-ihzhhpf-sit \
  --zone-name curavias.ch \
  --record-set-name app \
  --cname ca-app-fluent-ihzhhpf-prod.<region>.azurecontainerapps.io
```

#### 7.2 Entra PROD bindings

- Add PROD redirect URIs to existing app registration
- Verify MSAL authentication flow against PROD endpoints

### Phase 8 — End-to-End Verification (T20–T22)

#### 8.1 Full demo flow test

1. Navigate to `app.curavias.ch` → verify TLS + login page
2. Sign in as demo persona → verify role-based view
3. Invoke `bmca-agent` via Copilot drawer → verify response
4. Query Fabric Gold table via semantic model → verify data
5. Open CSA wizard → verify scenario creation in Cosmos
6. Check agent-host `/agents` endpoint → verify 7 agents loaded

#### 8.2 Produce PROD evidence document

```
docs/sprints/prod-evidence-eastus2.md
```

Contents:
- Resource inventory (all 25 resources with provisioningState)
- Model deployment confirmations
- Agent registration proof
- E2E test results
- Security posture verification (PE, AAD-only, TLS)
- Bicep deployment output

---

## Validation checklist (pre-merge)

```bash
# Bicep build
az bicep build --file infra/prod-eastus2/main.bicep

# Markdown lint
npx --yes markdownlint-cli2 "docs/**/*.md" "infra/**/*.md" "#node_modules"

# Link check
npx --yes markdown-link-check docs/sprints/prod-evidence-eastus2.md

# Resource verification
az resource list --resource-group rg-ihzhhpf-prod-eastus2 \
  --query "length(@)" -o tsv
# Expected: ≥ 25
```

---

## Sprint close criteria

All items from [Design Spec §14 (Definition of Done)](../specs/2026-07-17-sprint-19-prod-eastus2-full-deployment-design.md#14-definition-of-done) verified green.
