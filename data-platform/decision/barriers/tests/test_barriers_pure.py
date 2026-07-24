"""Unit tests for the deterministic ``derive_barriers`` runtime barrier builder.

Dependency-light: stdlib + unittest only (no PyYAML, no jsonschema, no Fabric).
Candidates are synthetic and carry no PHI (opaque ``candidate_key`` values,
ward IDs from the ontology, no patient names/MRNs).
"""
from __future__ import annotations

import copy
import unittest

from barriers.derive_barriers import DEFAULT_OWNER_MAP, derive_barriers

MEDICINE_A = "hcp:Ward/Medicine A"
MEDICINE_B = "hcp:Ward/Medicine B"
SURGERY_A = "hcp:Ward/Surgery A"


def _candidate(key, barrier_type, ward, aged_h, clears_at, bed_impact=None):
    c = {
        "candidate_key": key,
        "ward": ward,
        "barrier_type": barrier_type,
        "aged_h": aged_h,
        "clears_at": clears_at,
    }
    if bed_impact is not None:
        c["bed_impact"] = bed_impact
    return c


# The design's "8 candidates collapse into 5 barriers" fixture: 8 candidates
# across 5 barrier_types (two of which have 2 members each).
EIGHT_TO_FIVE = [
    _candidate("C1", "pharmacy", MEDICINE_A, 12, "2026-07-24T18:00:00Z"),
    _candidate("C2", "pharmacy", MEDICINE_B, 30, "2026-07-25T06:00:00Z"),
    _candidate("C3", "transport", MEDICINE_A, 8, "2026-07-24T14:00:00Z"),
    _candidate("C4", "transport", SURGERY_A, 20, "2026-07-25T02:00:00Z"),
    _candidate("C5", "social_placement", MEDICINE_A, 48, "2026-07-26T00:00:00Z"),
    _candidate("C6", "imaging", MEDICINE_B, 4, "2026-07-24T10:00:00Z"),
    _candidate("C7", "consult", SURGERY_A, 6, "2026-07-24T12:00:00Z"),
    _candidate("C8", "consult", SURGERY_A, 10, "2026-07-24T20:00:00Z"),
]


class TestCollapse(unittest.TestCase):
    def test_eight_candidates_collapse_into_five_barriers(self):
        result = derive_barriers(EIGHT_TO_FIVE)
        self.assertEqual(len(result), 5)
        by_type = {b["barrier_type"]: b for b in result}
        self.assertEqual(
            set(by_type.keys()),
            {"pharmacy", "transport", "social_placement", "imaging", "consult"},
        )
        self.assertEqual(by_type["pharmacy"]["candidate_count"], 2)
        self.assertEqual(by_type["transport"]["candidate_count"], 2)
        self.assertEqual(by_type["social_placement"]["candidate_count"], 1)
        self.assertEqual(by_type["imaging"]["candidate_count"], 1)
        self.assertEqual(by_type["consult"]["candidate_count"], 2)

    def test_three_barrier_types_collapse_with_summed_bed_impact(self):
        candidates = [
            _candidate("A1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z", bed_impact=1),
            _candidate("A2", "pharmacy", MEDICINE_A, 9, "2026-07-24T14:00:00Z", bed_impact=2),
            _candidate("A3", "pharmacy", MEDICINE_B, 2, "2026-07-24T08:00:00Z", bed_impact=1),
            _candidate("B1", "transport", MEDICINE_A, 6, "2026-07-24T11:00:00Z", bed_impact=1),
            _candidate("B2", "transport", SURGERY_A, 15, "2026-07-25T00:00:00Z", bed_impact=3),
            _candidate("C1", "imaging", MEDICINE_B, 3, "2026-07-24T09:00:00Z", bed_impact=1),
            _candidate("C2", "imaging", MEDICINE_B, 7, "2026-07-24T13:00:00Z", bed_impact=1),
            _candidate("C3", "imaging", SURGERY_A, 1, "2026-07-24T07:00:00Z", bed_impact=1),
        ]
        result = derive_barriers(candidates)
        self.assertEqual(len(result), 3)
        by_type = {b["barrier_type"]: b for b in result}
        self.assertEqual(by_type["pharmacy"]["candidate_count"], 3)
        self.assertEqual(by_type["pharmacy"]["bed_impact"], 4)
        self.assertEqual(by_type["transport"]["candidate_count"], 2)
        self.assertEqual(by_type["transport"]["bed_impact"], 4)
        self.assertEqual(by_type["imaging"]["candidate_count"], 3)
        self.assertEqual(by_type["imaging"]["bed_impact"], 3)


class TestAggregation(unittest.TestCase):
    def test_aged_h_is_max_and_clears_at_is_latest(self):
        candidates = [
            _candidate("A1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z"),
            _candidate("A2", "pharmacy", MEDICINE_B, 40, "2026-07-25T05:00:00Z"),
            _candidate("A3", "pharmacy", MEDICINE_A, 12, "2026-07-24T23:00:00Z"),
        ]
        result = derive_barriers(candidates)
        self.assertEqual(len(result), 1)
        barrier = result[0]
        self.assertEqual(barrier["aged_h"], 40)
        self.assertEqual(barrier["clears_at"], "2026-07-25T05:00:00Z")

    def test_wards_sorted_unique(self):
        candidates = [
            _candidate("A1", "pharmacy", MEDICINE_B, 5, "2026-07-24T10:00:00Z"),
            _candidate("A2", "pharmacy", MEDICINE_A, 6, "2026-07-24T11:00:00Z"),
            _candidate("A3", "pharmacy", MEDICINE_A, 7, "2026-07-24T12:00:00Z"),
            _candidate("A4", "pharmacy", SURGERY_A, 8, "2026-07-24T13:00:00Z"),
        ]
        result = derive_barriers(candidates)
        self.assertEqual(result[0]["wards"], [MEDICINE_A, MEDICINE_B, SURGERY_A])

    def test_bed_impact_defaults_to_one_when_absent(self):
        candidates = [
            _candidate("A1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z"),
            _candidate("A2", "pharmacy", MEDICINE_B, 6, "2026-07-24T11:00:00Z"),
        ]
        result = derive_barriers(candidates)
        self.assertEqual(result[0]["bed_impact"], 2)


class TestRanking(unittest.TestCase):
    def test_ranked_by_bed_impact_desc_then_aged_h_desc_then_type_asc(self):
        candidates = [
            # transport: bed_impact=5, aged_h=10
            _candidate("T1", "transport", MEDICINE_A, 10, "2026-07-24T10:00:00Z", bed_impact=5),
            # pharmacy: bed_impact=5, aged_h=20 (tie on bed_impact, wins on aged_h)
            _candidate("P1", "pharmacy", MEDICINE_A, 20, "2026-07-24T10:00:00Z", bed_impact=5),
            # imaging: bed_impact=5, aged_h=20 (tie on bed_impact + aged_h, wins on type asc)
            _candidate("I1", "imaging", MEDICINE_A, 20, "2026-07-24T10:00:00Z", bed_impact=5),
            # consult: bed_impact=1, aged_h=99 (lowest bed_impact, ranked last regardless of age)
            _candidate("C1", "consult", MEDICINE_A, 99, "2026-07-24T10:00:00Z", bed_impact=1),
        ]
        result = derive_barriers(candidates)
        self.assertEqual(
            [b["barrier_type"] for b in result],
            ["imaging", "pharmacy", "transport", "consult"],
        )

    def test_determinism(self):
        r1 = derive_barriers(copy.deepcopy(EIGHT_TO_FIVE))
        r2 = derive_barriers(copy.deepcopy(EIGHT_TO_FIVE))
        self.assertEqual(r1, r2)


class TestOwnerRole(unittest.TestCase):
    def test_default_owner_map_assigns_dca_to_known_types(self):
        result = derive_barriers(EIGHT_TO_FIVE)
        for barrier in result:
            self.assertEqual(barrier["owner_role"], DEFAULT_OWNER_MAP.get(barrier["barrier_type"], "dca"))
            self.assertEqual(barrier["owner_role"], "dca")

    def test_unmapped_barrier_type_falls_back_to_dca(self):
        candidates = [
            _candidate("X1", "unknown_barrier_type", MEDICINE_A, 5, "2026-07-24T10:00:00Z"),
        ]
        result = derive_barriers(candidates)
        self.assertEqual(result[0]["owner_role"], "dca")

    def test_custom_owner_map_override_is_honored(self):
        custom_map = {"pharmacy": "bmca", "transport": "dca"}
        candidates = [
            _candidate("P1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z"),
            _candidate("T1", "transport", MEDICINE_A, 5, "2026-07-24T10:00:00Z"),
        ]
        result = derive_barriers(candidates, owner_map=custom_map)
        by_type = {b["barrier_type"]: b for b in result}
        self.assertEqual(by_type["pharmacy"]["owner_role"], "bmca")
        self.assertEqual(by_type["transport"]["owner_role"], "dca")


class TestEdgeCases(unittest.TestCase):
    def test_empty_candidates_returns_empty_list(self):
        self.assertEqual(derive_barriers([]), [])

    def test_missing_barrier_type_raises(self):
        candidates = [
            {
                "candidate_key": "X1",
                "ward": MEDICINE_A,
                "aged_h": 5,
                "clears_at": "2026-07-24T10:00:00Z",
            }
        ]
        with self.assertRaises(ValueError):
            derive_barriers(candidates)

    def test_zero_bed_impact_raises(self):
        candidates = [
            _candidate("X1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z", bed_impact=0)
        ]
        with self.assertRaises(ValueError):
            derive_barriers(candidates)

    def test_negative_bed_impact_raises(self):
        candidates = [
            _candidate("X1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z", bed_impact=-1)
        ]
        with self.assertRaises(ValueError):
            derive_barriers(candidates)

    def test_bool_bed_impact_raises(self):
        candidates = [
            _candidate("X1", "pharmacy", MEDICINE_A, 5, "2026-07-24T10:00:00Z", bed_impact=True)
        ]
        with self.assertRaises(ValueError):
            derive_barriers(candidates)

    def test_input_not_mutated(self):
        candidates = copy.deepcopy(EIGHT_TO_FIVE)
        snapshot = copy.deepcopy(candidates)
        derive_barriers(candidates)
        self.assertEqual(candidates, snapshot)


if __name__ == "__main__":
    unittest.main()
