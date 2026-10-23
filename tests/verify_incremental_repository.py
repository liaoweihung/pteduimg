"""Opt-in integration on a disposable copy of the real repository, never its outputs.

python -B tests/verify_incremental_repository.py
Uses existing content/image copies solely as synthetic fixtures, not new medical cards.
"""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import build
from scripts import incremental_build as inc


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
            add("incremental_test_append", "pediatric_gi_syrup")
            unchanged = [p for p in (root / "cards").glob("*.html") if p.name in original and p.stem != "wempty_suspension"]
            assert all(original[p.name] == (inc.digest(p.read_bytes()), p.stat().st_mtime_ns) for p in unchanged)
            for page in ("wempty_suspension", "incremental_test_append"):
                text = (root / "cards" / (page + ".html")).read_text(encoding="utf-8")
                assert ("1/2" if page == "wempty_suspension" else "2/2") in text
                assert "../cards/" + ("incremental_test_append" if page == "wempty_suspension" else "wempty_suspension") + ".html" in text
            print(f"Append: 2 pages written; {len(unchanged)} unrelated HTML hashes and mtimes unchanged.")
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
