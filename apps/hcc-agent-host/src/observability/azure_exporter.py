"""Sprint 30 M1-observe — runtime Azure Monitor exporter seam.

This is the "real in prod" side of the tracing facade: it mirrors the in-memory
:class:`~observability.tracing.Span` / :class:`~observability.tracing.CustomEvent`
records to Application Insights via OpenTelemetry. It is imported **lazily** by
:func:`observability.tracing.build_exporter_from_env` only when
``APPLICATIONINSIGHTS_CONNECTION_STRING`` is set, so unit tests / CI never load
the optional ``azure-monitor-opentelemetry`` dependency.

The whole SDK path is defensive: any import or export failure degrades to a
no-op rather than crashing an agent turn (observability must never break the
critical path).
"""

from __future__ import annotations

import logging

from observability.tracing import CustomEvent, Span

logger = logging.getLogger(__name__)


class AzureMonitorExporter:  # pragma: no cover - requires the optional azure SDK + network
    """Mirror spans + customEvents to Application Insights via OpenTelemetry.

    Spans are already closed when exported, so each is represented as a short,
    fully-attributed OTel span. Events are emitted as OTel log records whose
    ``microsoft.custom_event.name`` attribute makes them land in the App Insights
    ``customEvents`` table (the Foundry ``trace`` sub-skill contract).
    """

    def __init__(self, connection_string: str) -> None:
        self._ok = False
        self._tracer = None
        self._logger = None
        try:
            from azure.monitor.opentelemetry import configure_azure_monitor
            from opentelemetry import trace

            configure_azure_monitor(connection_string=connection_string)
            self._tracer = trace.get_tracer("hcc-agent-host")
            self._logger = logging.getLogger("hcc-agent-host.customEvents")
            self._ok = True
        except Exception:
            logger.exception(
                "Azure Monitor exporter unavailable; agent-turn traces stay local"
            )

    def export_span(self, span: Span) -> None:
        if not self._ok or self._tracer is None:
            return
        try:
            with self._tracer.start_as_current_span(span.name) as otel_span:
                for key, value in span.attributes.items():
                    otel_span.set_attribute(key, value)
                if span.status == "error":
                    from opentelemetry.trace import Status, StatusCode

                    otel_span.set_status(Status(StatusCode.ERROR))
        except Exception:
            logger.exception("span export failed")

    def export_event(self, event: CustomEvent) -> None:
        if not self._ok or self._logger is None:
            return
        try:
            attrs = {
                "microsoft.custom_event.name": event.name,
                **{f"prop.{k}": v for k, v in event.properties.items()},
                **{f"measure.{k}": v for k, v in event.measurements.items()},
            }
            self._logger.info(event.name, extra=attrs)
        except Exception:
            logger.exception("event export failed")
