"""Sprint 26 WS-A — Foresight occupancy-forecast + driver pure-function tests.

Spark-free, deterministic. Defines the generator API before implementation
(TDD). Mirrors the external-signals offline test posture.
"""
import datetime as dt
import unittest

from _util import load_module

PRODUCED_AT = dt.datetime(2026, 7, 23, 8, 0, 0, tzinfo=dt.timezone.utc)

# A minimal deterministic ward baseline: Medicine A is the golden-thread ward
# (breaches capacity within 72h under +6 admissions / -2 discharges).
WARDS = [
    {
        "ward_id": "Medicine A",
        "hospital_id": "H_USZ",
        "bed_capacity": 50,
        "baseline_occupied": 51,
        "admissions_72h": 6,
        "discharges_72h": 2,
        "transfers_72h": 0,
        "seasonality_72h": 0,
        "seasonality_note": "flu season",
        "signal_id": "cap-2026-flu-zh-1",
    },
    {
        "ward_id": "Surgery B",
        "hospital_id": "H_USZ",
        "bed_capacity": 40,
        "baseline_occupied": 30,
        "admissions_72h": 3,
        "discharges_72h": 4,
        "transfers_72h": 0,
        "seasonality_72h": 0,
        "seasonality_note": None,
        "signal_id": None,
    },
]


class TestOccupancyForecast(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("build_gold_forecast.py")

    def test_deterministic(self):
        a = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        b = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        self.assertEqual(a, b)

    def test_row_per_ward_per_horizon(self):
        rows = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        # 2 wards × (0..72 inclusive) = 2 × 73
        self.assertEqual(len(rows), 2 * 73)
        horizons = {r["horizonH"] for r in rows if r["wardId"] == "Medicine A"}
        self.assertEqual(horizons, set(range(0, 73)))

    def test_forecast_id_pattern(self):
        rows = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        import re
        for r in rows:
            self.assertRegex(r["forecastId"], r"^OF-[A-Z0-9-]+$")

    def test_baseline_occupancy_and_breach(self):
        rows = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        med_h0 = next(r for r in rows if r["wardId"] == "Medicine A" and r["horizonH"] == 0)
        self.assertEqual(med_h0["forecastOccupiedBeds"], 51)
        self.assertAlmostEqual(med_h0["forecastOccupancyPct"], 102.0, places=3)
        self.assertTrue(med_h0["breach"])
        # By 72h net demand grows (+6 -2) so it stays breached.
        med_h72 = next(r for r in rows if r["wardId"] == "Medicine A" and r["horizonH"] == 72)
        self.assertGreater(med_h72["forecastOccupiedBeds"], 51)
        self.assertTrue(med_h72["breach"])

    def test_ci_bounds_widen_with_horizon(self):
        rows = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        med = [r for r in rows if r["wardId"] == "Medicine A"]
        for r in med:
            self.assertLessEqual(r["lowerCi"], r["forecastOccupiedBeds"])
            self.assertGreaterEqual(r["upperCi"], r["forecastOccupiedBeds"])
        h0 = next(r for r in med if r["horizonH"] == 0)
        h72 = next(r for r in med if r["horizonH"] == 72)
        spread0 = h0["upperCi"] - h0["lowerCi"]
        spread72 = h72["upperCi"] - h72["lowerCi"]
        self.assertGreater(spread72, spread0)


class TestForecastDrivers(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("build_gold_forecast.py")

    def test_four_factors_per_ward_horizon(self):
        drivers = self.mod.build_forecast_drivers(WARDS, PRODUCED_AT)
        med72 = [d for d in drivers if d["wardId"] == "Medicine A" and d["horizonH"] == 72]
        self.assertEqual(
            {d["factor"] for d in med72},
            {"forecast_admissions", "planned_discharges", "transfers", "seasonality"},
        )

    def test_driver_deltas_reconcile_to_net_forecast_change(self):
        """Sum of driver deltas at a horizon == occupied(h) - baseline_occupied."""
        forecast = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        drivers = self.mod.build_forecast_drivers(WARDS, PRODUCED_AT)
        for ward in WARDS:
            for h in (0, 24, 48, 72):
                fc = next(
                    r for r in forecast
                    if r["wardId"] == ward["ward_id"] and r["horizonH"] == h
                )
                net = round(fc["forecastOccupiedBeds"] - ward["baseline_occupied"], 3)
                total = round(sum(
                    d["delta"] for d in drivers
                    if d["wardId"] == ward["ward_id"] and d["horizonH"] == h
                ), 3)
                self.assertAlmostEqual(net, total, places=3,
                                       msg=f"{ward['ward_id']} h={h}: {net} != {total}")

    def test_admissions_and_discharges_signs(self):
        drivers = self.mod.build_forecast_drivers(WARDS, PRODUCED_AT)
        med72 = {d["factor"]: d for d in drivers
                 if d["wardId"] == "Medicine A" and d["horizonH"] == 72}
        self.assertGreater(med72["forecast_admissions"]["delta"], 0)
        self.assertLess(med72["planned_discharges"]["delta"], 0)

    def test_seasonality_driver_links_signal(self):
        drivers = self.mod.build_forecast_drivers(WARDS, PRODUCED_AT)
        med_season = next(
            d for d in drivers
            if d["wardId"] == "Medicine A" and d["factor"] == "seasonality" and d["horizonH"] == 72
        )
        self.assertEqual(med_season["signalId"], "cap-2026-flu-zh-1")
        self.assertEqual(med_season["note"], "flu season")
        # No signal for Surgery B — signalId is None.
        surg_season = next(
            d for d in drivers
            if d["wardId"] == "Surgery B" and d["factor"] == "seasonality" and d["horizonH"] == 72
        )
        self.assertIsNone(surg_season["signalId"])


if __name__ == "__main__":
    unittest.main()
