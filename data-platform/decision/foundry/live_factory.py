"""Live Foundry registration factory for the decision-tier tool (Sprint 26 WS-C).

Concrete implementation of the ``registration_factory`` seam that
:func:`foundry.register_decision_tier.apply` invokes when it runs **in-VNet**.
Following the injectable-transport pattern of
``apps/hcc-agent-host/src/tools/fabric_data_agent_client.py``, both the bearer
``token_provider`` and the ``http_request`` transport are injected, so the whole
REST sequence is unit-testable without cloud and the real Foundry Agents
(Assistants protocol) API is touched only when the factory is actually called.

The Foundry project is eastus2 (ADR-0032). The assistants base endpoint is
``https://<account>.services.ai.azure.com/api/projects/<project>/assistants``;
auth is a bearer token for ``https://cognitiveservices.azure.com/.default``
(RBAC: ``Cognitive Services User``). ``decision_tier_coordination`` is not a
native Foundry tool type, so the coordination runtime is registered as a native
**function** tool and the role binding is carried in assistant-level
``metadata`` (string values only, per the Assistants object contract).
"""
from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

#: OAuth scope for the Foundry data-plane (Assistants) API.
FOUNDRY_SCOPE = "https://cognitiveservices.azure.com/.default"

#: Assistants data-plane api-version (ADR-0032 / AGENTS.md §2).
DEFAULT_API_VERSION = "2025-05-15-preview"

#: SIT control-plane account + project (ADR-0032).
DEFAULT_ENDPOINT = "https://ai-ihzhhpf-sit-eastus2.services.ai.azure.com"
DEFAULT_PROJECT = "ai-ihzhhpf-sit-eastus2-project"


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    return DefaultAzureCredential().get_token(FOUNDRY_SCOPE).token


def _default_http_request(method, url, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _tool_name(role: str) -> str:
    return f"decision_tier_coordination_{role}"


def build_function_tool(tool: Dict[str, Any]) -> Dict[str, Any]:
    """Translate a decision-tier plan ``tool`` block into a native function tool.

    Deterministic, no side effects. Only the native ``name`` / ``description`` /
    ``parameters`` keys are emitted — Foundry rejects unknown keys inside a
    function tool, so the role/catalog binding is set at the assistant
    ``metadata`` level by the factory instead.
    """
    role = tool["role"]
    return {
        "type": "function",
        "function": {
            "name": _tool_name(role),
            "description": (
                "Deterministic decision-tier coordination runtime: open a plan, "
                "propose a lever-backed action with forecast-grounded expected "
                "impact, and drive the HITL approve/live-sync thread for the "
                f"{role} role. Applying a proposed action is gated by the "
                "'approved-to-apply' human confirmation (AGENTS.md \u00a74)."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["open_plan", "propose_action", "approve_action"],
                    },
                    "leverId": {"type": "string"},
                    "episodeKey": {"type": "string"},
                    "approver": {"type": "string"},
                },
                "required": ["operation"],
            },
        },
    }


def make_registration_factory(
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    project: str = DEFAULT_PROJECT,
    api_version: str = DEFAULT_API_VERSION,
    token_provider: Callable[[], str] = _default_token_provider,
    http_request: Callable[..., Any] = _default_http_request,
    timeout: int = 60,
) -> Callable[[Dict[str, Any]], Dict[str, Any]]:
    """Return a ``registration_factory`` closure for the given Foundry project.

    The returned callable takes the ``apply`` payload
    (``{"foundryAgent", "tool", "region"}``) and: resolves the assistant by
    name, appends the deterministic function tool if absent (idempotent), sets
    the decision-tier metadata, and POSTs the modify. Returns a registration
    record. Raises ``RuntimeError`` when the named assistant does not exist.
    """
    base = f"{endpoint.rstrip('/')}/api/projects/{project}/assistants"

    def _url(path: str) -> str:
        return f"{base}{path}?api-version={api_version}"

    def _headers() -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token_provider()}",
            "Content-Type": "application/json",
        }

    def _call(method: str, path: str, body: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        resp = http_request(method, _url(path), headers=_headers(), json=body, timeout=timeout)
        resp.raise_for_status()
        return resp.json()

    def _find_assistant(name: str) -> Optional[Dict[str, Any]]:
        listing = _call("GET", "")
        for item in listing.get("data") or []:
            if item.get("name") == name:
                return item
        return None

    def factory(payload: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = payload["foundryAgent"]
        tool = payload["tool"]
        role = tool["role"]

        assistant = _find_assistant(agent_name)
        if assistant is None:
            raise RuntimeError(f"Foundry assistant not found: {agent_name!r}")
        assistant_id = assistant["id"]

        existing_tools: List[Dict[str, Any]] = list(assistant.get("tools") or [])
        present = {
            t.get("function", {}).get("name")
            for t in existing_tools
            if t.get("type") == "function"
        }
        already = _tool_name(role) in present
        merged = existing_tools if already else existing_tools + [build_function_tool(tool)]

        metadata = {k: str(v) for k, v in (assistant.get("metadata") or {}).items()}
        metadata["decision_tier_role"] = role
        metadata["decision_tier_lever_catalog"] = str(tool.get("leverCatalog", ""))

        _call("POST", f"/{assistant_id}", {"tools": merged, "metadata": metadata})

        return {
            "assistantId": assistant_id,
            "toolName": _tool_name(role),
            "toolAlreadyPresent": already,
            "toolCount": len(merged),
            "region": payload["region"],
            "status": "registered",
        }

    return factory
