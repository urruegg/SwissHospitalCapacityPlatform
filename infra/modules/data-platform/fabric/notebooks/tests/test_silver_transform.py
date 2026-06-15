from pyspark.sql import Row

from _lib import transforms


def test_silver_episode_drops_non_allowlisted_columns(spark):
    bronze = spark.createDataFrame([
        Row(
            episode_id="EP-00000001",
            patient_id="pseudo-a1b2c3d4e5f60718",
            admit_ts="2026-06-14T08:00:00Z",
            discharge_ts="2026-06-14T18:00:00Z",
            ward="INT-A",
            source="walking-skeleton",
            leaked_column="should-not-survive",
        )
    ])
    silver = transforms.bronze_to_silver_episode(bronze)
    assert "leaked_column" not in silver.columns
    assert set(silver.columns) == {
        "episode_id", "patient_id", "admit_ts", "discharge_ts", "ward",
    }
    assert silver.count() == 1


def test_silver_quarantines_bad_pseudonym(spark):
    bronze = spark.createDataFrame([
        Row(
            episode_id="EP-00000002",
            patient_id="John Doe",  # not a valid pseudonym
            admit_ts="2026-06-14T09:00:00Z",
            discharge_ts="2026-06-14T19:00:00Z",
            ward="INT-A",
            source="walking-skeleton",
        )
    ])
    silver, quarantine = transforms.bronze_to_silver_episode_with_quarantine(bronze)
    assert silver.count() == 0
    assert quarantine.count() == 1
    assert quarantine.first()["quarantine_reason"] == "pii-shape-mismatch"
