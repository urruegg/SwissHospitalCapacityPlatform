"""Microsoft Web IQ live binding (POST /v3/search/web, x-apikey header).

Fits the tested provider-runner architecture (mirrors sed/live.py's injectable
transport). Runs one hospital-service-framed query per hazardType and maps the
ranked ``webResults`` into the parser's raw shape.

The API key is read from ``WEBIQ_API_KEY``. When it is absent (CI, or before an
operator provisions the Key Vault secret), ``poll`` raises so the runner falls
back to the simulator (``fallbackMode: simulated``) - the key's presence is the
enablement gate. Query terms are static hazard/region words guarded by
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

    def poll(self, transport: Callable[..., dict] | None = None) -> dict:
        key = os.environ.get(_API_KEY_ENV)
        if not key:
            raise RuntimeError("REFUSE: webiq-live-binding-disabled (WEBIQ_API_KEY unset)")
        fetch = transport or self._default_transport
        cantons = [c.strip() for c in os.environ.get(_REGION_ENV, ",".join(_DEFAULT_CANTONS)).split(",") if c.strip()]
        headers = {"x-apikey": key, "content-type": "application/json"}
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
