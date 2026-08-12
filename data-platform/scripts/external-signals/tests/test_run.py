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


if __name__ == "__main__":
    unittest.main()
