from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path):
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def page_for_image(image_path: str) -> Path:
    return ROOT / "cards" / f"{Path(image_path).stem}.html"


def check(condition: bool, ok: str, fail: str, failures: list[str]) -> None:
    if condition:
        print(f"OK   {ok}")
    else:
        print(f"FAIL {fail}")
        failures.append(fail)


def check_json_files(failures: list[str]) -> tuple[dict, dict]:
    cards = load_json(ROOT / "cards.json")
    manual = load_json(ROOT / "cards.manual.json")
    check(isinstance(cards, dict), "cards.json is valid", "cards.json must be an object", failures)
    check(
        isinstance(manual, dict),
        "cards.manual.json is valid",
        "cards.manual.json must be an object",
        failures,
    )
    return cards, manual


def check_card_pages(cards: dict, failures: list[str]) -> list[Path]:
    pages: list[Path] = []
    missing_pages: list[str] = []
    missing_images: list[str] = []

    for card in cards.values():
        for step in card.get("steps", []):
            if not isinstance(step, str) or not step.startswith("img/"):
                continue
            image_path = ROOT / step
            page_path = page_for_image(step)
            pages.append(page_path)
            if not image_path.exists():
                missing_images.append(step)
            if not page_path.exists():
                missing_pages.append(rel(page_path))

    check(not missing_images, "all referenced images exist", f"missing images: {missing_images[:5]}", failures)
    check(not missing_pages, "all card pages exist", f"missing card pages: {missing_pages[:5]}", failures)
    return pages


def check_home_viewer(failures: list[str]) -> None:
    base_css = read_text(ROOT / "css" / "base.css")
    for name in ("index.html", "public.html"):
        html = read_text(ROOT / name)
        check(
            "side-nav-zone side-nav-left" in html and "side-nav-zone side-nav-right" in html,
            f"{name} keeps transparent side tap zones",
            f"{name} is missing transparent side tap zones",
            failures,
        )
        check(
            'class="nav-btn left-btn"' in html and 'class="nav-btn right-btn"' in html,
            f"{name} keeps visible bottom nav buttons",
            f"{name} is missing visible bottom nav buttons",
            failures,
        )
        check(
            "EDUCATION_DATA_CACHE_KEY" in html and "loadCachedEducationData" in html,
            f"{name} renders cached card data first",
            f"{name} is missing cached-data rendering",
            failures,
        )
        check(
            "cards.json?v=" not in html and "no-store" not in html,
            f"{name} does not bypass cards.json cache",
            f"{name} bypasses cards.json cache",
            failures,
        )

    check(
        ".side-nav-zone" in base_css and "background: transparent" in base_css,
        "transparent side zones are styled",
        "css/base.css is missing transparent side zone styles",
        failures,
    )


def check_static_card_template(pages: list[Path], failures: list[str]) -> None:
    sample_pages = [page for page in pages if page.exists()][:10]
    missing_sw: list[str] = []
    missing_side_links: list[str] = []
    missing_bottom_nav: list[str] = []
    noisy_h1: list[str] = []

    for page in sample_pages:
        html = read_text(page)
        if "navigator.serviceWorker.register('../sw.js')" not in html:
            missing_sw.append(rel(page))
        if "image-side-link prev" not in html or "image-side-link next" not in html:
            missing_side_links.append(rel(page))
        if "page-arrow" not in html or "page-count" not in html:
            missing_bottom_nav.append(rel(page))
        h1_match = re.search(r"<h1>(.*?)</h1>", html, flags=re.S)
        if h1_match and re.search(r"第\s*\d+\s*張圖卡", h1_match.group(1)):
            noisy_h1.append(rel(page))

    check(not missing_sw, "sample card pages register service worker", f"card pages missing SW: {missing_sw}", failures)
    check(
        not missing_side_links,
        "sample card pages keep transparent side links",
        f"card pages missing side links: {missing_side_links}",
        failures,
    )
    check(
        not missing_bottom_nav,
        "sample card pages keep bottom page navigation",
        f"card pages missing bottom nav: {missing_bottom_nav}",
        failures,
    )
    check(
        not noisy_h1,
        "sample card page titles omit step-number suffix",
        f"card page h1 still contains step suffix: {noisy_h1}",
        failures,
    )


def check_analytics_guards(failures: list[str]) -> None:
    protected_pages = [
        "index.html",
        "public.html",
        "calc.html",
        "growth-calculator.html",
        "pregnancy-calculator.html",
        "rx-refillable-date.html",
    ]
    for name in protected_pages:
        html = read_text(ROOT / name)
        check(
            "isPrivateNetworkHost" in html and "window.isAnalyticsDisabled" in html,
            f"{name} has local/private GA guard",
            f"{name} is missing local/private GA guard",
            failures,
        )
        check(
            '<script async src="https://www.googletagmanager.com/gtag/js' not in html,
            f"{name} does not load GA unconditionally",
            f"{name} loads GA unconditionally",
            failures,
        )


def check_service_worker(failures: list[str]) -> None:
    sw = read_text(ROOT / "sw.js")
    checks = [
        ("RUNTIME_CACHE", "runtime cache exists", "sw.js is missing runtime cache"),
        ("pwa-runtime-v1", "runtime cache has stable name", "sw.js runtime cache name changed/missing"),
        (
            "cacheName !== CACHE_NAME && cacheName !== RUNTIME_CACHE",
            "runtime cache survives version cleanup",
            "runtime cache may be deleted on each update",
        ),
        ("coreUrlsToCache", "core pre-cache is limited", "sw.js is missing core pre-cache list"),
        ("caches.match(request).then(cachedResponse", "requests check cache first", "sw.js is not cache-first"),
    ]
    for needle, ok, fail in checks:
        check(needle in sw, ok, fail, failures)


def main() -> int:
    failures: list[str] = []
    cards, _manual = check_json_files(failures)
    pages = check_card_pages(cards, failures)
    check_home_viewer(failures)
    check_static_card_template(pages, failures)
    check_analytics_guards(failures)
    check_service_worker(failures)

    if failures:
        print("\nSite check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nSite check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
