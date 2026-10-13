"""In-memory negative tests for the read-only management validator.

No website or management fixture is written. Tests deliberately corrupt copies
to verify that an apparently successful inventory cannot hide broken evidence.
"""
import copy
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import check_project_management as pm


class ManagementValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.model = pm.load_model(cls.root)
        cls.live, cls.source_errors = pm.machine_snapshot(cls.root, "2026-10-13")

    def corrupt(self, mutate, expected):
        model = copy.deepcopy(self.model)
        mutate(model)
        errors, _ = pm.validate(self.root, model, self.live)
        self.assertTrue(any(expected in e for e in errors), errors)

    def test_current_snapshot(self):
        errors, _ = pm.validate(self.root, self.model, self.live)
        self.assertEqual(self.source_errors + errors, [])

    def test_duplicate_page(self):
        self.corrupt(lambda m: m["inventory"].append(m["inventory"][0].copy()), "inventory: duplicate")

    def test_missing_relation_target(self):
        self.corrupt(lambda m: m["relations"][0].update(target_id="page:no-such-page"), "invalid relation endpoints")

    def test_missing_membership(self):
        self.corrupt(lambda m: m["relations"].pop(0), "series/card relations differ")

    def test_missing_inventory_page(self):
        self.corrupt(lambda m: m["inventory"].pop(0), "inventory IDs differ")

    def test_retired_mislabeled_as_current(self):
        def change(m):
            next(r for r in m["inventory"] if r["visibility"] == "retired")["visibility"] = "current"
        self.corrupt(change, "machine field drift: visibility")

    def test_invalid_status(self):
        self.corrupt(lambda m: m["inventory"][0].update(medical_review_status="AI_approved"), "invalid medical_review_status")

    def test_duplicate_request(self):
        self.corrupt(lambda m: m["requests"].append(m["requests"][0].copy()), "requests: duplicate")

    def test_empty_evidence(self):
        self.corrupt(lambda m: m["requests"][0].update(evidence=""), "missing evidence")

    def test_missing_evidence_file(self):
        self.corrupt(lambda m: m["requests"][0].update(evidence="docs/not-here.md"), "evidence path missing")

    def test_unsigned_pharmacist_claim(self):
        self.corrupt(lambda m: m["inventory"][0].update(medical_review_status="pharmacist_reviewed"), "signed review missing")

    def test_stale_signed_content(self):
        def change(m):
            m["inventory"][0].update(medical_review_status="pharmacist_reviewed", reviewer="TEST-ONLY",
                review_date="2026-10-13", medical_review_evidence="docs/project-management/README.md",
                reviewed_content_sha256="old-content")
        self.corrupt(change, "pharmacist review is stale")

    def test_pilot_extra_edge(self):
        def change(m):
            m["relations"].append(dict(relation_id="TEST-ONLY", source_id="page:acne_stage",
                relation_type="further_reading", target_id="page:scar_remove", status="source_observed",
                origin="pilot_navigation", evidence="data/acne_navigation.json", note=""))
        self.corrupt(change, "Pilot relation set differs")

    def test_changed_report(self):
        self.corrupt(lambda m: m["audits"]["reports"][0].update(sha256="outdated"), "report changed")

    def test_bad_calendar_date(self):
        self.corrupt(lambda m: m["requests"][0].update(proposed_at="2026-99-99"), "invalid proposed_at")

    def test_unapproved_completion(self):
        self.corrupt(lambda m: m["requests"][0].update(status="completed", completed_at="2026-10-13",
            validation_result="test-only"), "completed without approval")

    def test_machine_field_drift(self):
        self.corrupt(lambda m: m["inventory"][0].update(favorite_keys='{"wrong":"key"}'), "machine field drift: favorite_keys")

    def test_read_only_and_preserves_manual_data(self):
        before = copy.deepcopy(self.model)
        original_open = Path.open

        def read_only_open(path, mode="r", *args, **kwargs):
            if any(c in mode for c in "wax+"):
                raise AssertionError("Attempted write: " + str(path))
            return original_open(path, mode, *args, **kwargs)

        with patch.object(Path, "open", read_only_open):
            live, errors = pm.machine_snapshot(self.root, "2026-10-13")
            self.assertFalse(errors)
            self.assertFalse(pm.validate(self.root, self.model, live)[0])
        self.assertEqual(self.model, before)
        self.assertTrue(all(set(r) == set(pm.MACHINE_FIELDS) for r in live))
        self.assertTrue(set(pm.MACHINE_FIELDS).isdisjoint(pm.MANUAL_FIELDS))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
