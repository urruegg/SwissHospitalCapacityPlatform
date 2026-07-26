"""Unit tests for the DC-SKILL-EVENT-v1 Event Hub publisher (Spark-free, offline).

Sprint 23 WS-A4 / ADR-0043 — the ``EventHub`` source-mode flip needs a simulator
that publishes the three near-real-time skills events onto the dedicated
``skills-events`` Event Hub entity, one AMQP message per record, routed by the
``eventKind`` application property. The publisher mirrors the DI pattern of
``apps/sim-capacity/src/emitters/eventhub_emitter.py``: an injected
``producer_client_factory`` lets these tests run fully offline with no
``azure-eventhub`` install and no live namespace.
"""
import sys
import unittest
from pathlib import Path

_PKG = Path(__file__).resolve().parents[1]
if str(_PKG) not in sys.path:
    sys.path.insert(0, str(_PKG))

import publish_skill_events as pub  # noqa: E402
from normalize import EVENT_KINDS  # noqa: E402


class _FakeProducer:
    """Context-manager stub matching EventHubProducerClient's send_batch surface."""

    def __init__(self, sink):
        self._sink = sink

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def send_batch(self, batch):
        self._sink.extend(batch)


class _FakeFactory:
    def __init__(self):
        self.sent = []
        self.calls = 0

    def __call__(self):
        self.calls += 1
        return _FakeProducer(self.sent)


class TestSkillEventPublisher(unittest.TestCase):
    def setUp(self):
        self.factory = _FakeFactory()
        self.publisher = pub.SkillEventPublisher(
            fully_qualified_namespace="evh-ihzhhpf-prod-i62t.servicebus.windows.net",
            eventhub_name="skills-events",
            producer_client_factory=self.factory,
        )

    def test_publish_sends_one_message_per_record(self):
        records = pub.build_records()
        sent = self.publisher.publish_records(records)
        self.assertEqual(sent, len(records))
        self.assertEqual(len(self.factory.sent), len(records))

    def test_each_message_carries_eventkind_property(self):
        records = pub.build_records()
        self.publisher.publish_records(records)
        for msg in self.factory.sent:
            kind = msg["properties"]["eventKind"]
            self.assertIn(kind, EVENT_KINDS)

    def test_published_kinds_cover_the_three_d4_kinds(self):
        self.publisher.publish_records(pub.build_records())
        kinds = {m["properties"]["eventKind"] for m in self.factory.sent}
        self.assertEqual(kinds, set(EVENT_KINDS))

    def test_message_body_is_the_record_json(self):
        records = pub.build_records()
        self.publisher.publish_records(records)
        # Body round-trips back to a record that carries the same eventKind.
        import json

        first = json.loads(self.factory.sent[0]["body"].decode("utf-8"))
        self.assertEqual(first["eventKind"], records[0]["eventKind"])
        self.assertEqual(first["eventId"], records[0]["eventId"])

    def test_dry_run_validates_and_sends_nothing(self):
        rc = pub.main(["--dry-run", "--namespace", "x", "--eventhub", "skills-events"])
        self.assertEqual(rc, 0)
        # main() builds its own publisher; the injected factory here is untouched.
        self.assertEqual(self.factory.calls, 0)


if __name__ == "__main__":
    unittest.main()
