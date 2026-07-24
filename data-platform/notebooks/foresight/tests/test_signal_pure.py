"""Sprint 26 WS-A — Foresight signal projection pure-function tests.

The Foresight ``gold.fact_signal`` table is a Trust-A projection over the
Sprint 21 ``gold.ext_fact_signal`` spine (DC-EXT-SIGNAL-v1), carrying a
deterministic probability and the driver-evidence linkage (evidencedBy ->
hcp:ExternalSignal). Spark-free + deterministic.
"""
import unittest

from _util import load_module

# Enriched ext_fact_signal rows (fact joined with ext_dim_source trust tier).
EXT_SIGNALS = [
    {
        "ext_signal_id": "cap-2026-flu-zh-1",
        "ext_source_id": "bag",
        "ext_hazard_type": "epidemic",
        "ext_severity": "Severe",
        "ext_trust_tier": "A",
        "ext_cantons": ["ZH"],
        "ext_onset": "2026-07-23T00:00:00Z",
        "ext_status": "Actual",
    },
    {
        # Trust-B: must be denied by the deny-by-default Trust-A gate.
        "ext_signal_id": "cap-2026-noise-1",
        "ext_source_id": "social",
        "ext_hazard_type": "rumour",
        "ext_severity": "Minor",
        "ext_trust_tier": "B",
        "ext_cantons": ["ZH"],
        "ext_onset": "2026-07-23T00:00:00Z",
        "ext_status": "Actual",
    },
]


class TestForesightSignal(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("build_gold_signal.py")

    def test_probability_is_deterministic_severity_map(self):
        self.assertEqual(self.mod.signal_probability("Extreme"), 0.95)
        self.assertEqual(self.mod.signal_probability("Severe"), 0.90)
        self.assertEqual(self.mod.signal_probability("Moderate"), 0.60)
        self.assertEqual(self.mod.signal_probability("Minor"), 0.30)
        # Unknown severity falls back to a conservative low probability.
        self.assertEqual(self.mod.signal_probability("Unknown"), 0.10)

    def test_deny_by_default_keeps_only_trust_a(self):
        rows = self.mod.foresight_signals(EXT_SIGNALS)
        ids = {r["signal_id"] for r in rows}
        self.assertIn("cap-2026-flu-zh-1", ids)
        self.assertNotIn("cap-2026-noise-1", ids)

    def test_projection_carries_trust_and_probability(self):
        rows = self.mod.foresight_signals(EXT_SIGNALS)
        flu = next(r for r in rows if r["signal_id"] == "cap-2026-flu-zh-1")
        self.assertEqual(flu["trust_tier"], "A")
        self.assertEqual(flu["probability"], 0.90)
        self.assertEqual(flu["hazard_type"], "epidemic")
        self.assertEqual(flu["source_id"], "bag")
        self.assertEqual(flu["evidences_factor"], "seasonality")

    def test_deterministic(self):
        self.assertEqual(
            self.mod.foresight_signals(EXT_SIGNALS),
            self.mod.foresight_signals(EXT_SIGNALS),
        )

    def test_empty_input_empty_output(self):
        self.assertEqual(self.mod.foresight_signals([]), [])


if __name__ == "__main__":
    unittest.main()
