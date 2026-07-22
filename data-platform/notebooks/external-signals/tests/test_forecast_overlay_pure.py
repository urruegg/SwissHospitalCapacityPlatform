import importlib.util
import sys
import unittest
from pathlib import Path

NB = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "external-signals"))
import forecast_uplift as fu  # noqa: E402

_ADJ_COLS = {
    "signalId", "hazardType", "severity", "hospital", "ward_id", "specialty_id",
    "canton", "date", "effective", "onset", "expires", "upliftFactor", "baseRequiredCapacity",
    "adjustedRequiredCapacity", "rationale", "rawHash", "connectorVersion", "ingestedAt", "licence",
}
_VIEW_COLS = {"hospital", "ward_id", "date", "baseRequiredCapacity", "adjustedRequiredCapacity", "attribution"}

BASE = [
    {"hospital": "H_ZH", "ward_id": "W_GER", "date": "2026-07-21", "required_capacity": 100.0},
    {"hospital": "H_ZH", "ward_id": "W_ORT", "date": "2026-07-21", "required_capacity": 80.0},
    {"hospital": "H_BE", "ward_id": "W_GER", "date": "2026-07-21", "required_capacity": 60.0},
]
WARD_SPECIALTY = {"W_GER": "geriatrics", "W_ORT": "orthopaedics"}
HOSPITAL_CANTON = {"H_ZH": "ZH", "H_BE": "BE"}
SIGNAL = {
    "signalId": "sig-1", "status": "Actual", "trustTier": "A",
    "hazardType": "heat", "severity": "Severe",
    "effective": "2026-07-20T12:00:00Z",
    "onset": "2026-07-20", "expires": "2026-07-22",
    "region": {"cantons": ["ZH"]},
    "provenance": {"rawHash": "abc", "connectorVersion": "meteoswiss-v1", "ingestedAt": "2026-07-21T06:00:00Z", "licence": "public"},
}


def _load_notebook():
    spec = importlib.util.spec_from_file_location("build_gold_forecast_adjustment", NB / "build_gold_forecast_adjustment.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TestForecastOverlayPure(unittest.TestCase):
    def setUp(self):
        self.mod = _load_notebook()
        self.m = fu.load_uplift_map()

    def test_adjustment_only_matching_canton_and_specialty_with_provenance(self):
        rows = self.mod.build_adjustment_rows(BASE, [SIGNAL], WARD_SPECIALTY, HOSPITAL_CANTON, self.m)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(set(row), _ADJ_COLS)
        self.assertEqual((row["hospital"], row["specialty_id"], row["canton"]), ("H_ZH", "geriatrics", "ZH"))
        self.assertAlmostEqual(row["adjustedRequiredCapacity"], 125.0)
        self.assertEqual(row["rawHash"], "abc")
        self.assertEqual(row["licence"], "public")

    def test_non_actual_or_non_trust_a_signals_are_excluded(self):
        exercise = dict(SIGNAL, status="Exercise")
        trust_b = dict(SIGNAL, trustTier="B")
        system = dict(SIGNAL, status="System")
        self.assertEqual(self.mod.build_adjustment_rows(BASE, [exercise, trust_b, system], WARD_SPECIALTY, HOSPITAL_CANTON, self.m), [])

    def test_adjusted_view_carries_base_adjusted_and_attribution(self):
        second_heat = dict(SIGNAL, signalId="sig-2")
        rows = self.mod.build_adjustment_rows(BASE, [SIGNAL, second_heat], WARD_SPECIALTY, HOSPITAL_CANTON, self.m)
        view = self.mod.build_adjusted_view(BASE, rows, self.m.get("clamp", 2.0))
        ger = next(v for v in view if v["ward_id"] == "W_GER" and v["hospital"] == "H_ZH")
        self.assertEqual(set(ger), _VIEW_COLS)
        self.assertEqual(ger["baseRequiredCapacity"], 100.0)
        self.assertAlmostEqual(ger["adjustedRequiredCapacity"], 156.25)
        self.assertEqual(ger["attribution"], ["sig-1", "sig-2"])
        ort = next(v for v in view if v["ward_id"] == "W_ORT")
        self.assertEqual(ort["adjustedRequiredCapacity"], ort["baseRequiredCapacity"])
        self.assertEqual(ort["attribution"], [])

    def test_duplicate_signal_rows_do_not_double_count(self):
        duplicate = dict(SIGNAL)
        rows = self.mod.build_adjustment_rows(BASE, [SIGNAL, duplicate], WARD_SPECIALTY, HOSPITAL_CANTON, self.m)
        view = self.mod.build_adjusted_view(BASE, rows, self.m.get("clamp", 2.0))
        ger = next(v for v in view if v["ward_id"] == "W_GER" and v["hospital"] == "H_ZH")
        self.assertAlmostEqual(ger["adjustedRequiredCapacity"], 125.0)
        self.assertEqual(ger["attribution"], ["sig-1"])

    def test_ineligible_duplicate_does_not_suppress_actual_signal(self):
        later_test = dict(
            SIGNAL,
            status="Test",
            provenance={**SIGNAL["provenance"], "ingestedAt": "2026-07-21T07:00:00Z"},
        )
        rows = self.mod.build_adjustment_rows(BASE, [SIGNAL, later_test], WARD_SPECIALTY, HOSPITAL_CANTON, self.m)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["signalId"], "sig-1")

    def test_clamp_applies_to_multi_signal_view(self):
        heat_2 = dict(SIGNAL, signalId="sig-3")
        heat_3 = dict(SIGNAL, signalId="sig-4")
        rows = self.mod.build_adjustment_rows(BASE, [SIGNAL, heat_2, heat_3], WARD_SPECIALTY, HOSPITAL_CANTON, self.m)
        view = self.mod.build_adjusted_view(BASE, rows, clamp=1.5)
        ger = next(v for v in view if v["ward_id"] == "W_GER" and v["hospital"] == "H_ZH")
        self.assertAlmostEqual(ger["adjustedRequiredCapacity"], 150.0)

    def test_fabric_sources_use_existing_ward_capacityunit_dim(self):
        self.assertEqual(self.mod.WARD_SPECIALTY_TABLE, "gold.dim_ward_capacityunit")

    def test_gold_writer_always_overwrites_empty_adjustment_fact(self):
        calls = []

        def fake_writer(spark, rows, columns, table_name, schema_kind):
            calls.append((rows, columns, table_name, schema_kind))

        self.mod.write_gold_tables(object(), [], [], fake_writer)
        self.assertEqual(calls[0][2], "gold.ext_fact_forecast_adjustment")
        self.assertEqual(calls[0][0], [])
        self.assertEqual(calls[0][3], "adjustment")


if __name__ == "__main__":
    unittest.main()
