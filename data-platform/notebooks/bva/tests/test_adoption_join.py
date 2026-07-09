#!/usr/bin/env python3
"""Unit tests for the BVA adoption-telemetry join (T4).

Dependency-free. Validates the ``adoption_index_from_signins`` mapping (success
filter, role→capability mapping, distinct-user counting, hospital attribution)
and its wiring into ``fact_value_realization``.

Run with::

    python3 -m unittest discover -s data-platform/notebooks/bva/tests
"""

import datetime as _dt
import json
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE_DIR = os.path.dirname(HERE)
SCRIPTS_DIR = os.path.abspath(os.path.join(MODULE_DIR, "..", "..", "scripts"))
sys.path.insert(0, MODULE_DIR)
sys.path.insert(0, SCRIPTS_DIR)

import bva_transforms as T  # noqa: E402
import bva_synth_focus as bsf  # noqa: E402

FIXTURE = os.path.join(HERE, "fixtures", "adoption_sample.json")
FIXED_END = _dt.date(2026, 6, 30)


def _signins():
    with open(FIXTURE, encoding="utf-8") as fh:
        return json.load(fh)


class AdoptionIndexTests(unittest.TestCase):
    def setUp(self):
        self.signins = _signins()
        self.persona_hospital = {
            "markus.frei@x": "USZ",
            "lea.meier@x": "LUKS",
            "tom.roth@x": "USZ",
        }
        self.index = T.adoption_index_from_signins(self.signins, persona_hospital=self.persona_hospital)

    def test_distinct_users_counted(self):
        # markus.frei signs in twice on BMCA/USZ/2026-06 -> counts once.
        self.assertEqual(self.index[("BMCA", "2026-06", "USZ")], 1)

    def test_second_bmca_user_distinct_hospital(self):
        self.assertEqual(self.index[("BMCA", "2026-06", "LUKS")], 1)

    def test_discharge_role_maps_to_dca(self):
        self.assertEqual(self.index[("DCA", "2026-06", "USZ")], 1)

    def test_admin_role_excluded(self):
        self.assertNotIn("HCC.SuperAdmin", T.DEFAULT_ROLE_CAPABILITY)
        # No CSA/other entry produced from the SuperAdmin sign-in.
        self.assertFalse(any(gk for gk in self.index if gk[0] not in {"BMCA", "DCA"}))

    def test_failed_signin_excluded(self):
        # fail.user has resultType 50126 -> not counted (would have been BMCA/Aggregated).
        self.assertNotIn(("BMCA", "2026-06", "Aggregated"), self.index)

    def test_unknown_user_falls_back_to_aggregated(self):
        idx = T.adoption_index_from_signins(self.signins, persona_hospital={})
        self.assertIn(("BMCA", "2026-06", "Aggregated"), idx)


class ValueRealizationJoinTests(unittest.TestCase):
    def setUp(self):
        focus = bsf.generate_rows(seed=42, days=40, end_date=FIXED_END)
        self.silver = T.to_silver(focus, ingest_utc="2026-06-30T02:00:00Z", source_seed=42)

    def test_join_sets_adoption_count(self):
        base = T.fact_value_realization(self.silver)
        gk = (base[0]["capability_key"], base[0]["month_key"], base[0]["hospital_key"])
        joined = T.fact_value_realization(self.silver, adoption_index={gk: 9})
        by_key = {(r["capability_key"], r["month_key"], r["hospital_key"]): r for r in joined}
        self.assertEqual(by_key[gk]["adoption_count"], 9)

    def test_coverage_non_empty_on_synthetic_backfill(self):
        # Simulate a synthetic backfill: at least one adoption group lands.
        signins = _signins()
        idx = T.adoption_index_from_signins(signins, persona_hospital={"markus.frei@x": "USZ"})
        self.assertGreater(sum(idx.values()), 0)


if __name__ == "__main__":
    unittest.main()
