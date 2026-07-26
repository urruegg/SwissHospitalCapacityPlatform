"""Sprint 23 WS-A4 / ADR-0043 -- DC-SKILL-EVENT-v1 Event Hub publisher (simulator).

Publishes the three near-real-time skills events onto the dedicated per-domain
``skills-events`` Event Hub entity so the ``EventHub`` source-mode Eventstream
(``es-ihzhhpf-skills-events``) can consume them via the ``cg-skills-eventstream``
consumer group. One AMQP message per record, routed by the ``eventKind``
application property -- the same routing contract the CustomEndpoint lane uses.

There is **no live skills-events publisher yet** (a real HRIS/LMS connector is
planned but not ready); this simulator emits synthetic ``sourceMode=simulated``
envelopes so the PROD-swn EventHub flip can be demonstrated end-to-end under the
ADR-0013 / ADR-0043 synthetic / no-PHI scope. It reuses the record-building logic
of :mod:`skill_events_synth` and mirrors the Managed-Identity + dependency-injection
pattern of ``apps/sim-capacity/src/emitters/eventhub_emitter.py`` so it can be
tested fully offline.

Like the seeder, this is the payload a **Container Apps** job runs -- it is never
wired into a GitHub workflow (NFR-SKILL-001).

Usage::

    cd data-platform/scripts/skills-events
    # Offline validation (no send):
    PYTHONPATH=. python publish_skill_events.py --dry-run
    # Live publish to the SIT Eventstream CustomEndpoint (SAS conn string; the
    # live SIT lane, #379). The string is injected from Key Vault by the Container
    # Apps job as SKILLS_EVENTS_CONNECTION_STRING -- never committed:
    PYTHONPATH=. python publish_skill_events.py \
        --connection-string "Endpoint=sb://...;SharedAccessKey=...;EntityPath=..."
    # Live publish via Managed Identity to the dedicated Event Hub (deferred EH lane):
    PYTHONPATH=. python publish_skill_events.py \
        --namespace evh-ihzhhpf-prod-i62t.servicebus.windows.net \
        --eventhub skills-events
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from typing import Any, Callable, Dict, Iterable, List, Optional

from skill_events_synth import (  # noqa: E402
    DEFAULT_DATASET_ID,
    build_envelope,
    build_records,
    validate,
)

try:  # pragma: no cover -- exercised only where the SDK is installed
    from azure.eventhub import EventData, EventHubProducerClient
    from azure.eventhub.exceptions import EventHubError
    from azure.identity import DefaultAzureCredential

    _AZURE_AVAILABLE = True
except ImportError:
    _AZURE_AVAILABLE = False
    EventHubProducerClient = None  # type: ignore[assignment]
    EventData = None  # type: ignore[assignment]
    EventHubError = Exception  # type: ignore[assignment,misc]
    DefaultAzureCredential = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


class SkillEventPublisher:
    """Publishes DC-SKILL-EVENT-v1 records to Event Hubs, one message per record.

    Mirrors ``apps/sim-capacity/src/emitters/eventhub_emitter.py``: MI auth via
    :class:`~azure.identity.DefaultAzureCredential`, transient-error retry, and a
    ``producer_client_factory`` seam so tests run without the Azure SDK or a live
    namespace.
    """

    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: Any = None,
        max_retries: int = 3,
        producer_client_factory: Optional[Callable[[], Any]] = None,
        connection_string: Optional[str] = None,
    ) -> None:
        self.fqns = fully_qualified_namespace
        self.eventhub_name = eventhub_name
        self.credential = credential
        self.max_retries = max_retries
        self._factory = producer_client_factory
        self.connection_string = connection_string

    def _get_producer(self) -> Any:
        if self._factory is not None:
            return self._factory()
        # CustomEndpoint (Event-Hub-compatible SAS) path — the live SIT lane. The
        # SAS connection string is issued by the Fabric Eventstream CustomEndpoint
        # source and injected at runtime (Key Vault -> Container Apps secret), never
        # committed. EntityPath is normally embedded, so eventhub_name is optional.
        if self.connection_string:
            if EventHubProducerClient is None:
                raise RuntimeError(
                    "azure-eventhub is not installed and no producer_client_factory "
                    "was provided; cannot construct a connection-string producer."
                )
            kwargs: Dict[str, Any] = {}
            if self.eventhub_name:
                kwargs["eventhub_name"] = self.eventhub_name
            return EventHubProducerClient.from_connection_string(
                self.connection_string, **kwargs
            )
        if not _AZURE_AVAILABLE:
            raise RuntimeError(
                "azure-eventhub is not installed and no producer_client_factory "
                "was provided; cannot construct a real producer."
            )
        return EventHubProducerClient(
            fully_qualified_namespace=self.fqns,
            eventhub_name=self.eventhub_name,
            credential=self.credential or DefaultAzureCredential(),
        )

    def _build_event_data(self, record: Dict[str, Any]) -> Any:
        body = json.dumps(record, sort_keys=True).encode("utf-8")
        event_kind = record.get("eventKind", "")
        if _AZURE_AVAILABLE:
            ed = EventData(body=body)
            # Application property drives Eventstream routing per eventKind.
            ed.properties = {"eventKind": event_kind}
            return ed
        # Offline / test path: a shape tests can introspect.
        return {"body": body, "properties": {"eventKind": event_kind}}

    def publish(self, record: Dict[str, Any]) -> None:
        """Publish a single record, retrying transient :class:`EventHubError`."""
        event_data = self._build_event_data(record)
        last_error: Optional[BaseException] = None
        for attempt in range(self.max_retries + 1):
            try:
                producer = self._get_producer()
                with producer:
                    producer.send_batch([event_data])
                return
            except EventHubError as e:  # noqa: PERF203 -- retry loop
                last_error = e
                if attempt == self.max_retries:
                    raise
                logger.warning(
                    "skill-event-publisher retry %d/%d for eventKind=%s: %s",
                    attempt + 1,
                    self.max_retries,
                    record.get("eventKind", ""),
                    e,
                )
        if last_error is not None:  # pragma: no cover -- unreachable
            raise last_error

    def publish_records(self, records: Iterable[Dict[str, Any]]) -> int:
        """Publish every record; return the count published."""
        count = 0
        for rec in records:
            self.publish(rec)
            count += 1
        return count


def _validate_or_die(dataset_id: str) -> List[Dict[str, Any]]:
    doc = build_envelope(dataset_id)
    errors = validate(doc)
    if errors:
        for err in errors:
            print(f"INVALID: {err}", file=sys.stderr)
        raise SystemExit(1)
    return doc["records"]


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Publish synthetic DC-SKILL-EVENT-v1 records to the skills-events Event Hub."
    )
    parser.add_argument("--dataset-id", default=DEFAULT_DATASET_ID)
    parser.add_argument(
        "--namespace",
        default="",
        help="Fully-qualified Event Hubs namespace host (e.g. evh-ihzhhpf-prod-i62t.servicebus.windows.net).",
    )
    parser.add_argument(
        "--eventhub",
        default="skills-events",
        help="Dedicated skills-events Event Hub entity name (per-domain, ADR-0043).",
    )
    parser.add_argument(
        "--connection-string",
        default=os.environ.get("SKILLS_EVENTS_CONNECTION_STRING", ""),
        help=(
            "CustomEndpoint SAS connection string (Event-Hub-compatible) for the live "
            "SIT Eventstream CustomEndpoint source. Defaults to the "
            "SKILLS_EVENTS_CONNECTION_STRING env var (injected from Key Vault by the "
            "Container Apps job). Mutually exclusive alternative to --namespace (MI)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate the envelope against the schema and print the record count; publish nothing.",
    )
    args = parser.parse_args(argv)

    records = _validate_or_die(args.dataset_id)

    if args.dry_run:
        target = args.eventhub or "CustomEndpoint"
        transport = "connection-string" if args.connection_string else "managed-identity"
        print(
            f"OK: {len(records)} DC-SKILL-EVENT-v1 records validated; "
            f"would publish to {target} via {transport} (dry-run, nothing sent)."
        )
        return 0

    if not args.namespace and not args.connection_string:
        print(
            "ERROR: one of --connection-string (CustomEndpoint SAS, live SIT lane) or "
            "--namespace (Event Hub via Managed Identity, deferred EH lane) is required "
            "for a live publish (or use --dry-run).",
            file=sys.stderr,
        )
        return 2

    publisher = SkillEventPublisher(
        fully_qualified_namespace=args.namespace,
        eventhub_name=args.eventhub,
        connection_string=args.connection_string or None,
    )
    sent = publisher.publish_records(records)
    if args.connection_string:
        print(f"OK: published {sent} records to the skills-events CustomEndpoint (SAS).")
    else:
        print(f"OK: published {sent} records to {args.eventhub} on {args.namespace}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
