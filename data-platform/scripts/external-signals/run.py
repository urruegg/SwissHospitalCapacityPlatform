"""Deployable provider-runner entrypoint (Sprint 44 Layer 2).

Discovers every provider manifest, runs each active binding (live -> simulated
fallback via ``providers.runner.run_provider``), wraps the records in a
``DC-EXT-SIGNAL-v1`` envelope, and publishes one envelope per provider to Event
Hub. Scales to zero when idle; loops on ``RUNNER_CADENCE_SECONDS``.

CI never runs this as a process. ``run_once`` is unit-tested with an injected
``emit`` callable and stubbed discover/run functions, fully offline - the Azure
SDK is imported lazily only inside ``_eventhub_emit``.
"""
from __future__ import annotations

import json
import logging
import os
import time
from typing import Callable

import normalize
from providers.registry import discover
from providers.runner import run_provider

logger = logging.getLogger("signal-runner")


def run_once(emit: Callable[[dict], None], *, discover_fn=discover, run_fn=run_provider) -> int:
    """One pass: discover -> run each provider -> emit one envelope per provider
    that produced records. A single failing provider is isolated (logged and
    skipped) so it never blocks the rest. Returns the total records emitted."""
    total = 0
    for spec in discover_fn():
        try:
            records = run_fn(spec)
        except Exception:  # noqa: BLE001 - one bad provider must not stop the rest
            logger.exception("provider %s failed", spec.source_id)
            continue
        if not records:
            continue
        envelope = normalize.envelope(
            records,
            dataset_id=f"DS-EXT-SIGNAL-{spec.source_id}",
            residency=os.environ.get("SIGNAL_RESIDENCY", "CH"),
        )
        emit(envelope)
        total += len(records)
        logger.info(
            "emitted %d records for %s (%s)",
            len(records), spec.source_id, records[0]["provenance"]["activeBinding"],
        )
    return total


def _eventhub_emit() -> Callable[[dict], None]:  # pragma: no cover - needs azure SDK + network
    from azure.eventhub import EventData, EventHubProducerClient
    from azure.identity import DefaultAzureCredential

    ns = os.environ["EVENT_HUB_NAMESPACE"]
    name = os.environ["EVENT_HUB_NAME"]
    fqns = ns if "." in ns else f"{ns}.servicebus.windows.net"
    cred = DefaultAzureCredential()

    def emit(envelope: dict) -> None:
        producer = EventHubProducerClient(
            fully_qualified_namespace=fqns, eventhub_name=name, credential=cred,
        )
        with producer:
            batch = producer.create_batch()
            batch.add(EventData(json.dumps(envelope).encode("utf-8")))
            producer.send_batch(batch)

    return emit


def main() -> int:  # pragma: no cover - container entrypoint
    logging.basicConfig(level=logging.INFO)
    emit = _eventhub_emit()
    cadence = int(os.environ.get("RUNNER_CADENCE_SECONDS", "900"))
    once = os.environ.get("RUNNER_ONCE", "").lower() == "true"
    while True:
        n = run_once(emit)
        logger.info("pass complete: %d records", n)
        if once:
            return 0
        time.sleep(cadence)


if __name__ == "__main__":  # pragma: no cover - container entrypoint
    raise SystemExit(main())
