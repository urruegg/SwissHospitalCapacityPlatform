"""Sprint 41 WS-RET Task RET.3: real read-only clients for Class B probes.py.

Every client here is read-only by construction (Resource Graph KQL query,
Fabric REST GET, Foundry Agent Service GET). ``probes.py``'s existing
injected ``clients=`` seam is unchanged; this module only supplies the
production values instead of test fakes.

Deviates from the plan's sample in two ways, both verified against the
real code before writing (per the task's diligence requirement):

1. ``probes.py``'s five reference-question probes call
   ``clients["resource_graph"].query(kql)``,
   ``clients["fabric_rest"].list_workspaces()`` and
   ``clients["foundry_agents"].list_agents()`` with **no arguments**
   beyond the fakes in ``liveproof/tests/test_probes.py`` - not
   ``list_agents(project_endpoint)`` as the plan's sample signature had
   it. The Foundry project endpoint is instead baked into the client at
   build time via ``FOUNDRY_PROJECT_ENDPOINT``/``FOUNDRY_PROJECT_NAME``
   env vars, mirroring
   ``data-platform/decision/foundry/live_factory.py``'s
   ``FOUNDRY_SCOPE``/``DEFAULT_ENDPOINT``/``DEFAULT_PROJECT`` (ADR-0032
   SIT defaults) - reused here rather than re-derived.
2. ``azure-mgmt-resourcegraph`` is not an installed dependency in this
   environment (verified: ``ModuleNotFoundError: No module named
   'azure.mgmt'``) - the Resource Graph client here is a raw REST call
   against the ARG ``resources`` endpoint instead of the mgmt SDK,
   matching the injectable-transport pattern
   ``ontology/data_agent.py``'s ``_RawFabricDataAgentClient`` already
   established for this repo.
"""
from __future__ import annotations

import os
from typing import Any

_ARG_API_VERSION = "2021-03-01"
_ARG_SCOPE = "https://management.azure.com/.default"
_FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"

# Foundry Agent Service data plane (ADR-0032 SIT defaults), same constants
# as data-platform/decision/foundry/live_factory.py.
_FOUNDRY_SCOPE = "https://ai.azure.com/.default"
_FOUNDRY_API_VERSION = "2025-05-15-preview"
_DEFAULT_FOUNDRY_ENDPOINT = "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com"
_DEFAULT_FOUNDRY_PROJECT = "ai-ihzhhpf-sit-eastus2-project"


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _token_provider(scope: str):
    """Lazily-evaluated bearer-token provider for ``scope`` (no network at
    construction time - only when the returned callable is invoked)."""

    def _get_token() -> str:
        from azure.identity import DefaultAzureCredential

        return DefaultAzureCredential().get_token(scope).token

    return _get_token


class _ResourceGraphQueryClient:
    """Read-only Azure Resource Graph client exposing only ``query(kql)``."""

    def __init__(
        self,
        subscription_id: str,
        token_provider: Any = None,
        http_request: Any = None,
        timeout: int = 10,
    ) -> None:
        self._subscription_id = subscription_id
        self._token_provider = token_provider or _token_provider(_ARG_SCOPE)
        self._http_request = http_request or _default_http_request
        self._timeout = timeout

    def query(self, kql: str) -> list[dict[str, Any]]:
        url = (
            "https://management.azure.com/providers/Microsoft.ResourceGraph/"
            f"resources?api-version={_ARG_API_VERSION}"
        )
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        body = {"subscriptions": [self._subscription_id], "query": kql}
        resp = self._http_request("POST", url, headers=headers, json=body, timeout=self._timeout)
        resp.raise_for_status()
        return list(resp.json().get("data", []))


class _FabricRestWorkspacesClient:
    """Read-only Fabric REST client exposing only ``list_workspaces()``."""

    def __init__(self, token_provider: Any = None, http_request: Any = None, timeout: int = 10) -> None:
        self._token_provider = token_provider or _token_provider(_FABRIC_SCOPE)
        self._http_request = http_request or _default_http_request
        self._timeout = timeout

    def list_workspaces(self) -> list[dict[str, Any]]:
        url = "https://api.fabric.microsoft.com/v1/workspaces"
        headers = {"Authorization": f"Bearer {self._token_provider()}"}
        resp = self._http_request("GET", url, headers=headers, timeout=self._timeout)
        resp.raise_for_status()
        return list(resp.json().get("value", []))


class _FoundryAgentsListClient:
    """Read-only Foundry Agent Service client exposing only ``list_agents()``.

    The project endpoint/name are resolved at construction time (env vars,
    falling back to the ADR-0032 SIT defaults) so ``list_agents()`` itself
    takes no arguments, matching ``probes.py``'s call site exactly.
    """

    def __init__(
        self,
        endpoint: str = None,
        project: str = None,
        token_provider: Any = None,
        http_request: Any = None,
        timeout: int = 10,
    ) -> None:
        self._endpoint = (
            endpoint or os.environ.get("FOUNDRY_PROJECT_ENDPOINT") or _DEFAULT_FOUNDRY_ENDPOINT
        ).rstrip("/")
        self._project = project or os.environ.get("FOUNDRY_PROJECT_NAME") or _DEFAULT_FOUNDRY_PROJECT
        self._token_provider = token_provider or _token_provider(_FOUNDRY_SCOPE)
        self._http_request = http_request or _default_http_request
        self._timeout = timeout

    def list_agents(self) -> list[dict[str, Any]]:
        url = (
            f"{self._endpoint}/api/projects/{self._project}/agents"
            f"?api-version={_FOUNDRY_API_VERSION}"
        )
        headers = {"Authorization": f"Bearer {self._token_provider()}"}
        resp = self._http_request("GET", url, headers=headers, timeout=self._timeout)
        resp.raise_for_status()
        return list(resp.json().get("value", []))


def build_production_clients(subscription_id: str) -> dict[str, Any]:
    """Build the real read-only Class B client map ``probes.liveProof`` expects.

    Every client is read-only by construction (KQL query / REST GET); no
    client touches the network until a probe actually calls it. See the
    module docstring for the two deviations from the plan's sample.
    """

    return {
        "resource_graph": _ResourceGraphQueryClient(subscription_id),
        "fabric_rest": _FabricRestWorkspacesClient(),
        "foundry_agents": _FoundryAgentsListClient(),
    }
