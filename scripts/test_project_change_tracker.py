"""Tests for scripts/project_change_tracker.py."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "project_change_tracker", ROOT / "scripts/project_change_tracker.py"
)
tracker = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(tracker)


class ProjectChangeTrackerTests(unittest.TestCase):
    def test_normalize_windows_path(self):
        self.assertEqual(tracker.normalize(r"cards\example.html"), "cards/example.html")

    def test_management_paths_are_not_site_changes(self):
        self.assertTrue(tracker.is_management_path("docs/project-management/project-dashboard.md"))
        self.assertFalse(tracker.is_site_path("docs/project-management/project-dashboard.md"))

    def test_site_paths_cover_pages_assets_and_generators(self):
        for path in ["index.html", "cards/example.html", "img/example.webp", "css/site.css", "build.py"]:
            with self.subTest(path=path):
                self.assertTrue(tracker.is_site_path(path))

    def test_outputs_and_research_docs_are_not_site_changes(self):
        self.assertFalse(tracker.is_site_path("output/preview/index.html"))
        self.assertFalse(tracker.is_site_path("docs/research.html"))
        self.assertFalse(tracker.is_site_path("data/untracked-research.json", tracked=False))

    def test_classification_can_return_multiple_areas(self):
        areas = tracker.classify_areas({"manifest.json", "index.html", "sw.js"})
        self.assertIn("外觀與品牌", areas)
        self.assertIn("入口與導覽", areas)
        self.assertIn("PWA／快取", areas)

    def test_new_series_derives_series_and_pages(self):
        before = {}
        after = {"demo": {"steps": ["img/demo_1.webp", "img/demo_2.webp"]}}
        series, pages = tracker.changed_series_and_pages(before, after)
        self.assertEqual(series, {"demo"})
        self.assertEqual(pages, {"demo_1", "demo_2"})

    def test_content_change_derives_page(self):
        old = [{"image": "img/demo.webp", "summary": "old"}]
        new = [{"image": "img/demo.webp", "summary": "new"}]
        _, pages = tracker.changed_series_and_pages({}, {}, old, new)
        self.assertEqual(pages, {"demo"})

    def test_page_filter_is_exact(self):
        changes = [
            {"page_ids": ["a"], "series_ids": ["s"], "request_ids": ["CR-1"]},
            {"page_ids": ["ab"], "series_ids": ["s2"], "request_ids": ["CR-2"]},
        ]
        self.assertEqual(tracker.filter_changes(changes, "a", None, None), [changes[0]])

    def test_live_history_report_has_stable_shape(self):
        report = tracker.build_report(
            ROOT, f"{tracker.TRACKING_START}..HEAD", False, None, None, None
        )
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["head"], tracker.git(ROOT, "rev-parse", "HEAD").strip())
        self.assertIn("history_changes", report["summary"])
        self.assertIsInstance(report["changes"], list)
        self.assertFalse(report["problems"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
