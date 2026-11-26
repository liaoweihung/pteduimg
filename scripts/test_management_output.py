"""Output-mode tests; no card, inventory, or medical source is modified."""
import copy
import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import check_project_management as pm


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts/check_project_management.py"


class ManagementOutputTests(unittest.TestCase):
    def test_stable_identity_detects_replacement_at_same_total(self):
        baseline = pm.diagnostics_from_errors([
            "old_page: machine field drift: rules_sha256",
            "AUD-002: report changed; append history and reassess affected claims",
        ])
        current = pm.diagnostics_from_errors([
            "new_page: machine field drift: rules_sha256",
            "AUD-002: report changed; append history and reassess affected claims",
        ])
        delta = pm.compare_diagnostics(current, baseline)
        self.assertEqual((len(delta["new"]), len(delta["resolved"]), len(delta["persistent"])), (1, 1, 1))

    def test_worsened_and_unclassified_are_shown(self):
        original = "page_1: evidence path missing: docs/missing.md"
        unknown = "new_page: unexpected validator failure"
        old = pm.diagnostics_from_errors([original])
        current = pm.diagnostics_from_errors([original, original, unknown])
        delta = pm.compare_diagnostics(current, old)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            pm.print_summary([original, original, unknown], [], current, delta, None)
        self.assertEqual(len(delta["worsened"]), 1)
        self.assertEqual(len(delta["new"]), 1)
        self.assertIn("WORSENED:", output.getvalue())
        self.assertIn("UNCLASSIFIED:", output.getvalue())
        self.assertIn(unknown, output.getvalue())

        changed_wording = pm.diagnostics_from_errors(
            ["page_1: evidence path missing: docs/missing.md"])
        self.assertEqual(len(pm.compare_diagnostics(changed_wording, [
            {**changed_wording[0], "message": "earlier wording"}])["worsened"]), 1)

    def test_real_full_summary_and_three_card_simulation(self):
        def run(*args):
            return subprocess.run([sys.executable, "-B", str(CHECKER), *args],
                                  cwd=ROOT, capture_output=True, text=True, encoding="utf-8")

        full = run()
        with tempfile.TemporaryDirectory(dir=ROOT / "outputs") as temp:
            self.assertTrue(Path(temp).resolve().is_relative_to((ROOT / "outputs").resolve()))
            path = Path(temp) / "management-report.json"
            summary = run("--summary", "--report-file", str(path))
            report = json.loads(path.read_text(encoding="utf-8"))
            baseline = run("--summary", "--baseline-file", str(path))

        full_errors = [line.removeprefix("ERROR: ") for line in full.stdout.splitlines()
                       if line.startswith("ERROR: ")]
        self.assertEqual(full.returncode, summary.returncode)
        self.assertEqual(len(full_errors), report["error_count"])
        self.assertEqual(full_errors, report["errors"])
        self.assertEqual(sum(item["count"] for item in report["diagnostics"]), report["error_count"])
        self.assertLess(len(summary.stdout), len(full.stdout) // 5)
        self.assertNotIn("ERROR: ", summary.stdout)
        self.assertIn("new and resolved errors cannot be determined", summary.stdout)
        self.assertIn("new=0", baseline.stdout)
        self.assertIn("resolved=0", baseline.stdout)

        # A three-card import can introduce issues while the total stays fixed.
        old = report["errors"]
        self.assertGreaterEqual(len(old), 3)
        added = [f"sim_card_{i}: machine field drift: source_sha256" for i in range(1, 4)]
        simulated = old[3:] + added
        self.assertEqual(len(simulated), len(old))
        delta = pm.compare_diagnostics(pm.diagnostics_from_errors(simulated), report["diagnostics"])
        self.assertEqual(len(delta["new"]), 3)
        self.assertEqual(len(delta["resolved"]), 3)
        self.assertEqual(len(delta["persistent"]), len(report["diagnostics"]) - 3)

        # Exercise the real validator against three in-memory card inventory changes.
        model = pm.load_model(ROOT)
        live, source_errors = pm.machine_snapshot(ROOT, "2026-10-23")
        live_by_id = {row["page_id"]: row for row in live}
        affected = {"smecta_1", "smecta_2", "smecta_3"}
        # Align only the three simulated rows' source_sha256 in memory so historical
        # drift on those rows does not mask the simulated delta.
        synced_before = copy.deepcopy(model)
        for row in synced_before["inventory"]:
            if row["page_id"] in affected:
                row["source_sha256"] = live_by_id[row["page_id"]]["source_sha256"]
        before_errors, _ = pm.validate(ROOT, synced_before, live)
        changed = copy.deepcopy(synced_before)
        for row in changed["inventory"]:
            if row["page_id"] in affected:
                row["source_sha256"] = "simulated_stale_source"
        after_errors, _ = pm.validate(ROOT, changed, live)
        local_delta = pm.compare_diagnostics(
            pm.diagnostics_from_errors(source_errors + after_errors),
            pm.diagnostics_from_errors(source_errors + before_errors))
        self.assertEqual({item["id"] for item in local_delta["new"]},
                         {f"machine_field_drift|{page}|source_sha256" for page in affected})
        self.assertEqual(len(local_delta["resolved"]), 0)

    def test_summary_prioritizes_new_worsened_and_medical_signoff_over_mechanical_drift(self):
        hist_errors = (
            [f"hist_page_{i}: machine field drift: rules_sha256" for i in range(40)]
            + [f"hist_page_{i}: machine field drift: source_sha256" for i in range(10)]
            + ["rules-v2: domain drift: page", "rules-v2: domain drift: footer"]
            + ["AUD-002: evidence path missing: data/old.md"]
        )
        baseline = pm.diagnostics_from_errors(hist_errors)
        current_errors = hist_errors + [
            "AUD-002: evidence path missing: data/old.md",  # worsened count 1 -> 2
            "card_drift: machine field drift: source_sha256",
            "card_ev: evidence path missing: docs/missing_new.md",
            "card_med: pharmacist review is stale; preserve historical signoff and request delta review",
            "card_unk: brand new unexpected failure",
        ]
        current = pm.diagnostics_from_errors(current_errors)
        delta = pm.compare_diagnostics(current, baseline)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pm.print_summary(current_errors, [], current, delta, Path("outputs/fake-report.json"))
        text = buf.getvalue()
        self.assertIn("Baseline difference: new=4, resolved=0, worsened=1, persistent=53", text)
        # Substantive NEW items must appear before mechanical drift NEW items.
        pos_med = text.index("NEW: [medical_signoff]")
        pos_ev = text.index("NEW: [evidence_and_audit]")
        pos_unk = text.index("NEW: [unclassified]")
        pos_drift = text.index("NEW: [machine_field_drift]")
        pos_worsened = text.index("WORSENED: [evidence_and_audit]")
        pos_persistent_drift = text.index("[Persistent mechanical drift: 52]")
        self.assertLess(pos_med, pos_ev)
        self.assertLess(pos_ev, pos_unk)
        self.assertLess(pos_unk, pos_drift)
        self.assertLess(pos_drift, pos_worsened)
        self.assertLess(pos_worsened, pos_persistent_drift)
        # Historical 50 machine_field_drift items are summarized, not listed one by one.
        self.assertIn("machine_field_drift (50): rules_sha256=40, source_sha256=10", text)
        self.assertNotIn("hist_page_15", text)
        # Unfamiliar errors remain explicitly printed as UNCLASSIFIED.
        self.assertIn("UNCLASSIFIED:", text)
        self.assertIn("brand new unexpected failure", text)

    def test_summary_without_baseline_highlights_high_priority_medical_and_rules_tampering(self):
        errs = [
            "card_1: pharmacist review is stale; preserve historical signoff and request delta review",
            "card_2: signed review missing reviewer",
            "rules-v2: historical mapping changed",
            "rules-v2: domain drift: global",
        ] + [f"p_{i}: machine field drift: rules_sha256" for i in range(15)]
        diags = pm.diagnostics_from_errors(errs)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pm.print_summary(errs, [], diags, None, None)
        text = buf.getvalue()
        self.assertIn("HIGH-PRIORITY [medical_signoff]:", text)
        self.assertIn("card_1: pharmacist review is stale", text)
        self.assertIn("card_2: signed review missing reviewer", text)
        # rules-v2 tampering must NOT be lumped into mechanical drift.
        self.assertIn("UNCLASSIFIED:", text)
        self.assertIn("rules-v2: historical mapping changed", text)
        self.assertIn("machine_field_drift (15): rules_sha256=15", text)
        self.assertNotIn("p_10", text)

    def test_summary_compacts_large_resolved_list(self):
        old_errs = [f"p_{i}: machine field drift: rules_sha256" for i in range(25)]
        new_errs = ["card_med: invalid medical_review_status"]
        old = pm.diagnostics_from_errors(old_errs)
        cur = pm.diagnostics_from_errors(new_errs)
        delta = pm.compare_diagnostics(cur, old)
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            pm.print_summary(new_errs, [], cur, delta, Path("outputs/after.json"))
        text = buf.getvalue()
        self.assertIn("NEW: [medical_signoff]", text)
        self.assertIn("RESOLVED SUMMARY (25 items): machine_field_drift=25", text)
        self.assertIn("20 more resolved items", text)

    def test_invalid_baseline_is_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "outputs") as temp:
            self.assertTrue(Path(temp).resolve().is_relative_to((ROOT / "outputs").resolve()))
            path = Path(temp) / "bad.json"
            path.write_text(json.dumps({"validator": "check_project_management", "schema_version": 1,
                                        "error_count": 0, "diagnostics": [
                                            {"id": "fake", "category": "machine_field_drift",
                                             "message": "p: machine field drift: title", "count": 1}]}),
                            encoding="utf-8")
            with self.assertRaises(ValueError):
                pm.load_baseline(path)


if __name__ == "__main__":
    unittest.main(verbosity=2)
