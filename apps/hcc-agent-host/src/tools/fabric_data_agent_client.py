"""M5 — live Fabric Data Agent client (ask_fn for FabricDataAgentAdapter).

Calls the published Data Agent consumption endpoint (confirmed in plan M3 Step 4)
and normalises the response to {"answer", "citations", "refused"}. HTTP + token
provider are injected so the client is unit-testable without cloud. Read-only.
"""

from __future__ import annotations

from typing import Any, Callable, Dict


def _default_token_provider() -> str:
    from azure.identity import DefaultAzureCredential

    cred = DefaultAzureCredential()
    return cred.get_token("https://api.fabric.microsoft.com/.default").token


def _default_http_post(url: str, json: Dict[str, Any], headers: Dict[str, str], timeout: int):
    import requests

    return requests.post(url, json=json, headers=headers, timeout=timeout)


class FabricDataAgentClient:
    def __init__(
        self,
        endpoint: str,
        workspace_id: str,
        data_agent_id: str,
        token_provider: Callable[[], str] = _default_token_provider,
        http_post: Callable[..., Any] = _default_http_post,
        timeout: int = 60,
    ):
        self._endpoint = endpoint
        self._workspace_id = workspace_id
        self._data_agent_id = data_agent_id
        self._token_provider = token_provider
        self._http_post = http_post
        self._timeout = timeout

    def ask(self, question: str) -> Dict[str, Any]:
        headers = {
            "Authorization": f"Bearer {self._token_provider()}",
            "Content-Type": "application/json",
        }
        body = {
            "workspaceId": self._workspace_id,
            "dataAgentId": self._data_agent_id,
            "question": question,
        }
        resp = self._http_post(self._endpoint, json=body, headers=headers, timeout=self._timeout)
        resp.raise_for_status()
        data = resp.json()
        return {
            "answer": data.get("answer", ""),
            "citations": list(data.get("citations", [])),
            "refused": bool(data.get("refused", False)),
        }
