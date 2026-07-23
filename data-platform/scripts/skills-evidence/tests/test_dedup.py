import unittest

from dedup import collapse
from normalize import build_record

COMMON = dict(
    external_system="successfactors",
    source_mode="simulated",
    external_person_ref="p-1",
    external_skill_code="SK-100",
    external_skill_label="Triage",
    captured_at="2026-07-19",
    connector_version="1.0.0",
    licence="synthetic",
    raw={"x": 1},
)


def _rec(evidence_id, self_or_confirmed, **over):
    return build_record(evidence_id=evidence_id, self_or_confirmed=self_or_confirmed,
                        **{**COMMON, **over})


class TestDedup(unittest.TestCase):
    def test_same_person_skill_system_collapses_to_one(self):
        out = collapse([_rec("e1", "self"), _rec("e2", "self")])
        self.assertEqual(len(out), 1)

    def test_employer_confirmed_beats_self(self):
        out = collapse([_rec("e1", "self"), _rec("e2", "employer_confirmed")])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["selfOrConfirmed"], "employer_confirmed")

    def test_employer_confirmed_wins_regardless_of_order(self):
        out = collapse([_rec("e1", "employer_confirmed"), _rec("e2", "self")])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0]["selfOrConfirmed"], "employer_confirmed")

    def test_different_skill_is_not_collapsed(self):
        out = collapse([_rec("e1", "self"), _rec("e2", "self", external_skill_code="SK-200")])
        self.assertEqual(len(out), 2)

    def test_different_system_is_not_collapsed(self):
        out = collapse([_rec("e1", "self"), _rec("e2", "self", external_system="lms")])
        self.assertEqual(len(out), 2)


if __name__ == "__main__":
    unittest.main()
