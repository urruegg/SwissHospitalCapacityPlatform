"""Sprint 43 WS-1 -- live Foundry Agent Service chat model (Option A).

Invokes a registered Foundry Agent (Agent Service "prompt" kind, e.g.
``bmca-agent``) via the Responses API and normalises the reply into the plain
string the ``ChatModel`` protocol expects (see ``orchestrator/dispatch.py``).

Confirmed live contract (Sprint 43 WS-1 Task 0 spike, 2026-08-08):
  POST {project_endpoint}/api/projects/{project_name}/openai/v1/responses
  Body: {"agent_reference": {"name": "<agent>", "type": "agent_reference"},
         "instructions": "<system prompt>", "input": "<grounded question>"}
  Auth: Bearer token, scope https://ai.azure.com/.default (Foundry User role)
  No api-version query param on /v1 paths (returns 400 if present).
  Synchronous -- "status": "completed" in the same response, no polling.

One instance serves every agent-host manifest: the Foundry Agent name is
passed per-call (``agent_name``), not bound at construction, because
``manifest.agent`` is already identical to the registered Foundry Agent name
(AGENTS.md naming convention) for all 8 agent-host agents.

Token provider and HTTP transport are injected (mirrors
``tools/fabric_data_agent_client.py``) so this class is unit-testable without
cloud access.
"""

from __future__ import annotations

from typing import Any, Callable

_FOUNDRY_SCOPE = "https://ai.azure.com/.default"


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token(_FOUNDRY_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _format_grounding(grounding: list[dict[str, Any]]) -> str:
    if not grounding:
        return "No grounding data was retrieved for this question."
    lines = ["Grounding data (Fabric gold tables, one JSON row per line):"]
    lines.extend(f"- {row}" for row in grounding)
    return "\n".join(lines)


class FoundryResponsesChatModel:
    """``ChatModel`` that invokes a registered Foundry Agent via the Responses API."""

    def __init__(
        self,
        project_endpoint: str,
        project_name: str,
        token_provider: Callable[[], str] = _default_token_provider,
        http_request: Callable[..., Any] = _default_http_request,
        timeout: int = 60,
    ):
        self._url = (
            f"{project_endpoint.rstrip('/')}/api/projects/{project_name}/openai/v1/responses"
        )
        self._token_provider = token_provider
        self._http_request = http_request
        self._timeout = timeout

    def complete(
        self,
        system_prompt: str,
        user_prompt: str,
        grounding: list[dict[str, Any]],
        *,
        agent_name: str = "",
    ) -> str:
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        body = {
            "agent_reference": {"name": agent_name, "type": "agent_reference"},
            "instructions": system_prompt,
            "input": f"{_format_grounding(grounding)}\n\nQuestion: {user_prompt}",
        }
        resp = self._http_request(
            "POST", self._url, headers=headers, json=body, timeout=self._timeout
        )
        resp.raise_for_status()
        return self._first_message_text(resp.json())

    @staticmethod
    def _first_message_text(payload: dict[str, Any]) -> str:
        for item in payload.get("output") or []:
            if item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if part.get("type") == "output_text":
                    text = part.get("text", "")
                    if text:
                        return text
        return ""
