import json
import unittest
from pathlib import Path

from connectors.successfactors import SuccessFactorsConnector
from connectors.lms import LmsConnector
from connectors.skills_manager import SkillsManagerConnector
from connectors.work_id import WorkIdConnector

FIX = Path(__file__).resolve().parent / "fixtures"

CASES = [
    (SuccessFactorsConnector(), "successfactors.json", "successfactors"),
    (LmsConnector(), "lms.json", "lms"),
    (SkillsManagerConnector(), "skills_manager.json", "skills_manager"),
    (WorkIdConnector(), "work_id.json", "work_id"),
]


def _load(name: str) -> dict:
    return json.loads((FIX / name).read_text(encoding="utf-8"))


class TestConnectors(unittest.TestCase):
    def test_each_connector_emits_simulated_badge(self):
        for conn, fixture, system in CASES:
            recs = conn.parse(_load(fixture))
            self.assertTrue(recs, f"{system} produced no records")
            for r in recs:
                self.assertEqual(r["externalSystem"], system)
                self.assertEqual(r["sourceMode"], "simulated")
                self.assertIn(r["selfOrConfirmed"], ("self", "employer_confirmed"))
                self.assertIn(r["trustTier"], ("A", "B", "C"))
                self.assertEqual(len(r["provenance"]["rawHash"]), 64)

    def test_hris_and_lms_are_employer_confirmed(self):
        for conn, fixture, _ in CASES[:2]:
            for r in conn.parse(_load(fixture)):
                self.assertEqual(r["selfOrConfirmed"], "employer_confirmed")

    def test_skills_manager_mode_c_is_self_declared(self):
        recs = SkillsManagerConnector().parse(_load("skills_manager.json"))
        for r in recs:
            self.assertEqual(r["selfOrConfirmed"], "self")  # mode C = candidate

    def test_skills_manager_mode_a_is_employer_confirmed(self):
        payload = _load("skills_manager.json")
        payload["mode"] = "A"
        recs = SkillsManagerConnector().parse(payload)
        for r in recs:
            self.assertEqual(r["selfOrConfirmed"], "employer_confirmed")

    def test_work_id_gln_and_scope_only_on_consent(self):
        recs = WorkIdConnector().parse(_load("work_id.json"))
        by_id = {r["evidenceId"]: r for r in recs}
        consented = by_id["wid-001"]
        anonymous = by_id["wid-002"]
        self.assertEqual(consented["workerGln"], "7601190000010")
        self.assertEqual(consented["consentScope"], "capacity-planning")
        self.assertIsNone(anonymous["workerGln"])
        self.assertIsNone(anonymous["consentScope"])
        # Work-ID skills are always self-declared (L0) regardless of consent.
        for r in recs:
            self.assertEqual(r["selfOrConfirmed"], "self")


if __name__ == "__main__":
    unittest.main()
