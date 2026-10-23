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
        before_errors, _ = pm.validate(ROOT, model, live)
        changed = copy.deepcopy(model)
        affected = {"smecta_1", "smecta_2", "smecta_3"}
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
