"""Base connector: shared fetch (optional network) + parse contract."""
from __future__ import annotations

from abc import ABC, abstractmethod

HAZARD_SCENARIO_MAP = {
    "heat": ("F8", 2),
    "flood": ("F8", 2),
    "earthquake": ("F1", 3),
    "epidemic": ("F6", 2),
    "rsv": ("F6", 2),
    "mci": ("F3", 3),
}


class BaseConnector(ABC):
    source_id: str = "base"
    source_authority: str = "unknown"
    licence: str = "unspecified"
    version: str = "0.0.0"

    @abstractmethod
    def parse(self, payload: dict) -> list[dict]:
        """Return a list of DC-EXT-SIGNAL-v1 records from a raw payload."""

    def scenario_for(self, hazard: str) -> tuple[str | None, int | None]:
        return HAZARD_SCENARIO_MAP.get(hazard, (None, None))

    def fetch(self, url: str) -> dict:  # pragma: no cover - network optional
        try:
            import requests
        except ImportError as exc:
            raise RuntimeError("requests not installed; use fixtures offline") from exc
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()
