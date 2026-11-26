"""In-memory negative tests for the read-only management validator.

No website or management fixture is written. Tests deliberately corrupt copies
to verify that an apparently successful inventory cannot hide broken evidence.
"""
import copy
import csv
import io
import json
import subprocess
import sys
import tempfile
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
            pm.validate(self.root, self.model, live)
        self.assertEqual(self.model, before)
        self.assertTrue(all(set(r) == set(pm.MACHINE_FIELDS) for r in live))
        self.assertTrue(set(pm.MACHINE_FIELDS).isdisjoint(pm.MANUAL_FIELDS))


class ScopedSnapshotAndApplyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.checker = cls.root / "scripts/check_project_management.py"
        cls.full_live, cls.full_errors = pm.machine_snapshot(cls.root, "2026-11-26")
        cls.full_by_id = {r["page_id"]: r for r in cls.full_live}

    def _run_cli(self, *args):
        return subprocess.run(
            [sys.executable, "-B", str(self.checker), *args],
            cwd=self.root, capture_output=True, text=True, encoding="utf-8",
        )

    def _build_temp_repo(self, directory: Path):
        (directory / "cards").mkdir(parents=True)
        (directory / "img").mkdir(parents=True)
        (directory / "data").mkdir(parents=True)
        (directory / pm.PM).mkdir(parents=True)
        (directory / "scripts").mkdir(parents=True)
        (directory / "templates").mkdir(parents=True)
        for rel in pm.RULE_FILES:
            p = directory / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(f"# fixture {rel}\n", encoding="utf-8")
        (directory / "data/acne_navigation.json").write_text('{"pages":[]}', encoding="utf-8")
        (directory / "img/page_a.webp").write_bytes(b"IMG-A")
        (directory / "img/page_b.webp").write_bytes(b"IMG-B")
        (directory / "img/page_r.webp").write_bytes(b"IMG-R")
        for pid, title in (("page_a", "頁面A"), ("page_b", "頁面B"), ("page_r", "退役頁")):
            (directory / f"cards/{pid}.html").write_text(
                f"<!doctype html><html><head><title>{title}</title></head><body><h1>{title}</h1></body></html>",
                encoding="utf-8",
            )
        cards = {
            "series_a": {"title": "系列A", "hidden": False, "steps": ["img/page_a.webp", "img/page_b.webp"]},
        }
        (directory / "cards.json").write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
        (directory / "cards.manual.json").write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
        retired = [{"page": "cards/page_r.html", "image": "img/page_r.webp", "title": "退役頁"}]
        (directory / "cards.retired.json").write_text(json.dumps(retired, ensure_ascii=False), encoding="utf-8")
        (directory / "data/card_content.json").write_text("[]", encoding="utf-8")

        live, errs = pm.machine_snapshot(directory, "2026-11-25")
        self.assertEqual(errs, [])
        fieldnames = [f for f in pm.MACHINE_FIELDS if f not in {"rules_version", "rules_v1_sha256"}] + pm.MANUAL_FIELDS + ["rules_version", "rules_v1_sha256"]
        rows = []
        for idx, row in enumerate(live):
            merged = dict(row)
            merged["source_sha256"] = f"stale_source_{idx}"
            merged["title"] = f"舊標題_{idx}"
            merged.update(
                medical_review_status="pharmacist_reviewed" if idx == 0 else "pending_pharmacist",
                medical_review_evidence="docs/project-management/README.md" if idx == 0 else "unknown",
                reviewer="藥師甲" if idx == 0 else "unknown",
                review_date="2026-11-01" if idx == 0 else "unknown",
                reviewed_content_sha256="keep_exact_reviewed_hash" if idx == 0 else "unknown",
                documented_status="documented_complete" if idx == 0 else "unknown",
                audit_ids="AUD-001" if idx == 0 else "",
                history_note="保留歷史註記" if idx == 0 else "",
                seo_aeo_status="unknown",
                known_issue_ids="CR-2026-001",
                review_required="no" if idx == 0 else "yes",
                review_reason="" if idx == 0 else "待複核",
                last_human_confirmed_at="2026-11-01" if idx == 0 else "unknown",
            )
            rows.append(merged)
        buf = io.StringIO(newline="")
        writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)
        (directory / pm.PM / "page-inventory.csv").write_bytes(buf.getvalue().encode("utf-8"))
        return rows, fieldnames

    def test_single_page_snapshot_matches_full_snapshot_on_real_repo(self):
        cards = pm.read_json(self.root, "cards.json")
        retired = pm.read_json(self.root, "cards.retired.json")
        stem_counts = {}
        for card in cards.values():
            for img in card.get("steps", []):
                stem = Path(img).stem
                stem_counts[stem] = stem_counts.get(stem, 0) + 1
        shared_pid = next(stem for stem, count in sorted(stem_counts.items()) if count > 1)
        retired_pid = Path(retired[0]["page"]).stem
        samples = [
            {"09_australia_usa_china"},
            {shared_pid},
            {retired_pid},
            {"09_australia_usa_china", shared_pid, retired_pid},
        ]
        for targets in samples:
            with self.subTest(targets=sorted(targets)):
                rows, errs, all_ids = pm._machine_snapshot(self.root, "2026-11-26", page_ids=targets)
                expected = [self.full_by_id[pid] for pid in sorted(targets)]
                self.assertEqual(rows, expected)
                self.assertEqual(errs, self.full_errors)
                self.assertEqual(all_ids, set(self.full_by_id))
        with self.assertRaisesRegex(ValueError, "Unknown --page IDs"):
            pm._machine_snapshot(self.root, "2026-11-26", page_ids={"no_such_page_id"})

    def test_propose_cli_single_page_matches_full_filtered(self):
        pid = "09_australia_usa_china"
        proc = self._run_cli("--propose", "--page", pid)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        payload = json.loads(proc.stdout)
        previous = {r["page_id"]: r for r in pm.read_csv(self.root, f"{pm.PM}/page-inventory.csv")}
        expected_removed = sorted(set(previous) - set(self.full_by_id))
        self.assertEqual(payload["removed_ids_require_manual_retirement_check"], expected_removed)
        self.assertEqual(payload["source_errors"], self.full_errors)
        if payload["machine_field_proposals"]:
            self.assertEqual(len(payload["machine_field_proposals"]), 1)
            row = payload["machine_field_proposals"][0]
            self.assertEqual(row["page_id"], pid)
            for field in pm.MACHINE_FIELDS:
                if field != "checked_at":
                    self.assertEqual(row[field], self.full_by_id[pid][field])

    def test_apply_machine_updates_only_whitelist_and_preserves_manual_and_non_target_rows(self):
        with tempfile.TemporaryDirectory(dir=self.root / "outputs") as temp:
            tmp_root = Path(temp)
            before_rows, _ = self._build_temp_repo(tmp_root)
            inv_path = tmp_root / pm.PM / "page-inventory.csv"

            # Capture read-only --propose before apply for equivalence check.
            propose_before = self._run_cli("--root", str(tmp_root), "--propose", "--page", "page_a")
            self.assertEqual(propose_before.returncode, 0, propose_before.stderr)
            proposed = json.loads(propose_before.stdout)["machine_field_proposals"]
            self.assertEqual(len(proposed), 1)

            # Apply ONLY page_a via CLI.
            apply_proc = self._run_cli("--root", str(tmp_root), "--apply-machine", "--page", "page_a")
            self.assertEqual(apply_proc.returncode, 0, apply_proc.stderr)
            result = json.loads(apply_proc.stdout)
            self.assertEqual(result["applied_pages"], ["page_a"])
            self.assertEqual(result["unchanged_pages"], [])
            self.assertTrue(result["written"])
            self.assertTrue(result["manual_fields_verified_unchanged"])

            # Verify CRLF & BOM preserved and zero diff on non-target rows & MANUAL_FIELDS.
            raw_after = inv_path.read_bytes()
            self.assertFalse(raw_after.startswith(b"\xef\xbb\xbf"))
            self.assertEqual(raw_after.count(b"\n") - raw_after.count(b"\r\n"), 0)
            after_rows = pm.read_csv(tmp_root, f"{pm.PM}/page-inventory.csv")
            before_by_id = {r["page_id"]: r for r in before_rows}
            after_by_id = {r["page_id"]: r for r in after_rows}
            for field in pm.MACHINE_FIELDS:
                if field != "checked_at":
                    self.assertEqual(after_by_id["page_a"][field], proposed[0][field])
            for field in pm.MANUAL_FIELDS:
                self.assertEqual(after_by_id["page_a"][field], before_by_id["page_a"][field])
            self.assertEqual(after_by_id["page_b"], before_by_id["page_b"])
            self.assertEqual(after_by_id["page_r"], before_by_id["page_r"])

            # Re-running --propose --page page_a must now report zero proposals.
            propose_after = self._run_cli("--root", str(tmp_root), "--propose", "--page", "page_a")
            self.assertEqual(propose_after.returncode, 0, propose_after.stderr)
            self.assertEqual(json.loads(propose_after.stdout)["machine_field_proposals"], [])

            # Re-running --apply-machine on already-synced page_a is a no-op.
            apply_again = self._run_cli("--root", str(tmp_root), "--apply-machine", "--page", "page_a")
            self.assertEqual(apply_again.returncode, 0, apply_again.stderr)
            again = json.loads(apply_again.stdout)
            self.assertFalse(again["written"])
            self.assertEqual(again["unchanged_pages"], ["page_a"])
            self.assertEqual(inv_path.read_bytes(), raw_after)

    def test_apply_machine_guardrails_fail_closed(self):
        # Missing --page must be rejected by CLI parser (never full-table write).
        no_page = self._run_cli("--apply-machine")
        self.assertNotEqual(no_page.returncode, 0)
        self.assertIn("--page", no_page.stderr)
        # Mutual exclusion with --propose / --summary.
        combo = self._run_cli("--apply-machine", "--propose", "--page", "09_australia_usa_china")
        self.assertNotEqual(combo.returncode, 0)

        with tempfile.TemporaryDirectory(dir=self.root / "outputs") as temp:
            tmp_root = Path(temp)
            before_rows, fieldnames = self._build_temp_repo(tmp_root)
            inv_path = tmp_root / pm.PM / "page-inventory.csv"
            original_bytes = inv_path.read_bytes()

            # Unknown page ID -> rejected without touching file.
            with self.assertRaisesRegex(ValueError, "Unknown --page IDs"):
                pm.apply_machine_fields(tmp_root, ["no_such_page"], "2026-11-26")
            self.assertEqual(inv_path.read_bytes(), original_bytes)

            # Live page missing from page-inventory.csv -> rejected (never fabricates MANUAL_FIELDS).
            cards = pm.read_json(tmp_root, "cards.json")
            cards["series_a"]["steps"].append("img/page_new.webp")
            (tmp_root / "cards.json").write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
            (tmp_root / "img/page_new.webp").write_bytes(b"IMG-NEW")
            (tmp_root / "cards/page_new.html").write_text("<html><body><h1>New</h1></body></html>", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing from page-inventory.csv"):
                pm.apply_machine_fields(tmp_root, ["page_new"], "2026-11-26")
            self.assertEqual(inv_path.read_bytes(), original_bytes)

            # Source error on target page (missing HTML) -> rejected without touching file.
            (tmp_root / "cards/page_a.html").unlink()
            with self.assertRaisesRegex(ValueError, "source errors"):
                pm.apply_machine_fields(tmp_root, ["page_a"], "2026-11-26")
            self.assertEqual(inv_path.read_bytes(), original_bytes)

            # Programmatic invariant check catches any MANUAL_FIELDS tampering.
            tampered = copy.deepcopy(before_rows)
            tampered[0]["reviewer"] = "AI_TAMPERED"
            with self.assertRaisesRegex(RuntimeError, "MANUAL_FIELDS violation"):
                pm._verify_machine_apply_invariants(before_rows, tampered, fieldnames, {"page_a"})

            tampered_other = copy.deepcopy(before_rows)
            tampered_other[1]["title"] = "CHANGED_NON_TARGET"
            with self.assertRaisesRegex(RuntimeError, "Non-target page modified"):
                pm._verify_machine_apply_invariants(before_rows, tampered_other, fieldnames, {"page_a"})


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    unittest.main(verbosity=2)
