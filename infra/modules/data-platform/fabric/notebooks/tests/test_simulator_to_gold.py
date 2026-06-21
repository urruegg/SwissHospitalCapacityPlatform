from pyspark.sql import Row

from _lib import transforms


def test_simulator_record_maps_to_gold_schema_with_simulator_provenance(spark):
    records = spark.createDataFrame([
        Row(
            encounterId="ENC-2026-9001",
            pseudonymId="PID-1234ABCD",
            expectedArrivalTimestamp="2026-06-21T10:00:00Z",
            expectedLOSDays=2,
            requestedSpecialtyServiceId="HCS-ONCOLOGY-0205",
            asOfTimestamp="2026-06-21T09:58:00Z",
        )
    ])

    gold = transforms.simulator_records_to_gold_demand_encounter(records)
    row = gold.first()

    assert row["episode_id"] == "ENC-2026-9001"
    assert row["provenance_source"] == "simulator"
    assert row["purpose_tags"] == ["capacity-planning"]
    assert row["residency"] == "CH"
    assert row["patient_id"].startswith("pseudo-")

