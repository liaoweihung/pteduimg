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
        self.assertTrue(any(expected in e for e in errors),
                        f"Expected {expected!r}; {len(errors)} errors; first five: {errors[:5]}")

    def test_current_snapshot(self):
        errors, _ = pm.validate(self.root, self.model, self.live)
        found = self.source_errors + errors
        if found:
            self.fail(f"{len(found)} snapshot errors; first five: {found[:5]}")

    def test_duplicate_page(self):
        self.corrupt(lambda m: m["inventory"].append(m["inventory"][0].copy()), "inventory: duplicate")

    def test_missing_relation_target(self):
        self.corrupt(lambda m: m["relations"][0].update(target_id="page:no-such-page"), "invalid relation endpoints")

    def _with_removed_series(self, model, series_id="retired_trial_series"):
        model["removed_series"] = {"schema_version": 1, "series": [{
            "id": series_id, "title": "試做系列", "removed_at": "2026-11-14",
            "reason": "測試", "request_id": model["requests"][0]["request_id"]}]}
        return series_id

    def test_removed_series_is_valid_request_target(self):
        model = copy.deepcopy(self.model)
        sid = self._with_removed_series(model)
        model["requests"][0]["related_ids"] = f"series:{sid}"
        errors, _ = pm.validate(self.root, model, self.live)
        self.assertFalse(any(f"missing related target series:{sid}" in e for e in errors))
        self.assertFalse(any(e.startswith("removed-series") or "removed series" in e for e in errors), errors[:5])

    def test_unknown_removed_series_still_missing(self):
        self.corrupt(lambda m: m["requests"][0].update(related_ids="series:no_such_series"),
                     "missing related target series:no_such_series")

    def test_removed_series_still_in_cards(self):
        active = next(iter(pm.read_json(self.root, "cards.json")))
        self.corrupt(lambda m: self._with_removed_series(m, active), f"removed series still in cards.json: {active}")

    def test_removed_series_needs_known_request(self):
        def mutate(m):
            self._with_removed_series(m)
            m["removed_series"]["series"][0]["request_id"] = "CR-0000-000"
        self.corrupt(mutate, "unknown request CR-0000-000")

    def test_relation_to_removed_series_is_invalid(self):
        def mutate(m):
            sid = self._with_removed_series(m)
            m["relations"][0].update(source_id=f"series:{sid}")
        self.corrupt(mutate, "invalid relation endpoints")

    def _card_request_with_missing_targets(self, model, status):
        row = next(r for r in model["requests"] if r["request_type"] in pm.CARD_REQUEST_TYPES)
        row.update(status=status, related_ids="series:no_such_trial|page:no_such_trial_1")
        if status == "completed":
            row.update(approval="approved", completed_at="2026-11-14", validation_result="test")
        return row["request_id"]

    def test_cancelled_card_request_skips_target_checks(self):
        model = copy.deepcopy(self.model)
        rid = self._card_request_with_missing_targets(model, "cancelled")
        errors, _ = pm.validate(self.root, model, self.live)
        self.assertFalse([e for e in errors if e.startswith(rid + ":") and
                          ("missing related target" in e or "ID in related_ids" in e)], errors[:5])

    def test_completed_card_request_still_needs_targets(self):
        model = copy.deepcopy(self.model)
        rid = self._card_request_with_missing_targets(model, "completed")
        errors, _ = pm.validate(self.root, model, self.live)
        self.assertIn(f"{rid}: missing related target series:no_such_trial", errors)
        self.assertIn(f"{rid}: missing related target page:no_such_trial_1", errors)
        model = copy.deepcopy(self.model)
        rid = self._card_request_with_missing_targets(model, "completed")
        next(r for r in model["requests"] if r["request_id"] == rid)["related_ids"] = ""
        errors, _ = pm.validate(self.root, model, self.live)
        self.assertIn(f"{rid}: missing series ID in related_ids", errors)
        self.assertIn(f"{rid}: missing page ID in related_ids", errors)

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
            if errors:
                self.fail(f"{len(errors)} source errors; first five: {errors[:5]}")
            validation_errors, _ = pm.validate(self.root, self.model, live)
            if validation_errors:
                self.fail(f"{len(validation_errors)} snapshot errors; first five: {validation_errors[:5]}")
        self.assertEqual(self.model, before)
        self.assertTrue(all(set(r) == set(pm.MACHINE_FIELDS) for r in live))
        self.assertTrue(set(pm.MACHINE_FIELDS).isdisjoint(pm.MANUAL_FIELDS))


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
