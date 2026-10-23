"""Conservative dependency builds. No timestamps, medical edits, or Git mutations."""
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

STATE = "outputs/incremental-build/state.json"
SOURCES = ("cards.json", "seo.json", "data/card_content.json")
RULES = ("build.py", "scripts/incremental_build.py", "scripts/site_footer.py",
         "scripts/site_header.py", "scripts/acne_pilot.py", "scripts/card_archive.py",
         "templates/site-footer.html", "css/base.css", "author.html",
         "data/acne_navigation.json", "cards.retired.json")
GLOBALS = ("seo.json", "all-cards.html", "sitemap.xml", "sitemap-main.xml",
           "sw.js", "robots.txt", "data/card_text_web_integration_report.md")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write_if_changed(path, text, encoding="utf-8", newline="\n", preserve_index_date=False):
    """Keep identical bytes (and mtime); index export date alone is not a change."""
    path = Path(path)
    if preserve_index_date and path.exists():
        old = path.read_text(encoding=encoding)
        pattern = r"(<span>\?{5})\d{4}-\d{2}-\d{2}(</span>)"
        if re.sub(pattern, r"\1DATE\2", old) == re.sub(pattern, r"\1DATE\2", text):
            return False
    data = text.replace("\r\n", "\n").encode(encoding)
    if path.exists() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError("Incremental baseline unavailable; run python build.py first. "
                         + result.stderr.decode("utf-8", errors="replace"))
    return result.stdout


def head(root):
    try:
        return git(root, "rev-parse", "HEAD").decode().strip()
    except (ValueError, OSError):
        return None


def snapshot(root):
    return {"version": 1, "head": head(root),
            "sources": {p: json.loads((root / p).read_text(encoding="utf-8")) for p in SOURCES},
            "rules": {p: digest((root / p).read_bytes().replace(b"\r\n", b"\n")) for p in RULES},
            "globals": {p: digest((root / p).read_bytes().replace(b"\r\n", b"\n")) for p in GLOBALS if (root / p).exists()},
            "runtime": runtime_digest(root)}


def save_baseline(root):
    write_if_changed(root / STATE, json.dumps(snapshot(root), ensure_ascii=False, indent=2) + "\n")


def baseline(root):
    state = root / STATE
    if state.exists():
        saved = json.loads(state.read_text(encoding="utf-8"))
        if saved.get("version") == 1 and saved.get("head") == head(root):
            return saved
    revision = head(root)
    if not revision:
        raise ValueError("No Git HEAD or local baseline; run python build.py first.")
    read = lambda p: git(root, "show", f"{revision}:{p}")
    return {"version": 1, "head": revision,
            "sources": {p: json.loads(read(p)) for p in SOURCES},
            "rules": {p: digest(read(p).replace(b"\r\n", b"\n")) for p in RULES},
            "globals": {p: digest(read(p).replace(b"\r\n", b"\n")) for p in GLOBALS}, "runtime": None}


def runtime_paths(root):
    # Public files only: omit authoring sources, management, prototypes and caches.
    paths = {p.relative_to(root).as_posix() for p in root.iterdir()
             if p.is_file() and p.suffix.lower() in {".html", ".js", ".css", ".json", ".png", ".ico", ".webmanifest"}}
    for directory in ("cards", "img", "assets", "css", "js", "topics", "web", "data"):
        for p in (root / directory).rglob("*"):
            if p.is_file() and p.suffix.lower() in {".html", ".js", ".css", ".json", ".webp", ".png", ".jpg", ".jpeg", ".svg", ".ico", ".woff", ".woff2"}:
                paths.add(p.relative_to(root).as_posix())
    return paths - {"sw.js", "cards.manual.json", "data/card_content.json"}


def runtime_digest(root, overlay=None, worker=None, extra=()):
    if worker is None:
        worker = (root / "sw.js").read_text(encoding="utf-8") if (root / "sw.js").exists() else ""
        worker = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = '';", worker)
    paths = runtime_paths(root)
    paths.update(p.removeprefix("./").split("?")[0] for p in extra if p != "./")
    if overlay:
        paths.update(runtime_paths(overlay))
    result = hashlib.sha256(worker.encode("utf-8"))
    for name in sorted(paths):
        path = overlay / name if overlay and (overlay / name).is_file() else root / name
        result.update(name.encode("utf-8") + b"\0")
        result.update(hashlib.sha256(path.read_bytes()).digest() if path.is_file() else b"missing")
    return result.hexdigest()


def worker_version(root, overlay, worker, extra):
    normalized = re.sub(r"const CACHE_NAME = '.*?';", "const CACHE_NAME = '';", worker)
    return "pwa-cache-v" + runtime_digest(root, overlay, normalized, extra)[:24]


def content_index(records):
    return {r["image"].replace("\\", "/"): r for r in records
            if isinstance(r, dict) and r.get("matchConfidence") == "high" and r.get("image")}


def owners(build, cards):
    result = {}
    for series, card in cards.items():
        if build.is_scheduled_hidden(card):
            continue
        for index, image in enumerate(card.get("steps") or []):
            if not image:
                continue
            if not image.startswith("img/") or ".." in Path(image).parts:
                raise ValueError("Unsafe image path: " + image)
            page = build.page_for_image(image)
            if page in result and result[page][2] != image:
                raise ValueError("Image stem collision: " + page)
            result.setdefault(page, (series, index, image))
    return result


def signatures(build, cards, contents, seo):
    return {page: [series, index, cards[series], contents.get(image), seo.get(page),
                   [seo.get(build.page_for_image(step)) for step in cards[series].get("steps", [])],
                   build.render_series_links(cards[series], cards)]
            for page, (series, index, image) in owners(build, cards).items()}


def validate_changes(build, old, new, requested):
    old_cards, cards = old["cards.json"], new["cards.json"]
    before, after = owners(build, old_cards), owners(build, cards)
    available = {Path(p).stem for p in after}
    if requested - available:
        raise ValueError("Unknown or unavailable IDs: " + ", ".join(sorted(requested - available)))
    selected_series = {s for s, c in cards.items() if any(Path(i).stem in requested for i in c.get("steps", []))}
    if set(old_cards) - set(cards) or set(before) - set(after):
        raise ValueError("Removal/retirement requires python build.py (full build).")
    for series, card in cards.items():
        previous = old_cards.get(series)
        if not previous and (card.get("hidden") or card.get("publish_at")):
            raise ValueError("New hidden/scheduled series requires python build.py: " + series)
        keys = card.get("favorite_keys")
        if keys and (not isinstance(keys, list) or len(keys) != len(card.get("steps") or [])):
            raise ValueError("favorite_keys must cover every step: " + series)
        if previous:
            if any(previous.get(k) != card.get(k) for k in ("hidden", "publish_at", "order")):
                raise ValueError("Visibility/schedule/order change requires python build.py: " + series)
            steps = previous.get("steps") or []
            if (card.get("steps") or [])[:len(steps)] != steps:
                raise ValueError("Only appending steps is incremental; regroup/reorder requires python build.py: " + series)
            for index in range(len(steps)):
                a, b = previous.get("favorite_keys") or [], card.get("favorite_keys") or []
                old_key = a[index] if index < len(a) else f"{series}-{index}"
                new_key = b[index] if index < len(b) else f"{series}-{index}"
                if old_key != new_key:
                    raise ValueError("Favorite identity change requires python build.py: " + series)
        if previous != card and series not in selected_series:
            raise ValueError("Include an IMAGE_ID from changed series: " + series)
        if not previous and any(build.page_for_image(i) in before for i in card.get("steps", [])):
            raise ValueError("Regrouping existing images requires python build.py: " + series)
    for page in before:
        if before[page][0] != after[page][0]:
            raise ValueError("Primary series changed; use python build.py: " + page)
    for source in ("data/card_content.json", "seo.json"):
        a, b = old[source], new[source]
        if source.endswith("card_content.json"):
            a, b = content_index(a), content_index(b)
        for key in a.keys() | b.keys():
            if a.get(key) != b.get(key):
                page_id = Path(key).stem
                if page_id not in requested and not any(Path(p).stem == page_id and value[0] in selected_series for p, value in after.items()):
                    raise ValueError("Include changed content/SEO IMAGE_ID (or use full build): " + page_id)
    return before, after


@contextmanager
def use_root(build, root):
    names = ("ROOT", "CARDS_DIR", "CARDS_JSON", "SEO_JSON", "CARD_CONTENT_JSON", "CARD_TEXT_REPORT")
    previous = {key: getattr(build, key) for key in names}
    for key, value in previous.items():
        setattr(build, key, root / value.relative_to(previous["ROOT"]))
    try:
        yield
    finally:
        for key, value in previous.items():
            setattr(build, key, value)


def merge_page(old, current, new, name, temp):
    if old == new:
        return current
    if current == old:
        return new
    paths = [temp / f"merge-{i}" for i in range(3)]
    for path, text in zip(paths, (current, old, new)):
        path.write_text(text, encoding="utf-8", newline="\n")
    result = subprocess.run(["git", "merge-file", "-p", *map(str, paths)], capture_output=True)
    if result.returncode:
        raise ValueError(f"Manual/legacy HTML conflict in {name}; no outputs written. Reconcile this page before retrying; do not discard manual edits.")
    return result.stdout.decode("utf-8")


def run_incremental(build, requested):
    root = build.ROOT
    saved = baseline(root)
    current = snapshot(root)
    changed_rules = [p for p in RULES if saved["rules"].get(p) != current["rules"][p]]
    if changed_rules:
        raise ValueError("Shared rules/retirement changed; use python build.py: " + ", ".join(changed_rules))
    old, new = saved["sources"], current["sources"]
    before, after = validate_changes(build, old, new, requested)
    cards = new["cards.json"]
    retired = build.read_retired_cards(root, cards)
    retired_images = {r["image"] for r in retired}
    contents = {i: r for i, r in content_index(new["data/card_content.json"]).items() if i not in retired_images}
    old_contents = {i: r for i, r in content_index(old["data/card_content.json"]).items() if i not in retired_images}
    seo = build.build_seo_index(cards, contents, False, new["seo.json"])
    old_seo = build.build_seo_index(old["cards.json"], old_contents, False, old["seo.json"])
    for page in after:
        for field in ("canonical", "og_url"):
            expected = old_seo[page][field] if page in before else build.abs_url(page)
            if seo[page][field] != expected:
                raise ValueError("URL identity change requires python build.py: " + page + " (" + field + ")")
    previous = signatures(build, old["cards.json"], old_contents, old_seo)
    following = signatures(build, cards, contents, seo)
    affected = {Path(p).stem for p in following if previous.get(p) != following[p]}
    for page in before:
        if not (root / page).is_file():
            raise ValueError("Missing baseline page; use python build.py: " + page)
    for page, (_, _, image) in after.items():
        if not (root / image).is_file():
            raise ValueError("Missing image: " + image)
        if page not in before and (root / page).exists():
            raise ValueError("New page would overwrite an existing file: " + page)
    if saved["runtime"] is None:
        changed = set(git(root, "diff", "HEAD", "--name-only", "-z").decode("utf-8").split("\0"))
        changed.update(git(root, "ls-files", "--others", "--exclude-standard", "-z").decode("utf-8").split("\0"))
        runtime_changed = bool(changed & (runtime_paths(root) | {"sw.js"}))
    else:
        runtime_changed = saved["runtime"] != current["runtime"]
    missing_globals = any(not (root / p).is_file() for p in GLOBALS)
    for name, expected in saved.get("globals", {}).items():
        if name not in ("seo.json", "sw.js") and (root / name).is_file() and digest((root / name).read_bytes().replace(b"\r\n", b"\n")) != expected:
            raise ValueError("Generated global output edited manually; reconcile before building: " + name)
    for name in ("404.html", "cards/404.html", "index.html", "public.html", "retired-cards.html", "sw.js") + tuple(r["page"] for r in retired):
        if not (root / name).is_file():
            raise ValueError("Missing structural output; use python build.py: " + name)
    if not affected and old == new and not runtime_changed and not missing_globals:
        print("Incremental: 0 affected pages; no public outputs changed.")
        return
    # Prepare everything off-tree; validation/merge failure cannot leave partial outputs.
    (root / "outputs").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="incremental-stage-", dir=root / "outputs") as directory:
        stage = Path(directory)
        for name in set(SOURCES + RULES + GLOBALS + ("index.html", "public.html", "retired-cards.html")):
            source = root / name
            if source.is_file():
                (stage / name).parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(source, stage / name)
        shutil.copytree(root / "cards", stage / "cards")
        rendered = build.generate_card_pages(cards, seo, contents, affected, render_only=True)
        old_rendered = build.generate_card_pages(old["cards.json"], old_seo, old_contents, affected, render_only=True)
        changed_pages = []
        for page, text in rendered.items():
            existing = root / page
            if existing.exists():
                original_text = existing.read_text(encoding="utf-8")
                text = merge_page(old_rendered[page], original_text, text, page, stage)
                if text == original_text:
                    continue  # Preserve existing bytes, including CRLF, when the render did not change.
            if write_if_changed(stage / page, text):
                changed_pages.append(page)
        with use_root(build, stage):
            # Homepage lists consume cards.json at runtime. Footer/template changes are rejected above.
            write_if_changed(stage / "seo.json", json.dumps(seo, ensure_ascii=False, indent=2) + "\n")
            write_if_changed(stage / "all-cards.html", build.render_all_cards_page(cards, seo), preserve_index_date=True)
            build.build_card_text_integration_report(contents)
            build.update_sitemap(list(after), contents)
            build.update_robots()
            build.update_service_worker(cards, list(after), [r["page"] for r in retired], source_root=root)
        names = changed_pages + list(GLOBALS)
        # Recheck inputs before publishing, so an editor cannot silently race planning.
        if snapshot(root) != current:
            raise ValueError("Inputs changed during build; retry. No outputs written.")
        originals = {name: (root / name).read_bytes() if (root / name).exists() else None for name in names}
        written = []
        try:
            for name in names:
                data = (stage / name).read_bytes()
                if originals[name] != data:
                    (root / name).parent.mkdir(parents=True, exist_ok=True)
                    written.append(name)
                    (root / name).write_bytes(data)
            result_state = snapshot(root)
            expected_sources = {**new, "seo.json": seo}
            if result_state["sources"] != expected_sources or result_state["rules"] != current["rules"]:
                raise ValueError("Sources changed while writing outputs; rolled back. Retry after editing stops.")
            write_if_changed(root / STATE, json.dumps(result_state, ensure_ascii=False, indent=2) + "\n")
        except (OSError, ValueError):
            for name in reversed(written):
                if originals[name] is None:
                    (root / name).unlink(missing_ok=True)
                else:
                    (root / name).write_bytes(originals[name])
            raise
    print(f"Incremental: {len(affected)} affected pages; {len(changed_pages)} card pages written.")
    print("Card pages: " + (", ".join(changed_pages) or "none"))
    print("Updated outputs: " + (", ".join(written) or "none"))
