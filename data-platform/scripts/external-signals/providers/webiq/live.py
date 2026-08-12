"""Microsoft Web IQ live binding (POST /v3/search/web).

Fits the tested provider-runner architecture (mirrors sed/live.py's injectable
transport). Runs one hospital-service-framed query per hazardType and maps the
ranked ``webResults`` into the parser's raw shape.

Auth (see ``_auth_header``): **Entra ID (keyless, managed identity)** is the
platform-aligned primary path - the runner UAMI's client id is bound in the Web
IQ portal and it acquires an app-only token for
``https://api.microsoft.ai/.default`` (``Authorization: Bearer``), enabled with
``WEBIQ_ENTRA_ENABLED=true``. An ``x-apikey`` from ``WEBIQ_API_KEY`` is honoured
as a local/eval fallback. With neither configured, ``poll`` raises so the runner
falls back to the simulator (``fallbackMode: simulated``) - config presence is
the enablement gate. Query terms are static hazard/region words guarded by
``parse.build_query`` (ADR-0016: no PHI ever leaves in an outbound query).
Returned web content is untrusted: only typed fields are extracted, never
forwarded free text (ADR-0060, NFR-SIG-001).
"""
from __future__ import annotations

import os
from typing import Callable

from . import parse

# Hospital-service-framed query terms per hazardType (Sprint 44 Q1 scope). The
# query DEFINES the hazard, so no content classifier is needed - a result for
# the epidemic query is an epidemic signal by construction.
_QUERIES = {
    "epidemic": ["hospital", "emergency", "respiratory", "infection", "outbreak", "surge", "Switzerland"],
    "heat": ["heatwave", "health", "warning", "hospital", "emergency", "Switzerland"],
    "mass-casualty": ["major", "accident", "mass", "casualty", "incident", "hospital", "Switzerland"],
    "air-quality": ["air", "pollution", "smog", "respiratory", "health", "advisory", "Switzerland"],
}
_API_KEY_ENV = "WEBIQ_API_KEY"
_ENTRA_ENV = "WEBIQ_ENTRA_ENABLED"
_SCOPE = "https://api.microsoft.ai/.default"  # Web IQ Entra ID app-only token scope
_REGION_ENV = "WEBIQ_REGION_CANTONS"
_DEFAULT_CANTONS = ["ZH", "LU", "SZ"]  # in-scope MVP hospital cantons (USZ / LUKS / SZB)


def _confidence(n: int) -> float:
    """Result count -> confidence. n>=2 clears the parse Actual threshold (0.6);
    a single thin result stays below it and is quarantined."""
    return round(min(0.5 + 0.05 * n, 0.9), 2)


class LiveBinding:
    def __init__(self, endpoint: str, hazard_types: list[str] | None = None):
        self.endpoint = endpoint
        self.hazard_types = hazard_types or list(_QUERIES)

    def _default_transport(self, url: str, body: dict, headers: dict) -> dict:  # pragma: no cover - network
        import requests

        resp = requests.post(url, json=body, headers=headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def _auth_header(self) -> dict:
        """Entra ID (keyless, managed identity) is the platform-aligned primary
        auth - the runner UAMI's client id is bound in the Web IQ portal and it
        acquires an app-only token for `_SCOPE`. An `x-apikey` is honoured as a
        fallback for local/eval. Neither configured -> raise so the runner falls
        back to the simulator (config presence is the enablement gate)."""
        key = os.environ.get(_API_KEY_ENV)
        if key:
            return {"x-apikey": key, "content-type": "application/json"}
        if os.environ.get(_ENTRA_ENV, "").lower() == "true":
            from azure.identity import DefaultAzureCredential

            token = DefaultAzureCredential().get_token(_SCOPE).token
            return {"Authorization": f"Bearer {token}", "content-type": "application/json"}
        raise RuntimeError(
            "REFUSE: webiq-live-disabled (set WEBIQ_ENTRA_ENABLED=true for keyless MI auth, or WEBIQ_API_KEY)"
        )

    def poll(self, transport: Callable[..., dict] | None = None) -> dict:
        fetch = transport or self._default_transport
        # Real path acquires + validates auth once (raises -> runner falls back);
        # an injected transport (tests) bypasses auth entirely.
        headers = {"content-type": "application/json"} if transport else self._auth_header()
        cantons = [c.strip() for c in os.environ.get(_REGION_ENV, ",".join(_DEFAULT_CANTONS)).split(",") if c.strip()]
        results = []
        for hazard in self.hazard_types:
            terms = _QUERIES.get(hazard)
            if not terms:
                continue
            query = parse.build_query(terms)  # PHI guard
            body = {"query": query, "maxResults": 10, "contentFormat": "passage", "maxLength": 5000}
            resp = fetch(self.endpoint, body, headers)
            web_results = resp.get("webResults", []) if isinstance(resp, dict) else []
            if not web_results:
                continue
            top = web_results[0]
            results.append({
                "title": top.get("title", ""),
                "uri": top.get("url", ""),
                "publishedAt": top.get("crawledAt", ""),
                "hazard": hazard,
                "cantons": cantons,
                "confidence": _confidence(len(web_results)),
                "snippet": (top.get("content", "") or "")[:280],
            })
        return {"results": results}
