"""Live Foundry registration factory for the decision-tier tool (Sprint 26 WS-C).

Concrete implementation of the ``registration_factory`` seam that
:func:`foundry.register_decision_tier.apply` invokes when it runs **in-VNet**.
Following the injectable-transport pattern of
``apps/hcc-agent-host/src/tools/fabric_data_agent_client.py``, both the bearer
``token_provider`` and the ``http_request`` transport are injected, so the whole
REST sequence is unit-testable without cloud and the real Foundry **Agent
Service** API is touched only when the factory is actually called.

The Foundry project is eastus2 (ADR-0032). The eight platform agents are
versioned Foundry *agent* objects (not OpenAI Assistants): the base endpoint is
``https://<account>.services.ai.azure.com/api/projects/<project>/agents`` and
auth is a bearer token for ``https://ai.azure.com/.default`` (RBAC: ``Foundry
User`` / ``Foundry Project Manager`` — **not** ``Cognitive Services User``,
which returns 401). Agents are immutable and versioned: an update is a
``POST /agents/{name}`` carrying the **complete** definition, which the service
turns into a new version and auto-promotes to ``latest`` only when the
definition actually changed. ``decision_tier_coordination`` is registered as a
native **function** tool (flat Responses-API shape) appended to the agent's
existing ``definition.tools``, and the role binding is carried in version-level
``metadata`` (string values only).
"""
from __future__ import annotations

import copy
from typing import Any, Callable, Dict, List, Optional

#: OAuth scope for the Foundry Agent Service data plane (ai.azure.com audience).
FOUNDRY_SCOPE = "https://ai.azure.com/.default"

#: Agents data-plane api-version (ADR-0032 / AGENTS.md §2).
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

    Deterministic, no side effects. Emits the **flat** Responses-API function
    tool shape used by the Foundry Agent Service (``type``/``name``/
    ``description``/``parameters`` at the top level) — NOT the nested
    ``{"type": "function", "function": {...}}`` Assistants shape. The
    role/catalog binding is set at the version ``metadata`` level by the factory.
    """
    role = tool["role"]
    return {
        "type": "function",
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
    (``{"foundryAgent", "tool", "region"}``) and: reads the agent's latest
    version, appends the deterministic function tool to a *copy* of its
    definition if absent (idempotent), merges the decision-tier metadata, and
    POSTs the update — which the service turns into a new immutable version.
    Returns a registration record. Raises ``RuntimeError`` when the named agent
    does not exist.
    """
    base = f"{endpoint.rstrip('/')}/api/projects/{project}/agents"

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

    def _latest_version(agent: Dict[str, Any]) -> Dict[str, Any]:
        return (agent.get("versions") or {}).get("latest") or {}

    def factory(payload: Dict[str, Any]) -> Dict[str, Any]:
        agent_name = payload["foundryAgent"]
        tool = payload["tool"]
        role = tool["role"]

        try:
            agent = _call("GET", f"/{agent_name}")
        except Exception as exc:  # 404 (or any read failure) -> not registrable
            raise RuntimeError(f"Foundry agent not found: {agent_name!r}") from exc

        latest = _latest_version(agent)
        # Echo the complete current definition so the new version preserves the
        # model, instructions, reasoning and every existing tool.
        definition = copy.deepcopy(latest.get("definition") or {})
        existing_tools: List[Dict[str, Any]] = list(definition.get("tools") or [])
        present = {
            t.get("name")
            for t in existing_tools
            if t.get("type") == "function"
        }
        already = _tool_name(role) in present
        if not already:
            existing_tools = existing_tools + [build_function_tool(tool)]
        definition["tools"] = existing_tools

        # Preserve existing version metadata; add the decision-tier binding.
        metadata = {k: str(v) for k, v in (latest.get("metadata") or {}).items()}
        metadata["decision_tier_role"] = role
        metadata["decision_tier_lever_catalog"] = str(tool.get("leverCatalog", ""))

        updated = _call("POST", f"/{agent_name}", {"definition": definition, "metadata": metadata})
        new_latest = _latest_version(updated)

        return {
            "agentName": agent_name,
            "agentVersion": new_latest.get("version"),
            "toolName": _tool_name(role),
            "toolAlreadyPresent": already,
            "toolCount": len(existing_tools),
            "region": payload["region"],
            "status": "registered",
        }

    return factory
