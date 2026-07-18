"""M5 (Option A) - live Fabric Data Agent client (ask_fn for FabricDataAgentAdapter).

The published Fabric Data Agent consumption endpoint
(``https://api.fabric.microsoft.com/v1/workspaces/{ws}/aiskills/{artifact}/aiassistant/openai``)
speaks the OpenAI **Assistants** protocol. This client runs the full
create-assistant -> thread -> message -> run -> poll -> messages sequence and
normalises the Data Agent's free-text answer into
``{"answer": str, "citations": list[str], "refused": bool}`` by extracting
``hcp:*`` / ``dim_*`` citations and detecting the ADR-0016 ``REFUSE:`` gate token.

The binding is region-agnostic: only ``FABRIC_DATA_AGENT_ENDPOINT`` changes when
the layer lifts from westus2 (Slice 0) to eastus2 (Sprint 19). HTTP transport and
token provider are injected so the client is unit-testable without cloud.
Read-only: the Data Agent enforces RLS + PHI gate-3; this client never mutates.
"""

from __future__ import annotations

import re
import time
from typing import Any, Callable, Dict, List

_FABRIC_SCOPE = "https://api.fabric.microsoft.com/.default"
_API_VERSION = "2024-05-01-preview"
_TERMINAL_OK = "completed"
_TERMINAL_BAD = {"failed", "cancelled", "canceled", "expired"}
_CITATION_RE = re.compile(r"(?:hcp:[A-Za-z_][\w/]*|dim_[A-Za-z0-9_]+)")


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token(_FABRIC_SCOPE).token


def _default_http_request(method: str, url: str, headers=None, json=None, timeout=None):
    import requests

    return requests.request(method, url, headers=headers, json=json, timeout=timeout)


def _extract_citations(answer: str) -> List[str]:
    seen: List[str] = []
    for match in _CITATION_RE.findall(answer):
        if match not in seen:
            seen.append(match)
    return seen


class FabricDataAgentClient:
    def __init__(
        self,
        endpoint: str,
        workspace_id: str,
        data_agent_id: str,
        token_provider: Callable[[], str] = _default_token_provider,
        http_request: Callable[..., Any] = _default_http_request,
        timeout: int = 60,
        poll_interval: float = 1.0,
        max_polls: int = 120,
        api_version: str = _API_VERSION,
    ):
        self._endpoint = endpoint.rstrip("/")
        self._workspace_id = workspace_id
        self._data_agent_id = data_agent_id
        self._token_provider = token_provider
        self._http_request = http_request
        self._timeout = timeout
        self._poll_interval = poll_interval
        self._max_polls = max_polls
        self._api_version = api_version

    def _url(self, path: str) -> str:
        return f"{self._endpoint}{path}?api-version={self._api_version}"

    def _call(self, method: str, path: str, headers: Dict[str, str], body=None) -> Dict[str, Any]:
        resp = self._http_request(
            method, self._url(path), headers=headers, json=body, timeout=self._timeout
        )
        resp.raise_for_status()
        return resp.json()

    def ask(self, question: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }

        assistant_id = self._call("POST", "/assistants", headers, {}).get("id")
        thread_id = self._call("POST", "/threads", headers, {}).get("id")
        self._call(
            "POST",
            f"/threads/{thread_id}/messages",
            headers,
            {"role": "user", "content": question},
        )
        run_id = self._call(
            "POST", f"/threads/{thread_id}/runs", headers, {"assistant_id": assistant_id}
        ).get("id")

        status = ""
        for _ in range(self._max_polls):
            run = self._call("GET", f"/threads/{thread_id}/runs/{run_id}", headers)
            status = str(run.get("status", "")).lower()
            if status == _TERMINAL_OK:
                break
            if status in _TERMINAL_BAD:
                raise RuntimeError(f"Fabric Data Agent run {run_id} {status}")
            if self._poll_interval:
                time.sleep(self._poll_interval)
        else:
            raise RuntimeError(f"Fabric Data Agent run {run_id} did not complete (last={status})")

        messages = self._call("GET", f"/threads/{thread_id}/messages", headers)
        answer = self._first_assistant_text(messages)

        refused = "REFUSE:" in answer.upper()
        citations: List[str] = [] if refused else _extract_citations(answer)
        return {"answer": answer, "citations": citations, "refused": refused}

    @staticmethod
    def _first_assistant_text(messages: Dict[str, Any]) -> str:
        for message in messages.get("data") or []:
            if message.get("role") != "assistant":
                continue
            parts = [
                (part.get("text") or {}).get("value", "")
                for part in (message.get("content") or [])
                if part.get("type") == "text"
            ]
            text = "".join(p for p in parts if p).strip()
            if text:
                return text
        return ""
