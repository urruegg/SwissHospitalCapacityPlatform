"""Event Hubs emitter — publishes envelope JSON via AMQP with Managed Identity (T3.5).

The emitter is thin by design: one envelope per :meth:`send` call, one producer
per attempt, MI credential via :class:`~azure.identity.DefaultAzureCredential`.
Batching optimisation is deferred to a follow-up (see ADR-0015).

Azure imports are guarded so the module can be tested and inspected without
``azure-eventhub`` installed. Tests inject a ``producer_client_factory`` (see
:mod:`tests.test_eventhub_emitter`) to run fully offline.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Callable, Dict, Iterable, Optional

try:  # pragma: no cover — exercised only on machines with the SDK installed
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


class EventHubEmitter:
    """Publishes envelope JSON to Azure Event Hubs via AMQP with MI auth."""

    def __init__(
        self,
        fully_qualified_namespace: str,
        eventhub_name: str,
        credential: Any = None,
        max_retries: int = 3,
        producer_client_factory: Optional[Callable[[], Any]] = None,
    ) -> None:
        self.fqns = fully_qualified_namespace
        self.eventhub_name = eventhub_name
        self.credential = credential
        self.max_retries = max_retries
        # Dependency injection for tests: return a context-manager-compatible
        # producer stub. When None, we build a real EventHubProducerClient.
        self._factory = producer_client_factory

    def _get_producer(self) -> Any:
        if self._factory is not None:
            return self._factory()
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

    def _build_event_data(self, envelope: Dict[str, Any]) -> Any:
        body = json.dumps(envelope).encode("utf-8")
        event_kind = envelope.get("eventKind", "")
        if _AZURE_AVAILABLE:
            ed = EventData(body=body)
            # Application property drives Eventstream routing per eventKind.
            ed.properties = {"eventKind": event_kind}
            return ed
        # Offline / test path: return a shape tests can introspect.
        return {"body": body, "properties": {"eventKind": event_kind}}

    def send(self, envelope: Dict[str, Any]) -> None:
        """Send a single envelope, retrying transient :class:`EventHubError`."""
        event_data = self._build_event_data(envelope)
        last_error: Optional[BaseException] = None
        for attempt in range(self.max_retries + 1):
            try:
                producer = self._get_producer()
                with producer:
                    producer.send_batch([event_data])
                return
            except EventHubError as e:  # noqa: PERF203 — retry loop
                last_error = e
                if attempt == self.max_retries:
                    raise
                logger.warning(
                    "eventhub-emitter retry %d/%d for eventKind=%s: %s",
                    attempt + 1,
                    self.max_retries,
                    envelope.get("eventKind", ""),
                    e,
                )
        if last_error is not None:  # pragma: no cover — unreachable
            raise last_error

    def send_many(self, envelopes: Iterable[Dict[str, Any]]) -> int:
        """Send multiple envelopes; return the count sent. Simple loop for now."""
        count = 0
        for env in envelopes:
            self.send(env)
            count += 1
        return count
