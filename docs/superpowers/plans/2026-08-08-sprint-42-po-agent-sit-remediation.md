# Sprint 42 — PO Agent SIT Root-Cause Remediation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the real SIT `po-agent-service` return a genuinely grounded
(`refused: false`) answer for at least one knowledge class, by fixing the 3
root causes + env-var mismatch the Sprint 41 WS-0 audit found, plus a
guardrail so the env-var class of drift can't silently recur.

**Architecture:** All fixes land in the existing
`infra/modules/experience-hosting/po-agent-runtime/main.bicep` module
(env vars + ARM RBAC), one new scripted Fabric REST grant (workspace roles
aren't ARM resources), one new scripted Azure AI Search index create
(mirrors the repo's existing `knowledge-base-rest.md` runbook — Search
indexes aren't ARM resources either), and a small Python guardrail test.
No Python business logic changes — Sprint 41's client code is already
correct against the frozen contract; only the environment must match it.

**Tech Stack:** Bicep, Python 3.11 (`requests`, stdlib `urllib`), pytest,
Azure CLI (`az bicep build`, `az account get-access-token`), GitHub Actions.

---

## Task 1: Fix the runtime container's env-var contract (Bicep)

**Files:**
- Modify: `infra/modules/experience-hosting/po-agent-runtime/main.bicep`
- Modify: `infra/main.bicep:573-591` (the `poAgentRuntime` module call)

- [ ] **Step 1: Add the new params to the module**

In `infra/modules/experience-hosting/po-agent-runtime/main.bicep`, add these
params right after the existing `searchRestApiVersion` param (after the
line `param searchRestApiVersion string = '2024-05-01-preview'`):

```bicep
@description('Name of the Azure AI Search index the runtime queries for Class A corpus retrieval. Threaded as AZURE_SEARCH_INDEX.')
param searchIndexName string = 'idx-curavias-corpus-${nameSuffix}'

@description('Published Fabric Data Agent consumption endpoint (Class D ontology). Empty skips Class D wiring — same fabricDataAgentEndpoint value already used by the agent-host module (infra/main.bicep).')
param fabricDataAgentEndpoint string = ''

@description('Fabric workspace ID hosting the Data Agent (Class D). Parsed by convention from fabricDataAgentEndpoint\'s /workspaces/{id}/ path segment when not overridden.')
param fabricWorkspaceId string = ''

@description('Fabric Data Agent artifact ID (Class D). Same fabricDataAgentId value already used by the agent-host module.')
param fabricDataAgentId string = ''

@description('Foundry project endpoint (Class B live-proof + Class C cost reconciliation). Defaults to the ADR-0032 SIT project; override per environment.')
param foundryProjectEndpoint string = 'https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com'

@description('Foundry project name (Class B/C). Defaults to the ADR-0032 SIT project.')
param foundryProjectName string = 'ai-ihzhhpf-sit-eastus2-project'
```

Add this `var` near the existing `var` block (right after `var acrPullRoleId = ...`):

```bicep
// Class D: workspace id is the path segment between /workspaces/ and /aiskills/
// in fabricDataAgentEndpoint (matches infra/modules/agent-host's own convention).
var effectiveFabricWorkspaceId = !empty(fabricWorkspaceId) ? fabricWorkspaceId : (!empty(fabricDataAgentEndpoint) ? split(split(fabricDataAgentEndpoint, '/workspaces/')[1], '/')[0] : '')
```

- [ ] **Step 2: Rename/add the container env vars**

In the same file, find the `runtimeApp` resource's `env` array (inside
`template.containers[0].env`). Replace this block:

```bicep
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: identity.properties.clientId
            }
            {
              name: 'SEARCH_ENDPOINT'
              value: searchEndpoint
            }
            {
              name: 'SEARCH_API_VERSION'
              value: searchRestApiVersion
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openai.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: openAiDeploymentName
            }
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmos.properties.documentEndpoint
            }
            {
              name: 'KEY_VAULT_URI'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'DEMO_SCOPE'
              value: demoScope ? 'true' : 'false'
            }
          ]
```

with:

```bicep
          env: [
            {
              name: 'AZURE_CLIENT_ID'
              value: identity.properties.clientId
            }
            {
              name: 'AZURE_SUBSCRIPTION_ID'
              value: subscription().subscriptionId
            }
            {
              name: 'AZURE_SEARCH_ENDPOINT'
              value: searchEndpoint
            }
            {
              name: 'AZURE_SEARCH_INDEX'
              value: searchIndexName
            }
            {
              name: 'SEARCH_API_VERSION'
              value: searchRestApiVersion
            }
            {
              name: 'FABRIC_DATA_AGENT_ENDPOINT'
              value: fabricDataAgentEndpoint
            }
            {
              name: 'FABRIC_WORKSPACE_ID'
              value: effectiveFabricWorkspaceId
            }
            {
              name: 'FABRIC_DATA_AGENT_ID'
              value: fabricDataAgentId
            }
            {
              name: 'FOUNDRY_PROJECT_ENDPOINT'
              value: foundryProjectEndpoint
            }
            {
              name: 'FOUNDRY_PROJECT_NAME'
              value: foundryProjectName
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: openai.properties.endpoint
            }
            {
              name: 'AZURE_OPENAI_DEPLOYMENT'
              value: openAiDeploymentName
            }
            {
              name: 'COSMOS_ENDPOINT'
              value: cosmos.properties.documentEndpoint
            }
            {
              name: 'KEY_VAULT_URI'
              value: keyVault.properties.vaultUri
            }
            {
              name: 'DEMO_SCOPE'
              value: demoScope ? 'true' : 'false'
            }
          ]
```

- [ ] **Step 3: Verify the module compiles**

Run: `az bicep build --file infra/modules/experience-hosting/po-agent-runtime/main.bicep --stdout > $null`
Expected: no output, exit code 0 (silent success means clean compile).

- [ ] **Step 4: Thread the new params from `infra/main.bicep`**

In `infra/main.bicep`, find the `poAgentRuntime` module call (starts at
line 573). Add these two lines inside its `params: { ... }` block, right
after the existing `searchRestApiVersion: ...` line:

```bicep
    searchIndexName: 'idx-curavias-corpus-${resourceSuffix}'
    fabricDataAgentEndpoint: fabricDataAgentEndpoint
    fabricDataAgentId: fabricDataAgentId
```

(`fabricDataAgentEndpoint`/`fabricDataAgentId` are `infra/main.bicep`'s
own existing top-level params, lines 289/295 — this reuses the exact same
values already threaded to the agent-host module, no new bicepparam entries
needed.)

- [ ] **Step 5: Verify the full template still compiles**

Run: `az bicep build --file infra/main.bicep --stdout > $null`
Expected: exit code 0. Pre-existing warnings unrelated to this change (if
any) are acceptable; no new errors mentioning `poAgentRuntime`,
`fabricDataAgentEndpoint`, `searchIndexName`, or `effectiveFabricWorkspaceId`.

- [ ] **Step 6: Commit**

```bash
git add infra/modules/experience-hosting/po-agent-runtime/main.bicep infra/main.bicep
git commit -m "fix(infra): align po-agent-runtime env vars with the Python contract"
```

---

## Task 2: Add Class B + C subscription-scope RBAC (Bicep)

**Files:**
- Modify: `infra/modules/experience-hosting/po-agent-runtime/main.bicep`

- [ ] **Step 1: Add the role-id vars and a toggle param**

Add this param after the `demoScope` param:

```bicep
@description('When true, grants the runtime MI subscription-scope Reader + Cost Management Reader (Class B/C). Default true; set false only for a narrower test deployment.')
param grantSubscriptionScopeRoles bool = true
```

Add these two vars next to the existing `searchIndexDataReaderRoleId` etc.
vars:

```bicep
// Class B (live-proof, Resource Graph) + Class C (cost) — both are
// subscription-scoped services with no narrower ARM scope.
var readerRoleId = 'acdd72a7-3385-48ef-bd42-f606fba81ae7'
var costManagementReaderRoleId = '72fafb9e-0641-4937-9268-a91bfd8191a3'
```

- [ ] **Step 2: Add the two role assignments**

Add this block right after the existing `searchReaderRole` resource
(after its closing `}`):

```bicep
resource readerRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (grantSubscriptionScopeRoles) {
  name: guid(subscription().id, identity.id, readerRoleId)
  scope: subscription()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', readerRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 42 — PO Agent runtime MI queries Azure Resource Graph (Class B live-proof, keyless).'
  }
}

resource costManagementReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (grantSubscriptionScopeRoles) {
  name: guid(subscription().id, identity.id, costManagementReaderRoleId)
  scope: subscription()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', costManagementReaderRoleId)
    principalId: identity.properties.principalId
    principalType: 'ServicePrincipal'
    description: 'Sprint 42 — PO Agent runtime MI queries Cost Management (Class C cost reconciliation, keyless).'
  }
}
```

- [ ] **Step 3: Verify compile**

Run: `az bicep build --file infra/modules/experience-hosting/po-agent-runtime/main.bicep --stdout > $null`
Expected: exit code 0, no errors.

- [ ] **Step 4: Commit**

```bash
git add infra/modules/experience-hosting/po-agent-runtime/main.bicep
git commit -m "feat(infra): grant po-agent-runtime MI subscription Reader + Cost Management Reader"
```

---

## Task 3: Class D — Fabric workspace role grant script

**Files:**
- Create: `data-platform/scripts/fabric/grant_po_agent_workspace_role.py`
- Create: `data-platform/scripts/fabric/tests/test_grant_po_agent_workspace_role.py`

Fabric workspace role assignments are not ARM resources (`POST
/v1/workspaces/{id}/roleAssignments`), so this is a script, not Bicep —
mirrors the `az account get-access-token` auth pattern already proven in
`data-platform/scripts/fabric/add_data_agent_source.py`.

- [ ] **Step 1: Write the failing test**

Create `data-platform/scripts/fabric/tests/test_grant_po_agent_workspace_role.py`:

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from grant_po_agent_workspace_role import ensure_role_assignment


class _FakeResponse:
    def __init__(self, status: int, body: dict):
        self.status = status
        self._body = json.dumps(body).encode("utf-8")

    def read(self):
        return self._body


def test_skips_when_principal_already_has_a_role():
    calls = []

    def fake_get(method, url, token):
        calls.append((method, url))
        return _FakeResponse(200, {"value": [{"principal": {"id": "po-mi-123"}, "role": "Viewer"}]})

    def fake_post(method, url, token, body=None):
        raise AssertionError("must not POST when a role already exists")

    result = ensure_role_assignment(
        workspace_id="f3af9733-9503-4e92-98f9-a901d96f1c87",
        principal_id="po-mi-123",
        role="Viewer",
        token="fake-token",
        http_get=fake_get,
        http_post=fake_post,
    )
    assert result == "already-granted"
    assert len(calls) == 1


def test_grants_role_when_missing():
    posted = {}

    def fake_get(method, url, token):
        return _FakeResponse(200, {"value": [{"principal": {"id": "someone-else"}, "role": "Viewer"}]})

    def fake_post(method, url, token, body=None):
        posted["url"] = url
        posted["body"] = body
        return _FakeResponse(201, {})

    result = ensure_role_assignment(
        workspace_id="f3af9733-9503-4e92-98f9-a901d96f1c87",
        principal_id="po-mi-123",
        role="Viewer",
        token="fake-token",
        http_get=fake_get,
        http_post=fake_post,
    )
    assert result == "granted"
    assert posted["body"]["principal"]["id"] == "po-mi-123"
    assert posted["body"]["role"] == "Viewer"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest data-platform/scripts/fabric/tests/test_grant_po_agent_workspace_role.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'grant_po_agent_workspace_role'`.

- [ ] **Step 3: Write the implementation**

Create `data-platform/scripts/fabric/grant_po_agent_workspace_role.py`:

```python
#!/usr/bin/env python3
"""Sprint 42 ST-2b: grant the PO Agent runtime MI a Fabric workspace role.

Fabric workspace role assignments are a Fabric REST API concept
(``POST /v1/workspaces/{id}/roleAssignments``), not an ARM resource — this is
why the fix is a script, not Bicep. Idempotent: checks the existing role
assignments first and skips the POST if the principal already has any role.
Read-only grant by default (``Viewer``), matching Class D's read-only design
(the Data Agent enforces RLS + the PHI gate; this grant only lets the caller
reach it at all).

Auth: ``az account get-access-token --resource https://api.fabric.microsoft.com``
(same pattern as ``add_data_agent_source.py``). Run ``az login`` first.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import urllib.error
import urllib.request

FABRIC_RESOURCE = "https://api.fabric.microsoft.com"
API = "https://api.fabric.microsoft.com/v1"


def _token() -> str:
    out = subprocess.run(
        ["az", "account", "get-access-token", "--resource", FABRIC_RESOURCE,
         "--query", "accessToken", "-o", "tsv"],
        capture_output=True, text=True, check=True, shell=True,
    )
    return out.stdout.strip()


def _http_get(method: str, url: str, token: str):
    req = urllib.request.Request(url, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    return urllib.request.urlopen(req)


def _http_post(method: str, url: str, token: str, body: dict | None = None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", f"Bearer {token}")
    if data is not None:
        req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req)


def ensure_role_assignment(
    workspace_id: str,
    principal_id: str,
    role: str,
    token: str,
    http_get=_http_get,
    http_post=_http_post,
) -> str:
    """Grant `role` to `principal_id` on the Fabric workspace, unless already granted.

    Returns "already-granted" or "granted".
    """
    list_url = f"{API}/workspaces/{workspace_id}/roleAssignments"
    resp = http_get("GET", list_url, token)
    existing = json.loads(resp.read().decode("utf-8")).get("value", [])
    for assignment in existing:
        if assignment.get("principal", {}).get("id") == principal_id:
            return "already-granted"

    body = {"principal": {"id": principal_id, "type": "ServicePrincipal"}, "role": role}
    http_post("POST", list_url, token, body=body)
    return "granted"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Grant a Fabric workspace role to the PO Agent runtime MI.")
    parser.add_argument("--workspace-id", required=True)
    parser.add_argument("--principal-id", required=True, help="objectId of the po-agent runtime MI (Bicep output principalId).")
    parser.add_argument("--role", default="Viewer")
    args = parser.parse_args(argv)

    token = _token()
    result = ensure_role_assignment(args.workspace_id, args.principal_id, args.role, token)
    print(f"grant_po_agent_workspace_role: {result} (workspace={args.workspace_id}, principal={args.principal_id}, role={args.role})")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest data-platform/scripts/fabric/tests/test_grant_po_agent_workspace_role.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/fabric/grant_po_agent_workspace_role.py data-platform/scripts/fabric/tests/test_grant_po_agent_workspace_role.py
git commit -m "feat(fabric): script to grant PO agent MI a Fabric workspace role (Class D)"
```

---

## Task 4: Guardrail — env-var contract test

**Files:**
- Create: `data-platform/scripts/po-agent/runtime/env_contract.py`
- Modify: `data-platform/scripts/po-agent/runtime/app.py`
- Create: `data-platform/scripts/po-agent/runtime/tests/test_env_contract.py`

- [ ] **Step 1: Write the failing test**

Create `data-platform/scripts/po-agent/runtime/tests/test_env_contract.py`:

```python
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from env_contract import REQUIRED_ENV_VARS

_REPO_ROOT = Path(__file__).resolve().parents[5]
_BICEP_MODULE = _REPO_ROOT / "infra" / "modules" / "experience-hosting" / "po-agent-runtime" / "main.bicep"


def _declared_env_names() -> set[str]:
    result = subprocess.run(
        ["az", "bicep", "build", "--file", str(_BICEP_MODULE), "--stdout"],
        capture_output=True, text=True, check=True, shell=True,
    )
    template = json.loads(result.stdout)
    names: set[str] = set()
    for resource in template["resources"]:
        containers = (
            resource.get("properties", {})
            .get("template", {})
            .get("containers", [])
        )
        for container in containers:
            for env in container.get("env", []):
                names.add(env["name"])
    return names


def test_bicep_declares_every_required_env_var():
    declared = _declared_env_names()
    missing = REQUIRED_ENV_VARS - declared
    assert not missing, f"po-agent-runtime Bicep module is missing env vars: {sorted(missing)}"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_env_contract.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'env_contract'`.

- [ ] **Step 3: Write `env_contract.py`**

Create `data-platform/scripts/po-agent/runtime/env_contract.py`:

```python
"""Sprint 42 ST-4 guardrail: single source of truth for the env vars
`get_tools()` (app.py) reads. A CI test parses the Bicep module and asserts
every name here is declared as a container env var, so the class of drift
that shipped in Sprint 41 (SEARCH_ENDPOINT vs AZURE_SEARCH_ENDPOINT) fails
the build instead of shipping silently.
"""
from __future__ import annotations

REQUIRED_ENV_VARS: set[str] = {
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_SEARCH_ENDPOINT",
    "AZURE_SEARCH_INDEX",
    "FABRIC_DATA_AGENT_ENDPOINT",
    "FABRIC_WORKSPACE_ID",
    "FABRIC_DATA_AGENT_ID",
    "FOUNDRY_PROJECT_ENDPOINT",
    "FOUNDRY_PROJECT_NAME",
}
```

- [ ] **Step 4: Import it from `app.py` (single source of truth, not a copy)**

In `data-platform/scripts/po-agent/runtime/app.py`, add this import near
the top (next to `import orchestrator`):

```python
from env_contract import REQUIRED_ENV_VARS
```

`app.py` does not need to call `REQUIRED_ENV_VARS` anywhere else today —
the import alone proves `env_contract.py` is a real sibling module of
`app.py` (same directory, same `sys.path` story as everything else in
`runtime/`), not a dead file the test imports from a different path.

- [ ] **Step 5: Run the guardrail test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/runtime/tests/test_env_contract.py -v`
Expected: PASS once Task 1's Bicep changes are committed (this test
inherently depends on Task 1 — run Task 1 first if not already done).

- [ ] **Step 6: Run the full po-agent test sweep**

Run: `python -m pytest data-platform/scripts/po-agent/ -v`
Expected: all tests pass (existing + the 2 new suites from Tasks 3-4).

- [ ] **Step 7: Commit**

```bash
git add data-platform/scripts/po-agent/runtime/env_contract.py data-platform/scripts/po-agent/runtime/app.py data-platform/scripts/po-agent/runtime/tests/test_env_contract.py
git commit -m "test(po-agent): guardrail — Bicep env vars must match the runtime contract"
```

---

## Task 5: Class A — real search index (script, per the existing runbook)

`infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md`
already documents this as REST-only (no ARM resource type exists for a
Search index... actually a search index *is* creatable via the Search
data-plane REST API only, not a `Microsoft.Search` ARM sub-resource in this
repo's chosen approach) — this task turns that runbook's Step 1 into a
real, idempotent script instead of copy-pasted `curl`.

**Files:**
- Create: `data-platform/scripts/po-agent/corpus/create_search_index.py`
- Create: `data-platform/scripts/po-agent/corpus/tests/test_create_search_index.py`

- [ ] **Step 1: Write the failing test**

Create `data-platform/scripts/po-agent/corpus/tests/test_create_search_index.py`:

```python
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from create_search_index import build_index_definition, put_index


class _FakeResponse:
    def __init__(self, status: int):
        self.status = status

    def raise_for_status(self):
        pass

    def json(self):
        return {}


def test_build_index_definition_mirrors_grounded_chunk_fields():
    definition = build_index_definition("idx-curavias-corpus-sit")
    field_names = {f["name"] for f in definition["fields"]}
    assert {"classId", "text", "citation", "asOf", "liveness", "status", "confidence", "language"} <= field_names
    key_fields = [f for f in definition["fields"] if f.get("key")]
    assert len(key_fields) == 1
    citation_field = next(f for f in definition["fields"] if f["name"] == "citation")
    assert citation_field["type"] == "Edm.ComplexType"
    citation_subfields = {f["name"] for f in citation_field["fields"]}
    assert {"sourceRef", "anchor"} <= citation_subfields


def test_put_index_calls_expected_url():
    calls = {}

    def fake_request(method, url, headers=None, json=None, timeout=None):
        calls["method"] = method
        calls["url"] = url
        calls["json"] = json
        return _FakeResponse(201)

    put_index(
        endpoint="https://srch-ihzhhpf-sit.search.windows.net",
        index_name="idx-curavias-corpus-sit",
        token_provider=lambda: "fake-token",
        http_request=fake_request,
    )
    assert calls["method"] == "PUT"
    assert calls["url"] == (
        "https://srch-ihzhhpf-sit.search.windows.net/indexes/idx-curavias-corpus-sit"
        "?api-version=2024-05-01-preview"
    )
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_create_search_index.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'create_search_index'`.

- [ ] **Step 3: Write the implementation**

Create `data-platform/scripts/po-agent/corpus/create_search_index.py`:

```python
#!/usr/bin/env python3
"""Sprint 42 ST-3: create the Class A corpus search index (RBAC token, no keys).

Turns Step 1 of
``infra/modules/knowledge-layer/foundry-iq-knowledge-base/knowledge-base-rest.md``
into an idempotent script (a PUT with the same name updates in place) instead
of a manually-run curl command. Field schema mirrors the frozen GroundedChunk
contract (``data/synthetic/schema/grounded-chunk-v1.schema.json``) exactly,
including a nested ``citation`` complex field (``sourceRef``/``anchor``),
matching what ``search_client.py``'s ``query_corpus`` already reads back
unchanged (``hit.get("citation") or {}``) — no changes needed to that
already-tested file.
"""
from __future__ import annotations

import os
from typing import Any

_API_VERSION = "2024-05-01-preview"
_SEARCH_SCOPE = "https://search.azure.com/.default"


def build_index_definition(index_name: str) -> dict[str, Any]:
    return {
        "name": index_name,
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "classId", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "text", "type": "Edm.String", "searchable": True},
            {
                "name": "citation",
                "type": "Edm.ComplexType",
                "fields": [
                    {"name": "sourceRef", "type": "Edm.String", "filterable": True, "retrievable": True},
                    {"name": "anchor", "type": "Edm.String", "retrievable": True},
                ],
            },
            {"name": "asOf", "type": "Edm.DateTimeOffset", "filterable": True, "sortable": True},
            {"name": "liveness", "type": "Edm.String", "filterable": True},
            {"name": "status", "type": "Edm.String", "filterable": True},
            {"name": "confidence", "type": "Edm.Double", "filterable": True, "sortable": True},
            {"name": "language", "type": "Edm.String", "filterable": True, "facetable": True},
        ],
    }


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(_SEARCH_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def put_index(
    endpoint: str,
    index_name: str,
    token_provider=_default_token_provider,
    http_request=_default_http_request,
    timeout: int = 30,
) -> None:
    """Create (or update, idempotent) the corpus search index."""
    url = f"{endpoint.rstrip('/')}/indexes/{index_name}?api-version={_API_VERSION}"
    headers = {
        "Authorization": f"Bearer {token_provider()}",
        "Content-Type": "application/json",
    }
    resp = http_request("PUT", url, headers=headers, json=build_index_definition(index_name), timeout=timeout)
    resp.raise_for_status()


def main() -> int:
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index_name = os.environ.get("AZURE_SEARCH_INDEX", "idx-curavias-corpus-sit")
    put_index(endpoint, index_name)
    print(f"create_search_index: PUT {index_name} on {endpoint} — ok")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_create_search_index.py -v`
Expected: PASS (2 passed).

- [ ] **Step 5: Commit**

```bash
git add data-platform/scripts/po-agent/corpus/create_search_index.py data-platform/scripts/po-agent/corpus/tests/test_create_search_index.py
git commit -m "feat(po-agent): idempotent Class A search index creation script"
```

---

## Task 6: Class A — corpus refresh CLI (ties snapshot -> tag -> publish -> index)

**Files:**
- Create: `data-platform/scripts/po-agent/corpus/refresh_job.py`
- Create: `data-platform/scripts/po-agent/corpus/tests/test_refresh_job.py`

- [ ] **Step 1: Write the failing test**

Create `data-platform/scripts/po-agent/corpus/tests/test_refresh_job.py`:

```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from refresh_job import build_grounded_chunks


def test_build_grounded_chunks_from_snapshot_docs():
    docs = [
        {"source_path": "docs/PRD.md", "text": "# PRD\nSome product content.", "date": "2026-08-01"},
    ]
    chunks = build_grounded_chunks(docs, commit="abc1234")
    assert len(chunks) >= 1
    assert chunks[0]["classId"] == "A"
    assert chunks[0]["citation"]["sourceRef"].startswith("docs/PRD.md@abc1234")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_refresh_job.py -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'refresh_job'`.

- [ ] **Step 3: Write the implementation**

Create `data-platform/scripts/po-agent/corpus/refresh_job.py`:

```python
#!/usr/bin/env python3
"""Sprint 42 ST-3: the Container Apps Job entrypoint (replaces the placeholder
`mcr.microsoft.com/dotnet/samples:aspnetapp` image `caj-po-refresh-*` runs).

Wires the already-tested pipeline: `snapshot.snapshot_tree()` -> per-doc
`chunk_tag.chunk_document()` -> `publish.publish()` (PHI gate + GroundedChunk
mapping, already handles ordering/confidence) -> upload into the real search
index via a raw REST client (mirrors `search_client.py`'s injectable-transport
pattern).
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import chunk_tag
import publish
import snapshot

_API_VERSION = "2024-05-01-preview"
_SEARCH_SCOPE = "https://search.azure.com/.default"


def build_grounded_chunks(docs: list[dict], commit: str) -> list[dict]:
    """snapshot docs -> tagged chunks (all docs) -> published GroundedChunks."""
    tagged: list[dict] = []
    for doc in docs:
        tagged.extend(chunk_tag.chunk_document(doc["source_path"], doc["text"], commit))
        for t in tagged[-1:]:
            t.setdefault("date", doc.get("date"))
    return publish.publish(tagged)


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(_SEARCH_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def upload_chunks(
    endpoint: str,
    index_name: str,
    chunks: list[dict],
    token_provider=_default_token_provider,
    http_request=_default_http_request,
    timeout: int = 60,
) -> int:
    """Upload GroundedChunks into the index (nested citation.sourceRef/anchor
    shape, matching create_search_index.py's build_index_definition schema
    and search_client.py's query_corpus read-back)."""
    if not chunks:
        return 0
    documents = []
    for i, chunk in enumerate(chunks):
        documents.append(
            {
                "@search.action": "mergeOrUpload",
                "id": f"{chunk['citation']['sourceRef']}#{i}".replace("/", "_").replace("@", "_"),
                "classId": chunk["classId"],
                "text": chunk["text"],
                "citation": {
                    "sourceRef": chunk["citation"]["sourceRef"],
                    "anchor": chunk["citation"].get("anchor", ""),
                },
                "asOf": chunk["asOf"],
                "liveness": chunk["liveness"],
                "status": chunk["status"],
                "confidence": chunk["confidence"],
                "language": chunk["language"],
            }
        )
    url = f"{endpoint.rstrip('/')}/indexes/{index_name}/docs/index?api-version={_API_VERSION}"
    headers = {"Authorization": f"Bearer {token_provider()}", "Content-Type": "application/json"}
    resp = http_request("POST", url, headers=headers, json={"value": documents}, timeout=timeout)
    resp.raise_for_status()
    return len(documents)


def main() -> int:
    repo_root = Path(os.environ.get("CORPUS_REPO_ROOT", "/app/repo"))
    commit = snapshot.get_commit(repo_root)
    docs = snapshot.snapshot_tree(repo_root, commit)
    chunks = build_grounded_chunks(docs, commit)

    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    index_name = os.environ.get("AZURE_SEARCH_INDEX", "idx-curavias-corpus-sit")
    count = upload_chunks(endpoint, index_name, chunks)
    print(f"refresh_job: uploaded {count} GroundedChunks (from {len(docs)} source docs) to {index_name}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry
    raise SystemExit(main())
```

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest data-platform/scripts/po-agent/corpus/tests/test_refresh_job.py -v`
Expected: PASS.

- [ ] **Step 5: Run the full po-agent test sweep**

Run: `python -m pytest data-platform/scripts/po-agent/ -v`
Expected: all tests pass.

- [ ] **Step 6: Commit**

```bash
git add data-platform/scripts/po-agent/corpus/refresh_job.py data-platform/scripts/po-agent/corpus/tests/test_refresh_job.py
git commit -m "feat(po-agent): corpus refresh job entrypoint (snapshot -> tag -> publish -> index)"
```

---

## Task 7: Corpus refresh image + CI (mirrors the runtime build workflow)

**Files:**
- Create: `data-platform/scripts/po-agent/corpus/Dockerfile`
- Create: `.github/workflows/po-agent-corpus-build.yml`

- [ ] **Step 1: Write the Dockerfile**

Create `data-platform/scripts/po-agent/corpus/Dockerfile`:

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /app/repo
CMD ["python", "refresh_job.py"]
```

- [ ] **Step 2: Write `requirements.txt`**

Create `data-platform/scripts/po-agent/corpus/requirements.txt`:

```text
azure-identity>=1.17.0
requests>=2.32.0
```

- [ ] **Step 3: Write the CI workflow**

Create `.github/workflows/po-agent-corpus-build.yml` (mirrors
`.github/workflows/po-agent-runtime-build.yml` exactly, scoped to the
`corpus/` subfolder):

```yaml
name: po-agent-corpus-build

# Sprint 42 ST-3 — build + push the po-agent corpus-refresh container image
# on `data-platform/scripts/po-agent/corpus/**` changes.
#
# Scope: build + push only. Bumping `caj-po-refresh-*`'s image is a manual,
# reviewed `az containerapp job update` step (mirrors how Sprint 41 bumped
# the runtime service), not an automatic deploy from this workflow.

on:
  push:
    branches:
      - main
    paths:
      - 'data-platform/scripts/po-agent/corpus/**'
      - '.github/workflows/po-agent-corpus-build.yml'
  workflow_dispatch:

permissions:
  contents: read
  id-token: write

env:
  ACR_LOGIN_SERVER: 'cri75lbu5sj4hza.azurecr.io'
  IMAGE_NAME: 'po-agent-corpus-refresh'

jobs:
  build-and-push:
    name: Build + push po-agent-corpus-refresh image
    runs-on: ubuntu-latest
    environment:
      name: sit

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Azure login (OIDC)
        uses: azure/login@v2
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ vars.AZURE_TENANT_ID }}
          subscription-id: ${{ vars.AZURE_SUBSCRIPTION_ID }}

      - name: ACR login
        shell: bash
        run: |
          set -euo pipefail
          registry_name="${ACR_LOGIN_SERVER%.azurecr.io}"
          az acr login --name "$registry_name"

      - name: Compute image tags
        id: tags
        shell: bash
        run: |
          set -euo pipefail
          short_sha="${GITHUB_SHA::7}"
          {
            echo "sha_tag=$short_sha"
            echo "full_sha=${ACR_LOGIN_SERVER}/${IMAGE_NAME}:${short_sha}"
            echo "full_latest=${ACR_LOGIN_SERVER}/${IMAGE_NAME}:latest"
          } >> "$GITHUB_OUTPUT"

      - name: Docker build
        shell: bash
        run: |
          set -euo pipefail
          docker build \
            -f data-platform/scripts/po-agent/corpus/Dockerfile \
            -t "${{ steps.tags.outputs.full_sha }}" \
            -t "${{ steps.tags.outputs.full_latest }}" \
            data-platform/scripts/po-agent/corpus

      - name: Docker push
        shell: bash
        run: |
          set -euo pipefail
          docker push "${{ steps.tags.outputs.full_sha }}"
          docker push "${{ steps.tags.outputs.full_latest }}"

      - name: Summary
        if: always()
        shell: bash
        run: |
          {
            echo "## po-agent-corpus-refresh image build"
            echo "- Trigger: ${{ github.event_name }}"
            echo "- Commit: ${{ github.sha }} (short: ${{ steps.tags.outputs.sha_tag }})"
            echo "- Tags pushed:"
            echo "  - \`${{ steps.tags.outputs.full_sha }}\`"
            echo "  - \`${{ steps.tags.outputs.full_latest }}\`"
            echo "- Status: ${{ job.status }}"
            echo ""
            echo "Bump caj-po-refresh-ihzhhpf-sit via: az containerapp job update -g rg-ihzhhpf-sit -n caj-po-refresh-ihzhhpf-sit --image ${{ steps.tags.outputs.full_sha }} (approval-gated per AGENTS.md §4)."
          } >> "$GITHUB_STEP_SUMMARY"
```

- [ ] **Step 4: Commit**

```bash
git add data-platform/scripts/po-agent/corpus/Dockerfile data-platform/scripts/po-agent/corpus/requirements.txt .github/workflows/po-agent-corpus-build.yml
git commit -m "ci(po-agent): build + push the corpus-refresh container image"
```

---

## Task 8: Deploy + verify in real SIT (requires `approved-to-apply`)

**This task requires live Azure access and an explicit `approved-to-apply`
comment/message per AGENTS.md §4 before Step 3 (RBAC grant) and Step 6
(image bump) — do not run those two steps without it.**

- [ ] **Step 1: Confirm the module still compiles against real SIT params**

Run:

```powershell
az bicep build --file infra/main.bicep --stdout > $null
echo $LASTEXITCODE
```

Expected: `0`.

- [ ] **Step 2: Surgical env-var + RBAC update (Tasks 1 + 2) — targeted, not full deploy**

Given the documented unrelated drift in `main.bicep` (Sprint 41's own
lesson), deploy only the `po-agent-runtime` module scope:

```powershell
az deployment group create `
  -g rg-ihzhhpf-sit `
  --template-file infra/modules/experience-hosting/po-agent-runtime/main.bicep `
  --parameters location=westus2 nameSuffix=ihzhhpf-sit `
    containerAppEnvironmentId=<real cae-po-ihzhhpf-sit resource id> `
    containerImage=<current running image, from `az containerapp show`> `
    searchEndpoint=https://srch-ihzhhpf-sit.search.windows.net `
    searchServiceId=<real srch-ihzhhpf-sit resource id> `
    fabricDataAgentEndpoint=https://api.fabric.microsoft.com/v1/workspaces/f3af9733-9503-4e92-98f9-a901d96f1c87/aiskills/b2e53c23-182a-452d-9321-e63f6009e80b/aiassistant/openai `
    fabricDataAgentId=b2e53c23-182a-452d-9321-e63f6009e80b `
  --what-if
```

Review the `what-if` output. Confirm it shows only: env-var changes on
`ca-po-ihzhhpf-sit` + `caj-po-refresh-ihzhhpf-sit`, and 2 new role
assignments (Reader, Cost Management Reader). If it shows anything else
(e.g. recreating Cosmos/OpenAI/Key Vault), stop and re-check the params —
do not proceed to apply.

- [ ] **Step 3: Apply (after `approved-to-apply`)**

Re-run the same command from Step 2 without `--what-if`.

- [ ] **Step 4: Grant the Class D Fabric workspace role**

```powershell
python data-platform/scripts/fabric/grant_po_agent_workspace_role.py `
  --workspace-id f3af9733-9503-4e92-98f9-a901d96f1c87 `
  --principal-id <po-agent-runtime MI object id, Bicep output principalId> `
  --role Viewer
```

- [ ] **Step 5: Create the real search index**

```powershell
$env:AZURE_SEARCH_ENDPOINT = "https://srch-ihzhhpf-sit.search.windows.net"
$env:AZURE_SEARCH_INDEX = "idx-curavias-corpus-sit"
python data-platform/scripts/po-agent/corpus/create_search_index.py
```

- [ ] **Step 6: Build + bump the corpus-refresh job image (after `approved-to-apply`)**

Push to `main` (Task 7's workflow builds it automatically), then:

```powershell
az containerapp job update -g rg-ihzhhpf-sit -n caj-po-refresh-ihzhhpf-sit --image cri75lbu5sj4hza.azurecr.io/po-agent-corpus-refresh:<sha>
az containerapp job start -g rg-ihzhhpf-sit -n caj-po-refresh-ihzhhpf-sit
```

- [ ] **Step 7: Verify the index has documents**

```powershell
$token = az account get-access-token --resource https://search.azure.com --query accessToken -o tsv
Invoke-RestMethod -Uri "https://srch-ihzhhpf-sit.search.windows.net/indexes/idx-curavias-corpus-sit/docs/`$count?api-version=2024-05-01-preview" -Headers @{Authorization="Bearer $token"}
```

Expected: a count > 0.

- [ ] **Step 8: Live smoke-test `/answer` again**

```powershell
$appUrl = az containerapp show -g rg-ihzhhpf-sit -n ca-po-ihzhhpf-sit --query properties.configuration.ingress.fqdn -o tsv
Invoke-RestMethod -Method Post -Uri "https://$appUrl/answer" -ContentType "application/json" -Body '{"question":"What is the Curavias platform?","caller":{"persona":"exec","tier":"internal"},"language":"en"}'
```

Expected: `refused: false` with at least one citation, for Class A and/or D.

- [ ] **Step 9: Update the audit findings doc + commit**

Append a "Sprint 42 remediation — live re-test" section to
`docs/superpowers/specs/2026-08-08-sprint-41-ws0-audit-findings.md`
recording the real Step 7/8 output (per §9 Document Versioning — bump
`Version`, this is additive so MINOR).

```bash
git add docs/superpowers/specs/2026-08-08-sprint-41-ws0-audit-findings.md
git commit -m "docs(superpowers): record Sprint 42 remediation live re-test results"
git push origin main
```
