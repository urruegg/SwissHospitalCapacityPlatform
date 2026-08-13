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


# --- Option C: read the public Event Hub directly (agent-host is in the VNet) ---
# The runner keeps publishing DC-EXT-SIGNAL-v1 envelopes to the Event Hub; here we
# read the recent window, distil the latest record per signal, and reshape into the
# same gold snapshot the Blob path produced, so SnapshotSource + the mapping are
# reused unchanged. Chosen over a Blob/Cosmos bridge because all platform storage is
# private-only + the runner is non-VNet (see the without-admin design doc).

_DATA_MODE = {"live": "Live", "simulated": "Simulated", "internal": "Internal"}


def _records_from_envelopes(bodies: list[bytes]) -> list[dict[str, Any]]:
    """Latest-wins per ``signalId`` across recent envelopes (bodies in enqueue order)."""
    latest: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for body in bodies:
        try:
            envelope = json.loads(body)
        except (ValueError, TypeError):
            continue
        for rec in envelope.get("records") or []:
            sid = rec.get("signalId")
            if not sid:
                continue
            if sid not in latest:
                order.append(sid)
            latest[sid] = rec
    return [latest[sid] for sid in order]


def _gold_rows_from_records(
    records: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Project DC-EXT-SIGNAL records to (ext_fact_signal, ext_dim_source) rows.

    Mirrors ``data-platform/scripts/external-signals/snapshot.build_snapshot`` (the
    two deployables cannot share code)."""
    facts: list[dict[str, Any]] = []
    sources: dict[str, dict[str, Any]] = {}
    for rec in records:
        facts.append({
            "ext_signal_id": rec.get("signalId"),
            "ext_source_id": rec.get("sourceId"),
            "ext_hazard_type": rec.get("hazardType"),
            "ext_severity": rec.get("severity"),
            "ext_cantons": list((rec.get("region") or {}).get("cantons", [])),
            "ext_status": rec.get("status"),
            "ext_web_citations": rec.get("webCitations") or [],
        })
        sid = rec.get("sourceId")
        if sid and sid not in sources:
            prov = rec.get("provenance") or {}
            sources[sid] = {
                "ext_source_id": sid,
                "ext_source_authority": rec.get("sourceAuthority"),
                "ext_trust_tier": rec.get("trustTier"),
                "ext_data_mode": _DATA_MODE.get(prov.get("activeBinding", "live"), "Simulated"),
            }
    return facts, [sources[k] for k in sorted(sources)]


def build_eventhub_snapshot_bytes(events_reader: Callable[[], list[bytes]]) -> bytes:
    """Read recent Event Hub envelopes and emit a gold-shaped snapshot as bytes."""
    facts, srcs = _gold_rows_from_records(_records_from_envelopes(events_reader()))
    return json.dumps({"ext_fact_signal": facts, "ext_dim_source": srcs}).encode("utf-8")


def eventhub_snapshot_fetcher(
    events_reader: Callable[[], list[bytes]] | None = None,
) -> Callable[[], bytes]:
    """A ``SnapshotSource`` fetcher backed by the Event Hub (default reader) or an
    injected reader (tests)."""
    reader = events_reader or _default_eh_events_reader
    return lambda: build_eventhub_snapshot_bytes(reader)


def _default_eh_events_reader() -> list[bytes]:  # pragma: no cover - needs azure SDK + network
    """Bounded read of the recent Event Hub window across all partitions."""
    import threading
    from datetime import datetime, timedelta, timezone

    from azure.eventhub import EventHubConsumerClient
    from azure.identity import DefaultAzureCredential

    ns = os.environ["SIGNALS_EVENTHUB_NAMESPACE"]
    name = os.environ["SIGNALS_EVENTHUB_NAME"]
    consumer_group = os.environ.get("SIGNALS_EVENTHUB_CONSUMER_GROUP", "$Default")
    lookback_min = int(os.environ.get("SIGNALS_EVENTHUB_LOOKBACK_MIN", "30"))
    drain_seconds = float(os.environ.get("SIGNALS_EVENTHUB_DRAIN_SECONDS", "8"))
    fqns = ns if "." in ns else f"{ns}.servicebus.windows.net"

    bodies: list[bytes] = []

    def on_batch(_ctx, events):
        for ev in events:
            bodies.append(ev.body_as_str().encode("utf-8"))

    client = EventHubConsumerClient(
        fully_qualified_namespace=fqns, eventhub_name=name,
        consumer_group=consumer_group, credential=DefaultAzureCredential(),
    )
    start = datetime.now(timezone.utc) - timedelta(minutes=lookback_min)
    with client:
        stopper = threading.Timer(drain_seconds, client.close)
        stopper.start()
        try:
            client.receive_batch(
                on_event_batch=on_batch, starting_position=start,
                starting_position_inclusive=True, max_wait_time=2,
            )
        except Exception:  # noqa: BLE001 - bounded pull; closing the client raises here
            pass
        finally:
            stopper.cancel()
    return bodies


def default_signal_source() -> SnapshotSource:
    """Pick the live-signals source from env: Event Hub (Option C) when
    ``SIGNALS_EVENTHUB_NAMESPACE`` is set, else Blob (``SIGNALS_SNAPSHOT_URL``), else
    disabled (the golden service serves fixtures)."""
    if os.environ.get("SIGNALS_EVENTHUB_NAMESPACE"):
        return SnapshotSource(fetcher=eventhub_snapshot_fetcher())
    return SnapshotSource()
