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

    def assert_matches_full_build(self):
        inc_hashes = {p: value[0] for p, value in self.state().items()}
        self.run_build()
        full_hashes = {p: value[0] for p, value in self.state().items()}
        self.assertEqual(inc_hashes, full_hashes)

    def test_next_reads_cross_series_title_updates_last_step_and_matches_full_build(self):
        self.cards["compression"] = {
            "title": "Compression Old",
            "category": "public_education",
            "topics": ["chronic_conditions"],
            "steps": ["img/c0.webp", "img/c1.webp"],
        }
        self.cards["knee"] = {
            "title": "Knee Brace",
            "category": "public_education",
            "topics": ["chronic_conditions"],
            "steps": ["img/k0.webp", "img/k1.webp"],
        }
        self.sources()
        self.run_build()
        before = self.state()
        self.cards["compression"]["title"] = "Compression Updated"
        self.sources()
        self.run_build("--incremental", "c0")
        after = self.state()
        self.assertIn("Compression Updated", (self.root / "cards/k1.html").read_text(encoding="utf-8"))
        self.assertEqual(before["cards/k0.html"], after["cards/k0.html"])
        self.assertEqual(before["cards/other.html"], after["cards/other.html"])
        self.assert_matches_full_build()

    def test_next_reads_new_public_series_updates_existing_last_step_and_matches_full_build(self):
        before = self.state()
        self.cards["new_pub"] = {
            "title": "New Public Series",
            "category": "public_education",
            "topics": ["test"],
            "steps": ["img/new_pub0.webp"],
        }
        self.sources()
        self.run_build("--incremental", "new_pub0")
        after = self.state()
        self.assertIn("New Public Series", (self.root / "cards/a5.html").read_text(encoding="utf-8"))
        for i in range(5):
            self.assertEqual(before[f"cards/a{i}.html"], after[f"cards/a{i}.html"])
        self.assertEqual(before["cards/other.html"], after["cards/other.html"])
        self.assert_matches_full_build()

    def test_next_reads_conflict_on_cross_series_last_page_is_atomic(self):
        self.cards["compression"] = {
            "title": "Compression Old",
            "category": "public_education",
            "topics": ["chronic_conditions"],
            "steps": ["img/c0.webp", "img/c1.webp"],
        }
        self.cards["knee"] = {
            "title": "Knee Brace",
            "category": "public_education",
            "topics": ["chronic_conditions"],
            "steps": ["img/k0.webp", "img/k1.webp"],
        }
        self.sources()
        self.run_build()
        knee_last = self.root / "cards/k1.html"
        knee_last.write_text(
            knee_last.read_text(encoding="utf-8").replace("Compression Old", "Manual Custom Title"),
            encoding="utf-8",
        )
        self.cards["compression"]["title"] = "Compression Updated"
        self.sources()
        before = self.state()
        with self.assertRaises(SystemExit):
            self.run_build("--incremental", "c0")
        self.assertEqual(before, self.state())

    def test_manual_cards_only_rendering_and_non_rendering_boundaries(self):
        self.cards["peer"] = {
            "title": "Peer Public",
            "category": "public_education",
            "topics": ["chronic_conditions"],
            "steps": ["img/p0.webp", "img/p1.webp"],
        }
        self.sources()
        self.run_build()
        before = self.state()
        manual = json.loads((self.root / "cards.manual.json").read_text(encoding="utf-8"))
        manual["six"]["topics"] = ["chronic_conditions"]
        manual["six"]["tool_link"] = {"title": "Manual Tool", "url": "../calc.html"}
        self.put("cards.manual.json", manual)
        self.run_build("--incremental", "a0")
        after = self.state()
        self.assertIn("Manual Tool", (self.root / "cards/a0.html").read_text(encoding="utf-8"))
        self.assertIn("Test six", (self.root / "cards/p1.html").read_text(encoding="utf-8"))
        self.assertEqual(before["cards/p0.html"], after["cards/p0.html"])
        self.assertEqual(before["cards/other.html"], after["cards/other.html"])
        self.assert_matches_full_build()

        # Non-rendering manual-only field change writes 0 public outputs and advances baseline.
        manual["six"]["tags"] = ["manual_only_non_rendering_tag"]
        self.put("cards.manual.json", manual)
        before_non_render = self.state()
        out = self.run_build("--incremental", "a0")
        self.assertIn("0 card pages written", out)
        self.assertEqual(before_non_render, self.state())
        self.assertIn("0 affected pages; no public outputs changed.", self.run_build("--incremental", "a0"))

    def test_manual_cards_invalid_edits_are_rejected_atomically(self):
        for kind in ("unselected", "orphan", "hidden"):
            with self.subTest(kind=kind):
                orig_manual = (self.root / "cards.manual.json").read_bytes()
                manual = json.loads(orig_manual.decode("utf-8"))
                if kind == "unselected":
                    manual["other"]["tool_link"] = {"title": "Unselected", "url": "../calc.html"}
                elif kind == "orphan":
                    manual["ghost_series"] = {"title": "Ghost"}
                elif kind == "hidden":
                    manual["six"]["hidden"] = True
                self.put("cards.manual.json", manual)
                before = self.state()
                with self.assertRaises(SystemExit):
                    self.run_build("--incremental", "a0")
                self.assertEqual(before, self.state())
                (self.root / "cards.manual.json").write_bytes(orig_manual)

    def test_cr_only_change_updates_recent_changes_and_sw_without_touching_cards(self):
        cr_path = self.root / inc.CHANGE_REQUESTS
        header = (
            "request_id,proposed_at,name,description,request_type,scope,related_ids,"
            "priority,status,approval,needs_pharmacist,author_permission,commercial_disclosure,"
            "completed_at,git_commit,validation_result,evidence\n"
        )
        row_in_progress = (
            "CR-2026-999,2026-11-26,測試新增系列,說明,新增系列,series:six,series:six|page:a0,"
            "P1,in_progress,approved,no,unknown,unknown,unknown,same_commit,unknown,evidence.md\n"
        )
        inc.write_if_changed(cr_path, header + row_in_progress)
        self.run_build()
        self.assertEqual(json.loads((self.root / "data/recent-changes.json").read_text(encoding="utf-8")), [])

        before = self.state()
        row_completed = row_in_progress.replace(",in_progress,", ",completed,").replace(",unknown,same_commit,", ",2026-11-26,same_commit,")
        inc.write_if_changed(cr_path, header + row_completed)
        out = self.run_build("--incremental", "a0")
        after = self.state()
        self.assertIn("0 card pages written", out)
        for name, value in before.items():
            if name.startswith("cards/"):
                self.assertEqual(value, after[name])
        recent = json.loads((self.root / "data/recent-changes.json").read_text(encoding="utf-8"))
        self.assertEqual(len(recent), 1)
        self.assertEqual(recent[0]["request_id"], "CR-2026-999")
        self.assertNotEqual(before["sw.js"][0], after["sw.js"][0])
        self.assert_matches_full_build()

        # CR edit that does not change recent-changes.json writes 0 public outputs and advances baseline.
        before_noop = self.state()
        inc.write_if_changed(cr_path, header + row_completed.replace(",unknown,evidence.md", ",checked,evidence.md"))
        self.run_build("--incremental", "a0")
        after_noop = self.state()
        for name in list(inc.GLOBALS) + [p for p in before_noop if p.startswith("cards/")]:
            self.assertEqual(before_noop[name], after_noop[name], name)
        self.assertIn("0 affected pages; no public outputs changed.", self.run_build("--incremental", "a0"))

    def test_incremental_reuses_runtime_hashes_without_copytree_and_detects_invalidation(self):
        self.records = [{
            "image": "img/a0.webp", "matchConfidence": "high", "title": "A", "summary": "S",
            "sections": [{"heading": "H", "text": "Old"}], "updatedAt": "2026-01-02",
            "sourceCheckedAt": "2026-01-03", "revisionCredit": "Test", "needsMedicalReview": True,
            "references": [{"title": "Test fixture only", "url": "https://example.invalid/test"}],
        }]
        self.sources()
        self.run_build()
        self.records[0]["sections"][0]["text"] = "Updated"
        self.sources()

        read_counts = {}
        orig_read_bytes = Path.read_bytes

        def counting_read_bytes(path_obj):
            rel = None
            try:
                rel = path_obj.resolve().relative_to(self.root.resolve()).as_posix()
            except ValueError:
                pass
            if rel is not None:
                read_counts[rel] = read_counts.get(rel, 0) + 1
            return orig_read_bytes(path_obj)

        with patch.object(inc.shutil, "copytree", side_effect=AssertionError("copytree should not be called")), \
                patch.object(Path, "read_bytes", counting_read_bytes):
            out = self.run_build("--incremental", "a0")
        self.assertIn("1 card pages written", out)
        # Unchanged runtime files in root are hashed only once across all 4 digest points.
        self.assertEqual(read_counts.get("img/other.webp"), 1)
        self.assertEqual(read_counts.get("cards/other.html"), 1)
        # Saved runtime digest and sw.js match fresh uncached runtime_digest exactly.
        saved_state = json.loads((self.root / inc.STATE).read_text(encoding="utf-8"))
        self.assertEqual(saved_state["runtime"], inc.runtime_digest(self.root))
        self.assert_matches_full_build()

        # Verify RuntimeDigestCache.invalidate forces re-read even with preserved size & mtime.
        target = self.root / "img/other.webp"
        target.write_bytes(b"aaaa")
        st = target.stat()
        cache = inc.RuntimeDigestCache(self.root)
        h1 = cache.file_digest(self.root, "img/other.webp")
        target.write_bytes(b"bbbb")
        import os
        os.utime(target, ns=(st.st_atime_ns, st.st_mtime_ns))
        cache.invalidate(["img/other.webp"])
        h2 = cache.file_digest(self.root, "img/other.webp")
        self.assertNotEqual(h1, h2)

    def test_concurrent_runtime_edit_during_build_is_rejected(self):
        self.append()
        orig_update_sw = build.update_service_worker
        tampered = False

        def tamper_during_build(*args, **kwargs):
            nonlocal tampered
            result = orig_update_sw(*args, **kwargs)
            if not tampered:
                tampered = True
                (self.root / "img/other.webp").write_bytes(b"concurrently modified image bytes!")
            return result

        before = {k: v for k, v in self.state().items() if k != "img/other.webp"}
        with patch.object(build, "update_service_worker", tamper_during_build), self.assertRaises(SystemExit):
            self.run_build("--incremental", "a6")
        self.assertTrue(tampered)
        after = {k: v for k, v in self.state().items() if k != "img/other.webp"}
        self.assertEqual(before, after)

    def test_historical_seo_titles_are_preserved(self):
        seo = json.loads((self.root / "seo.json").read_text(encoding="utf-8"))
        seo["cards/a0.html"]["title"] = "歷史自訂標題｜測試保留"
        seo["cards/a0.html"]["display_title"] = "歷史顯示標題"
        seo["cards/a0.html"]["tracking_title"] = "歷史追蹤標題"
        self.put("seo.json", seo)

        self.run_build()
        rebuilt_seo = json.loads((self.root / "seo.json").read_text(encoding="utf-8"))
        self.assertEqual(rebuilt_seo["cards/a0.html"]["title"], "歷史自訂標題｜測試保留")
        self.assertEqual(rebuilt_seo["cards/a0.html"]["display_title"], "歷史顯示標題")
        self.assertEqual(rebuilt_seo["cards/a0.html"]["tracking_title"], "歷史追蹤標題")
        html_text = (self.root / "cards/a0.html").read_text(encoding="utf-8")
        self.assertIn("<h1>歷史顯示標題</h1>", html_text)
        self.assertIn('page_title: "歷史追蹤標題"', html_text)

    def test_full_build_aborts_on_missing_or_empty_seo_when_cards_exist(self):
        # Case 1: seo.json is empty object {}
        self.put("seo.json", {})
        before_empty = self.state()
        with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as ctx:
            self.run_build()
        self.assertNotEqual(ctx.exception.code, 0)
        self.assertIn("--allow-empty-seo", err.getvalue())
        self.assertEqual(before_empty, self.state())

        # Case 2: seo.json is missing
        (self.root / "seo.json").unlink()
        before_missing = self.state()
        with contextlib.redirect_stderr(io.StringIO()) as err, self.assertRaises(SystemExit) as ctx:
            self.run_build()
        self.assertNotEqual(ctx.exception.code, 0)
        self.assertIn("seo.json", err.getvalue())
        self.assertEqual(before_missing, self.state())

        # Case 3: explicit --allow-empty-seo succeeds
        self.run_build("--allow-empty-seo")
        rebuilt_seo = json.loads((self.root / "seo.json").read_text(encoding="utf-8"))
        self.assertIn("cards/a0.html", rebuilt_seo)


if __name__ == "__main__":
    unittest.main()
