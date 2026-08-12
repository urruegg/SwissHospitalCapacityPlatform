"""Sprint 44 live path (Slice 3) — read the runner's gold-shaped signals snapshot.

Env-gated (``SIGNALS_SNAPSHOT_URL``) Blob reader with a short TTL cache; maps the
gold rows to ``BoardSignal`` dicts via ``golden.signals``. Returns ``None`` when
disabled (env unset) or the blob is missing/unreadable/malformed, so the golden
service keeps serving its fixtures (the existing ``degraded`` contract). The
fetcher + clock are injected so this is unit-testable offline; the Azure SDK is
imported lazily only inside the default fetcher.

Forward-compatible: swapping ``_default_fetcher`` for a
``FabricDeltaClient.query('gold.ext_fact_signal')`` read serves real OneLake gold
through the same mapping once a Fabric Admin enables external OneLake access.
"""

from __future__ import annotations

import json
import os
import time
from typing import Any, Callable

from golden.signals import gold_rows_to_board_signals


def _default_fetcher() -> bytes:  # pragma: no cover - needs azure SDK + network
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobClient

    url = os.environ["SIGNALS_SNAPSHOT_URL"]
    client = BlobClient.from_blob_url(url, credential=DefaultAzureCredential())
    return client.download_blob().readall()


class SnapshotSource:
    """TTL-cached reader of the gold-shaped signals snapshot Blob."""

    def __init__(
        self,
        *,
        fetcher: Callable[[], bytes] | None = None,
        ttl_seconds: float = 60.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        self._fetcher = fetcher
        self._ttl = ttl_seconds
        self._clock = clock
        self._at = 0.0
        self._cached: list[dict[str, Any]] | None = None
        self._loaded = False

    def _enabled(self) -> bool:
        return self._fetcher is not None or bool(os.environ.get("SIGNALS_SNAPSHOT_URL"))

    def external_signals(self) -> list[dict[str, Any]] | None:
        """Mapped live external ``BoardSignal``s, or ``None`` (=> fixtures) when
        disabled or the snapshot is unreadable/malformed. Cached for ``ttl_seconds``."""
        if not self._enabled():
            return None
        now = self._clock()
        if self._loaded and now - self._at < self._ttl:
            return self._cached
        self._cached = self._load()
        self._at = now
        self._loaded = True
        return self._cached

    def _load(self) -> list[dict[str, Any]] | None:
        try:
            data = json.loads((self._fetcher or _default_fetcher)())
            facts = list(data.get("ext_fact_signal") or [])
            sources = list(data.get("ext_dim_source") or [])
        except Exception:  # noqa: BLE001 - any read/parse failure => serve fixtures
            return None
        return gold_rows_to_board_signals(facts, sources)
