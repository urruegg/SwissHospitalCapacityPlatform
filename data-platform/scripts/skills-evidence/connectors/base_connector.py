"""Base connector: shared metadata + parse contract for skills evidence.

Mirrors ``external-signals/connectors/base_connector.py``. Every adapter is
simulated now (``source_mode = "simulated"``) and exposes the same surface, so a
real SuccessFactors / LMS / Skills-Manager / Work-ID API can slot in later by
setting ``source_mode = "live"`` and implementing ``fetch`` -- without touching
the ontology or the DC-SKILL-EVIDENCE-v1 contract.
"""
from __future__ import annotations

from abc import ABC, abstractmethod


class BaseConnector(ABC):
    source_id: str = "base"
    source_authority: str = "unknown"
    external_system: str = "base"
    licence: str = "synthetic"
    version: str = "0.0.0"
    source_mode: str = "simulated"
    trust_tier: str = "A"

    @abstractmethod
    def parse(self, payload: dict) -> list[dict]:
        """Return a list of DC-SKILL-EVIDENCE-v1 records from a raw payload."""

    def fetch(self, url: str) -> dict:  # pragma: no cover - network optional
        """Real-API hook. Unused while simulated; kept for drop-in live mode."""
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests not installed; use fixtures offline") from exc
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
