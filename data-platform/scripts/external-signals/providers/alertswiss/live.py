"""Alertswiss CAP live adapter (network optional; transport is injectable)."""
from __future__ import annotations

from typing import Callable


class LiveBinding:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    def _default_transport(self, url: str) -> dict:  # pragma: no cover - network
        import requests
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def poll(self, transport: Callable[[str], dict] | None = None) -> dict:
        fetch = transport or self._default_transport
        return fetch(self.endpoint)
