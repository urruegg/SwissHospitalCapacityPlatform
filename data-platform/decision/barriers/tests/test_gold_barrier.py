"""Unit tests for the DCA barrier Gold-materialization builder.

Sprint 26 WS-B follow-up: ``build_discharge_barriers`` wraps the pure
``derive_barriers`` runtime builder and projects its ranked barriers onto flat
``gold.fact_discharge_barrier`` rows (1:1 with the DC-DISCHARGE-BARRIER-v1
contract). These tests are Spark-free (the Fabric ``run()`` I/O is not
exercised offline) and dependency-light (stdlib + a local draft-07 validator).

No PHI: candidates carry only opaque ``candidate_key`` values and ontology ward
IDs, and the Gold rows they produce carry only aggregate counts + ward IDs.
"""
from __future__ import annotations

import copy
import datetime as dt
import json
import unittest
from pathlib import Path

from barriers.tests._util import validate
from barriers.build_gold_barrier import (
    BARRIER_RUN_ID,
    CONTRACT_BARRIER,
    DEFAULT_CANDIDATES,
    build_discharge_barriers,
    discharge_barrier_envelope,
)

REPO_ROOT = Path(__file__).resolve().parents[4]
SCHEMA_PATH = REPO_ROOT / "data" / "synthetic" / "schema" / "dc-discharge-barrier-v1.schema.json"
PRODUCED_AT = dt.datetime(2026, 7, 24, 8, 0, 0, tzinfo=dt.timezone.utc)

GOLD_ROW_KEYS = {
    "contractId", "barrierId", "hospitalId", "producedAt", "producedBy",
    "barrierType", "ownerRole", "rank", "candidateCount", "bedImpact",
    "agedH", "clearsAt", "wards", "purposeTag", "asOfTimestamp",
}
# Tokens that must never appear as Gold row keys (PHI guard).
_PHI_KEY_TOKENS = ("name", "mrn", "patient", "dob", "birth", "candidate_key", "candidatekey")


def _schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


class TestGoldRowShape(unittest.TestCase):
    def setUp(self):
        self.rows = build_discharge_barriers(DEFAULT_CANDIDATES, PRODUCED_AT)

    def test_default_candidates_collapse_to_five_barriers(self):
        self.assertEqual(len(self.rows), 5)

    def test_every_row_has_exactly_the_contract_keys(self):
        for row in self.rows:
            self.assertEqual(set(row.keys()), GOLD_ROW_KEYS)

    def test_rows_carry_run_metadata_and_contract_id(self):
        for row in self.rows:
            self.assertEqual(row["contractId"], CONTRACT_BARRIER)
            self.assertEqual(row["producedBy"], BARRIER_RUN_ID)
            self.assertEqual(row["producedAt"], "2026-07-24T08:00:00Z")
            self.assertEqual(row["hospitalId"], "H_USZ")

    def test_barrier_id_is_deterministic_slug(self):
        by_type = {r["barrierType"]: r for r in self.rows}
        self.assertEqual(by_type["social_placement"]["barrierId"], "DB-H-USZ-SOCIAL-PLACEMENT-20260724T08")
        self.assertEqual(by_type["pharmacy"]["barrierId"], "DB-H-USZ-PHARMACY-20260724T08")

    def test_owner_role_is_dca_for_all_default_barriers(self):
        for row in self.rows:
            self.assertEqual(row["ownerRole"], "dca")

    def test_wards_are_ontology_ids(self):
        for row in self.rows:
            for ward in row["wards"]:
                self.assertTrue(ward.startswith("hcp:Ward/"), ward)


class TestRanking(unittest.TestCase):
    def test_rank_is_dense_one_based_and_matches_sort_order(self):
        rows = build_discharge_barriers(DEFAULT_CANDIDATES, PRODUCED_AT)
        self.assertEqual([r["rank"] for r in rows], [1, 2, 3, 4, 5])
        # bedImpact is non-increasing along the ranked order.
        impacts = [r["bedImpact"] for r in rows]
        self.assertEqual(impacts, sorted(impacts, reverse=True))


class TestAggregationPreserved(unittest.TestCase):
    def test_bed_impact_and_counts_match_pure_builder(self):
        rows = build_discharge_barriers(DEFAULT_CANDIDATES, PRODUCED_AT)
        by_type = {r["barrierType"]: r for r in rows}
        # pharmacy: C1 (bed_impact default 1) + C2 (1) = count 2, impact 2.
        self.assertEqual(by_type["pharmacy"]["candidateCount"], 2)
        self.assertEqual(by_type["consult"]["candidateCount"], 2)
        # agedH is the worst-aged member; clearsAt the latest.
        self.assertEqual(by_type["social_placement"]["agedH"], 48)
        self.assertEqual(by_type["social_placement"]["clearsAt"], "2026-07-26T00:00:00Z")


class TestNullable(unittest.TestCase):
    def test_missing_age_and_clears_at_serialise_as_null(self):
        candidates = [
            {"candidate_key": "K1", "ward": "hcp:Ward/Medicine A", "barrier_type": "pharmacy"},
        ]
        rows = build_discharge_barriers(candidates, PRODUCED_AT)
        self.assertEqual(len(rows), 1)
        self.assertIsNone(rows[0]["agedH"])
        self.assertIsNone(rows[0]["clearsAt"])
        self.assertEqual(rows[0]["wards"], ["hcp:Ward/Medicine A"])


class TestNoPhi(unittest.TestCase):
    def test_no_phi_like_keys_in_gold_rows(self):
        rows = build_discharge_barriers(DEFAULT_CANDIDATES, PRODUCED_AT)
        for row in rows:
            for key in row:
                lowered = key.lower()
                for token in _PHI_KEY_TOKENS:
                    self.assertNotIn(token, lowered, f"PHI-like key {key!r}")

    def test_input_candidates_not_mutated(self):
        candidates = copy.deepcopy(DEFAULT_CANDIDATES)
        snapshot = copy.deepcopy(candidates)
        build_discharge_barriers(candidates, PRODUCED_AT)
        self.assertEqual(candidates, snapshot)


class TestDeterminism(unittest.TestCase):
    def test_repeated_builds_are_identical(self):
        r1 = build_discharge_barriers(copy.deepcopy(DEFAULT_CANDIDATES), PRODUCED_AT)
        r2 = build_discharge_barriers(copy.deepcopy(DEFAULT_CANDIDATES), PRODUCED_AT)
        self.assertEqual(r1, r2)


class TestSchemaConformance(unittest.TestCase):
    def test_default_envelope_validates(self):
        records = build_discharge_barriers(DEFAULT_CANDIDATES, PRODUCED_AT)
        envelope = discharge_barrier_envelope(records, "slice1")
        errors = validate(envelope, _schema())
        self.assertEqual(errors, [], "\n".join(errors))

    def test_nullable_envelope_validates(self):
        candidates = [
            {"candidate_key": "K1", "ward": "hcp:Ward/Medicine A", "barrier_type": "pharmacy"},
        ]
        records = build_discharge_barriers(candidates, PRODUCED_AT)
        envelope = discharge_barrier_envelope(records, "nullable")
        errors = validate(envelope, _schema())
        self.assertEqual(errors, [], "\n".join(errors))


if __name__ == "__main__":
    unittest.main()
