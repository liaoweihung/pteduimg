"""Opt-in integration on a disposable copy of the real repository, never its outputs.

python -B tests/verify_incremental_repository.py
Uses existing content/image copies solely as synthetic fixtures, not new medical cards.
"""
import copy
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts import incremental_build as inc


def snapshot(root):
    return {p.name: (p.read_bytes(), p.stat().st_mtime_ns)
            for p in (root / "cards").glob("*.html")}


def assert_unchanged(root, before, allowed=()):
    for name, value in before.items():
        if name not in allowed:
            path = root / "cards" / name
            assert (path.read_bytes(), path.stat().st_mtime_ns) == value, name


class Links(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def assert_append(root, before, old_steps, new_step):
    steps = old_steps + [new_step]
    names = [Path(step).stem + ".html" for step in steps]
    allowed = set()
    for index, name in enumerate(names):
        text = (root / "cards" / name).read_text(encoding="utf-8")
        count = f"{index + 1}/{len(steps)}"
        assert f'<span class="page-count">{count}</span>' in text, name
        links = Links(text).links
        for label, target in [("上一張", names[index - 1]),
                              ("下一張", names[(index + 1) % len(names)])]:
            nav = [a for a in links if a.get("aria-label") == label]
            assert len(nav) == 2 and all(a.get("href") == "../cards/" + target for a in nav), name
        pattern = r'(<ol class="related-list" aria-label="同系列圖卡">)(.*?)(</ol>)'
        related = re.search(pattern, text, re.S)
        assert related, name
        assert [a.get("href") for a in Links(related[2]).links] == [
            "../cards/" + n for n in names], name
        assert [a.get("href") for a in Links(related[2]).links if a.get("aria-current") == "page"] == ["../cards/" + name], name
        if name in before:
            old = before[name][0].decode("utf-8").replace("\r\n", "\n")
            old_related = re.search(pattern, old, re.S)
            assert old_related, name
            assert re.findall(r"<li>.*?</li>", related[2], re.S)[:-1] == re.findall(
                r"<li>.*?</li>", old_related[2], re.S), name
            # Only counts, the two navigation pairs and the ordered sibling list may change.
            def stable(value):
                value = re.sub(pattern, r'\1<SIBLINGS>\3', value, flags=re.S)
                value = re.sub(r'href="[^"]+"(?= aria-label="(?:上一張|下一張)")', 'href="<NAV>"', value)
                return value
            import difflib
            evidence = Path(__file__).resolve().parents[1] / "outputs/append-html-diffs"
            evidence.mkdir(exist_ok=True)
            (evidence / (name + ".diff")).write_text("".join(difflib.unified_diff(
                old.splitlines(True), text.splitlines(True))), encoding="utf-8")
            expected = old.replace(f"{index + 1}/{len(old_steps)}", count)
            assert stable(expected) == stable(text), "Unexpected HTML change: " + name
            allowed.add(name)  # Each allowed page has just passed field-level checks.
    assert_unchanged(root, before, allowed)
    return allowed


def main():
    source = build.ROOT
    (source / "outputs").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="incremental-repository-test-", dir=source / "outputs") as directory:
        root = Path(directory)
        paths = set(inc.git(source, "ls-files", "-z").decode("utf-8").split("\0")) - {""}
        paths.update(inc.RULES)
        for name in paths:
            if (source / name).is_file():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source / name, root / name)
        with inc.use_root(build, root):
            # Test setup only: preserve actual legacy HTML instead of full-regenerating it.
            inc.save_baseline(root)
            cards = build.read_cards()
            manual = json.loads((root / "cards.manual.json").read_text(encoding="utf-8"))
            records = json.loads((root / "data/card_content.json").read_text(encoding="utf-8"))
            seed = next(r for r in records if Path(r["image"]).stem == "wempty_suspension")
            original = {p.name: (inc.digest(p.read_bytes()), p.stat().st_mtime_ns) for p in (root / "cards").glob("*.html")}

            def add(page, series):
                image = "img/" + page + ".webp"
                shutil.copyfile(root / seed["image"], root / image)
                record = copy.deepcopy(seed)
                record.update(image=image, cardId=series, url=build.abs_url("cards/" + page + ".html"))
                records.append(record)
                cards[series]["steps"].append(image)
                manual[series] = copy.deepcopy(cards[series])
                for name, data in (("cards.json", cards), ("cards.manual.json", manual), ("data/card_content.json", records)):
                    inc.write_if_changed(root / name, json.dumps(data, ensure_ascii=False, indent=2) + "\n")
                build.main(["--incremental", page])

            cards["incremental_test"] = copy.deepcopy(cards["pediatric_gi_syrup"])
            cards["incremental_test"]["steps"] = []
            add("incremental_test_new", "incremental_test")
            assert all(original[p.name] == (inc.digest(p.read_bytes()), p.stat().st_mtime_ns)
                       for p in (root / "cards").glob("*.html") if p.name in original)
            print(f"New series: 1 page added; {len(original)} existing HTML hashes and mtimes unchanged.")
            before_append = snapshot(root)
            old_steps = list(cards["pediatric_gi_syrup"]["steps"])
            add("incremental_test_append", "pediatric_gi_syrup")
            allowed = assert_append(root, before_append, old_steps,
                                    "img/incremental_test_append.webp")
            print(f"Append: {len(allowed)} existing dependent pages verified; unrelated bytes and mtimes unchanged.")
            active = inc.owners(build, cards)
            for name in ("seo.json", "all-cards.html", "sitemap.xml", "sitemap-main.xml", "sw.js"):
                text = (root / name).read_text(encoding="utf-8")
                assert all(p in text for p in active), name
            print(f"All five global indexes include all {len(active)} active pages.")
            before = {p: (inc.digest((root / p).read_bytes()), (root / p).stat().st_mtime_ns)
                      for p in list(active) + list(inc.GLOBALS)}
            build.main(["--incremental", "incremental_test_append"])
            assert all(value == (inc.digest((root / p).read_bytes()), (root / p).stat().st_mtime_ns) for p, value in before.items())
            print("Repeated incremental: zero byte or mtime changes.")
        result = subprocess.run([sys.executable, "-B", "scripts/check_site.py"], cwd=root, capture_output=True)
        log = source / "outputs/incremental-repository-check-site.log"
        log.write_bytes(result.stdout + result.stderr)
        print(f"Isolated check_site exit={result.returncode}; log={log}")
        if result.returncode:
            print(result.stdout.decode("utf-8", errors="replace")[-4000:])
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()
