from pyspark.sql import Row

from _lib import transforms


def test_gold_demand_encounter_from_silver_episode(spark):
    silver = spark.createDataFrame([
        Row(
            episode_id="EP-00000001",
            patient_id="pseudo-a1b2c3d4e5f60718",
            admit_ts="2026-06-14T08:00:00Z",
            discharge_ts="2026-06-14T18:00:00Z",
            ward="INT-A",
        )
    ])
    gold = transforms.silver_episode_to_gold_demand_encounter(silver, provenance_source="kis-mirror")
    row = gold.first()
    assert row["episode_id"] == "EP-00000001"
    assert row["provenance_source"] == "kis-mirror"
    assert row["purpose_tags"] == ["capacity-planning"]
    assert row["residency"] == "CH"


def test_gold_rejects_silver_without_residency_tag(spark):
    silver = spark.createDataFrame([
        Row(
            episode_id="EP-00000001",
            patient_id="pseudo-a1b2c3d4e5f60718",
            admit_ts="2026-06-14T08:00:00Z",
            discharge_ts="2026-06-14T18:00:00Z",
            ward="INT-A",
        )
    ])
    gold = transforms.silver_episode_to_gold_demand_encounter(silver, provenance_source="kis-mirror")
    assert gold.filter(gold.residency.isNull()).count() == 0
