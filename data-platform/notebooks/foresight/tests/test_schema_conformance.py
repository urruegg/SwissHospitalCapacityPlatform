"""Sprint 26 WS-A — Foresight generator output conforms to its DC-* contracts.

Validates the occupancy-forecast + forecast-driver envelope builders against
``data/synthetic/schema/dc-occupancy-forecast-v1.schema.json`` and
``dc-forecast-driver-v1.schema.json`` using the dependency-free draft-07 subset
validator in ``_util`` (stdlib only — no jsonschema, so it runs in CI).
"""
import datetime as dt
import json
import unittest
from pathlib import Path

from _util import load_module, validate

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_DIR = REPO_ROOT / "data" / "synthetic" / "schema"
PRODUCED_AT = dt.datetime(2026, 7, 23, 8, 0, 0, tzinfo=dt.timezone.utc)

WARDS = [
    {
        "ward_id": "Medicine A", "hospital_id": "H_USZ", "bed_capacity": 50,
        "baseline_occupied": 51, "admissions_72h": 6, "discharges_72h": 2,
        "transfers_72h": 0, "seasonality_72h": 0, "seasonality_note": "flu season",
        "signal_id": "cap-2026-flu-zh-1",
    },
]


def _schema(name):
    return json.loads((SCHEMA_DIR / name).read_text(encoding="utf-8"))


class TestSchemaConformance(unittest.TestCase):
    def setUp(self):
        self.mod = load_module("build_gold_forecast.py")

    def test_occupancy_forecast_envelope_valid(self):
        records = self.mod.build_occupancy_forecast(WARDS, PRODUCED_AT)
        envelope = self.mod.occupancy_forecast_envelope(records, "slice1")
        errors = validate(envelope, _schema("dc-occupancy-forecast-v1.schema.json"))
        self.assertEqual(errors, [], "\n".join(errors))

    def test_forecast_driver_envelope_valid(self):
        records = self.mod.build_forecast_drivers(WARDS, PRODUCED_AT)
        envelope = self.mod.forecast_driver_envelope(records, "slice1")
        errors = validate(envelope, _schema("dc-forecast-driver-v1.schema.json"))
        self.assertEqual(errors, [], "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
