"""Idempotency test for merge_upsert (spec sec.6.3, sec.5.2 W1.3 expectation)."""
import uuid

import pytest

from _lib.io import merge_upsert


@pytest.fixture
def merge_db(spark):
    db = f"test_merge_{uuid.uuid4().hex[:8]}"
    spark.sql(f"CREATE DATABASE IF NOT EXISTS {db}")
    yield db
    spark.sql(f"DROP DATABASE IF EXISTS {db} CASCADE")


def test_merge_upsert_is_idempotent(spark, merge_db):
    source = spark.createDataFrame(
        [("EP-1", "pseudo-aaaaaaaaaaaaaaaa"), ("EP-2", "pseudo-bbbbbbbbbbbbbbbb")],
        ["episode_id", "patient_id"],
    )
    target = f"{merge_db}.silver_episode"

    merge_upsert(spark, source, target, key_cols=["episode_id"])
    first_count = spark.read.table(target).count()

    merge_upsert(spark, source, target, key_cols=["episode_id"])
    second_count = spark.read.table(target).count()

    assert first_count == 2
    assert second_count == 2


def test_merge_upsert_updates_matched_rows(spark, merge_db):
    initial = spark.createDataFrame(
        [("EP-1", "ward-A")], ["episode_id", "ward"]
    )
    updated = spark.createDataFrame(
        [("EP-1", "ward-B")], ["episode_id", "ward"]
    )
    target = f"{merge_db}.silver_episode_update"

    merge_upsert(spark, initial, target, key_cols=["episode_id"])
    merge_upsert(spark, updated, target, key_cols=["episode_id"])

    row = spark.read.table(target).collect()[0]
    assert row["ward"] == "ward-B"
