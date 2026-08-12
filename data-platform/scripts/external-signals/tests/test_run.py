import unittest

import run
from providers.registry import ProviderSpec


def _spec(source_id, mode="simulated", tier="A"):
    return ProviderSpec(
        source_id=source_id, authority=source_id.upper(), trust_tier=tier,
        channel_kind="external", hazard_types=["heat"], default_mode=mode,
        licence="x", provider_version="v",
    )


class TestRunOnce(unittest.TestCase):
    def test_emits_one_dc_ext_signal_envelope_per_provider_with_records(self):
        emitted = []
        records = [{"signalId": "s", "sourceId": "webiq",
                    "provenance": {"activeBinding": "simulated"}}]
        total = run.run_once(
            emitted.append,
            discover_fn=lambda: [_spec("webiq")],
            run_fn=lambda spec: records,
        )
        self.assertEqual(total, 1)
        self.assertEqual(len(emitted), 1)
        self.assertEqual(emitted[0]["contractId"], "DC-EXT-SIGNAL-v1")
        self.assertEqual(emitted[0]["datasetId"], "DS-EXT-SIGNAL-webiq")
        self.assertEqual(emitted[0]["records"], records)

    def test_provider_failure_is_isolated(self):
        emitted = []

        def run_fn(spec):
            if spec.source_id == "bad":
                raise RuntimeError("boom")
            return [{"signalId": "s", "provenance": {"activeBinding": "simulated"}}]

        total = run.run_once(
            emitted.append,
            discover_fn=lambda: [_spec("good"), _spec("bad")],
            run_fn=run_fn,
        )
        self.assertEqual(total, 1)  # only the healthy provider emitted
        self.assertEqual(len(emitted), 1)

    def test_empty_records_emit_nothing(self):
        emitted = []
        total = run.run_once(
            emitted.append,
            discover_fn=lambda: [_spec("quiet")],
            run_fn=lambda spec: [],
        )
        self.assertEqual(total, 0)
        self.assertEqual(emitted, [])

    def test_snapshot_sink_receives_gold_shaped_snapshot_of_all_records(self):
        snapshots = []
        rec_a = {"signalId": "a", "sourceId": "webiq", "hazardType": "epidemic",
                 "provenance": {"activeBinding": "live", "ingestedAt": "t"},
                 "region": {"cantons": ["ZH"]}}
        rec_b = {"signalId": "b", "sourceId": "sed", "hazardType": "earthquake",
                 "provenance": {"activeBinding": "simulated", "ingestedAt": "t"}}
        run.run_once(
            lambda e: None,
            discover_fn=lambda: [_spec("webiq"), _spec("sed")],
            run_fn=lambda spec: [rec_a] if spec.source_id == "webiq" else [rec_b],
            snapshot_sink=snapshots.append,
        )
        self.assertEqual(len(snapshots), 1)
        ids = {f["ext_signal_id"] for f in snapshots[0]["ext_fact_signal"]}
        self.assertEqual(ids, {"a", "b"})

    def test_snapshot_sink_skipped_when_no_records(self):
        snapshots = []
        run.run_once(
            lambda e: None,
            discover_fn=lambda: [_spec("quiet")],
            run_fn=lambda spec: [],
            snapshot_sink=snapshots.append,
        )
        self.assertEqual(snapshots, [])

    def test_snapshot_sink_failure_never_blocks_the_run(self):
        def boom(_snapshot):
            raise RuntimeError("blob down")

        total = run.run_once(
            lambda e: None,
            discover_fn=lambda: [_spec("webiq")],
            run_fn=lambda spec: [{"signalId": "s", "sourceId": "webiq",
                                  "provenance": {"activeBinding": "simulated"}}],
            snapshot_sink=boom,
        )
        self.assertEqual(total, 1)  # Event Hub publish + count unaffected


if __name__ == "__main__":
    unittest.main()
