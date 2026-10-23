"""Isolated build regressions; never build in the real working tree.

Run: python -B -m unittest discover -s tests -p test_incremental_build.py
"""
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts import incremental_build as inc

REPO = build.ROOT


class IncrementalTests(unittest.TestCase):
    def setUp(self):
        (REPO / "outputs").mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="pteduimg-test-", dir=REPO / "outputs")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in inc.RULES + ("sw.js", "index.html", "public.html"):
            (self.root / name).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / name, self.root / name)
        self.cards = {"six": {"title": "Test six", "category": "public_education", "topics": ["test"],
                              "steps": [f"img/a{i}.webp" for i in range(6)]},
                      "other": {"title": "Unrelated", "steps": ["img/other.webp"]}}
        self.records = []
        self.put("cards.retired.json", [])
        self.put("seo.json", {})
        self.sources()
        self.addCleanup(patch.stopall)
        patch.object(build, "load_navigation", return_value={}).start()
        self.scope = inc.use_root(build, self.root)
        self.scope.__enter__()
        self.addCleanup(self.scope.__exit__, None, None, None)
        self.run_build()

    def put(self, name, value):
        inc.write_if_changed(self.root / name, json.dumps(value, ensure_ascii=False, indent=2) + "\n")

    def sources(self):
        self.put("cards.json", self.cards)
        self.put("cards.manual.json", self.cards)
        self.put("data/card_content.json", self.records)
        for card in self.cards.values():
            for image in card["steps"]:
                path = self.root / image
                if not path.exists():
                    inc.write_if_changed(path, "test image bytes")

    def run_build(self, *args):
        with contextlib.redirect_stdout(io.StringIO()) as output:
            build.main(list(args))
        return output.getvalue()

    def state(self):
        return {p.relative_to(self.root).as_posix(): (inc.digest(p.read_bytes()), p.stat().st_mtime_ns)
                for p in self.root.rglob("*") if p.is_file() and "outputs" not in p.relative_to(self.root).parts}

    def append(self):
        self.cards["six"]["steps"].append("img/a6.webp")
        self.sources()

    def test_append_updates_seven_pages_complete_indexes_and_favorites(self):
        before = self.state()
        self.append()
        output = self.run_build("--incremental", "a6")
        self.assertIn("7 card pages written", output)
        self.assertEqual(before["cards/other.html"], self.state()["cards/other.html"])
        for i in range(7):
            text = (self.root / f"cards/a{i}.html").read_text(encoding="utf-8")
            self.assertIn(f"{i+1}/7", text)
            self.assertIn(f"../cards/a{(i+1)%7}.html", text)
            self.assertIn(f"../cards/a{(i-1)%7}.html", text)
            self.assertIn(f'"six-{i}"', text)
        for name in ("seo.json", "all-cards.html", "sitemap.xml", "sitemap-main.xml", "sw.js"):
            text = (self.root / name).read_text(encoding="utf-8")
            for page in [f"cards/a{i}.html" for i in range(7)] + ["cards/other.html"]:
                self.assertIn(page, text, name)

    def test_new_series_only_writes_one_page(self):
        before = self.state()
        self.cards["new"] = {"title": "New", "steps": ["img/new.webp"]}
        self.sources()
        self.assertIn("1 card pages written", self.run_build("--incremental", "new"))
        for name, value in before.items():
            if name.startswith("cards/"):
                self.assertEqual(value, self.state()[name])

    def test_noop_preserves_all_bytes_and_mtimes(self):
        before = self.state()
        self.run_build("--incremental", "a0")
        self.assertEqual(before, self.state())
        self.append()
        self.run_build("--incremental", "a6")
        before = self.state()
        self.run_build("--incremental", "a6")
        self.assertEqual(before, self.state())

    def test_text_change_only_writes_target_preserves_dates(self):
        self.records = [{"image": "img/a0.webp", "matchConfidence": "high", "title": "A", "summary": "S",
                         "sections": [{"heading": "H", "text": "Old"}], "updatedAt": "2026-01-02",
                         "sourceCheckedAt": "2026-01-03", "revisionCredit": "Test", "needsMedicalReview": True}]
        self.records[0]["references"] = [{"title": "Test fixture only", "url": "https://example.invalid/test"}]
        self.sources()
        self.run_build()
        before = self.state()
        self.records[0]["sections"][0]["text"] = "New"
        self.sources()
        self.assertIn("1 card pages written", self.run_build("--incremental", "a0"))
        for i in range(1, 6):
            self.assertEqual(before[f"cards/a{i}.html"], self.state()[f"cards/a{i}.html"])
        text = (self.root / "cards/a0.html").read_text(encoding="utf-8")
        self.assertIn("2026-01-02", text)
        self.assertIn("2026-01-03", text)
        self.assertTrue(json.loads((self.root / "data/card_content.json").read_text())[0]["needsMedicalReview"])

    def test_related_series_reverse_dependency(self):
        self.cards["other"]["related_series"] = ["six"]
        self.sources()
        self.run_build()
        self.cards["six"]["title"] = "Changed title"
        self.sources()
        self.run_build("--incremental", "a0")
        self.assertIn("Changed title", (self.root / "cards/other.html").read_text(encoding="utf-8"))

    def test_only_does_not_touch_globals_or_siblings(self):
        self.cards["six"]["title"] = "New title"
        self.sources()
        before = self.state()
        self.run_build("--only", "a0")
        after = self.state()
        for name in inc.GLOBALS + ("cards/a1.html", "cards/other.html"):
            self.assertEqual(before[name], after[name])

    def test_full_repeat_has_identical_content_and_worker(self):
        before = {p: value[0] for p, value in self.state().items()}
        with patch.object(inc, "git", side_effect=FileNotFoundError("git unavailable")):
            self.run_build()
        self.assertEqual(before, {p: value[0] for p, value in self.state().items()})

    def test_git_bootstrap_without_full_rebuild(self):
        saved = {p: (self.root / p).read_bytes() for p in inc.SOURCES + inc.RULES + inc.GLOBALS}
        (self.root / inc.STATE).unlink()
        self.append()
        def fake_git(root, *args):
            if args == ("rev-parse", "HEAD"): return b"fixture-head"
            if args[0] == "show": return saved[args[1].split(":", 1)[1]]
            if args[0] == "diff": return b"cards.json\0cards.manual.json\0"
            return b""
        with patch.object(inc, "git", side_effect=fake_git):
            self.assertIn("7 card pages written", self.run_build("--incremental", "a6"))

    def test_seo_title_updates_sibling_related_links(self):
        seo = json.loads((self.root / "seo.json").read_text(encoding="utf-8"))
        seo["cards/a0.html"]["page_title"] = "Changed SEO heading"
        self.put("seo.json", seo)
        self.run_build("--incremental", "a0")
        self.assertIn("Changed SEO heading", (self.root / "cards/a1.html").read_text(encoding="utf-8"))

    def test_git_bootstrap_detects_worker_only_change(self):
        saved = {p: (self.root / p).read_bytes() for p in inc.SOURCES + inc.RULES + inc.GLOBALS}
        (self.root / inc.STATE).unlink()
        worker = self.root / "sw.js"
        worker.write_bytes(worker.read_bytes() + b"\n// test worker change\n")
        before = worker.read_bytes()
        def fake_git(root, *args):
            if args == ("rev-parse", "HEAD"): return b"fixture-head"
            if args[0] == "show": return saved[args[1].split(":", 1)[1]]
            if args[0] == "diff": return b"sw.js\0"
            return b""
        with patch.object(inc, "git", side_effect=fake_git):
            self.run_build("--incremental", "a0")
        self.assertNotEqual(before, worker.read_bytes())
        self.assertIn(b"// test worker change", worker.read_bytes())

    def test_write_failure_restores_all_public_bytes(self):
        self.append()
        before = {name: value[0] for name, value in self.state().items()}
        write = Path.write_bytes
        failed = False
        def once(path, data):
            nonlocal failed
            if path == self.root / "seo.json" and not failed:
                failed = True
                raise OSError("injected write failure")
            return write(path, data)
        with patch.object(Path, "write_bytes", once), self.assertRaises(SystemExit):
            self.run_build("--incremental", "a6")
        self.assertTrue(failed)
        self.assertEqual(before, {name: value[0] for name, value in self.state().items()})

    def test_index_date_alone_does_not_write(self):
        path = self.root / "all-cards.html"
        original = path.read_text(encoding="utf-8")
        import re
        changed = re.sub(r"(<span>\?{5})\d{4}-\d{2}-\d{2}", r"\g<1>2099-01-01", original)
        before = path.stat().st_mtime_ns
        self.assertFalse(inc.write_if_changed(path, changed, preserve_index_date=True))
        self.assertEqual(before, path.stat().st_mtime_ns)

    def test_non_rendering_metadata_preserves_crlf_pages(self):
        path = self.root / "cards/a0.html"
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
        before = self.state()["cards/a0.html"]
        self.cards["six"]["internal_note"] = "Does not affect HTML"
        self.sources()
        self.run_build("--incremental", "a0")
        self.assertEqual(before, self.state()["cards/a0.html"])

    def test_url_identity_change_rejected_without_outputs(self):
        seo = json.loads((self.root / "seo.json").read_text(encoding="utf-8"))
        seo["cards/a0.html"]["canonical"] = build.abs_url("cards/different.html")
        self.put("seo.json", seo)
        before = self.state()
        with self.assertRaises(SystemExit):
            self.run_build("--incremental", "a0")
        self.assertEqual(before, self.state())

    def test_worker_changes_for_image_bytes_not_clock(self):
        before = (self.root / "sw.js").read_bytes()
        (self.root / "img/a0.webp").write_bytes(b"new image")
        self.run_build("--incremental", "a0")
        after = (self.root / "sw.js").read_bytes()
        self.assertNotEqual(before, after)
        self.run_build("--incremental", "a0")
        self.assertEqual(after, (self.root / "sw.js").read_bytes())
        normalize = lambda b: __import__('re').sub(rb"const CACHE_NAME = '.*?';", b"VERSION", b)
        self.assertEqual(normalize(before), normalize(after))

    def test_manual_edit_preserved_on_affected_page(self):
        page = self.root / "cards/a0.html"
        page.write_text(page.read_text(encoding="utf-8").replace("</body>", "<!-- manual -->\n</body>"), encoding="utf-8")
        self.append()
        self.run_build("--incremental", "a6")
        self.assertIn("<!-- manual -->", page.read_text(encoding="utf-8"))

    def test_manual_conflict_fails_before_any_write(self):
        page = self.root / "cards/a0.html"
        page.write_text(page.read_text(encoding="utf-8").replace("1/6", "manual count"), encoding="utf-8")
        self.append()
        before = self.state()
        with self.assertRaises(SystemExit):
            self.run_build("--incremental", "a6")
        self.assertEqual(before, self.state())

    def test_unsupported_changes_are_atomic(self):
        for kind in ("delete", "reorder", "hidden", "schedule", "template", "retirement", "missing", "unknown", "unselected"):
            with self.subTest(kind=kind):
                originals = {p: p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
                if kind == "template":
                    with (self.root / "templates/site-footer.html").open("a") as f:
                        f.write("changed")
                elif kind == "retirement":
                    self.put("cards.retired.json", [{"invalid": True}])
                elif kind == "missing":
                    (self.root / "cards/a0.html").unlink()
                elif kind not in ("unknown",):
                    cards = json.loads((self.root / "cards.json").read_text())
                    if kind == "delete": cards["six"]["steps"].pop()
                    if kind == "reorder": cards["six"]["steps"].reverse()
                    if kind == "hidden": cards["six"]["hidden"] = True
                    if kind == "schedule": cards["six"]["publish_at"] = "2030-01-01T00:00:00+08:00"
                    if kind == "unselected": cards["other"]["title"] = "Changed"
                    self.put("cards.json", cards)
                before = self.state()
                with self.assertRaises(SystemExit):
                    self.run_build("--incremental", "unknown" if kind == "unknown" else "a0")
                self.assertEqual(before, self.state())
                for p, data in originals.items(): p.write_bytes(data)


if __name__ == "__main__":
    unittest.main()
