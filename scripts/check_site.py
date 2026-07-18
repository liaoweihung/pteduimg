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


def is_scheduled_hidden(card: dict) -> bool:
    return isinstance(card, dict) and card.get("hidden") is True and bool(card.get("publish_at"))


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
        skip_pages = is_scheduled_hidden(card)
        for step in card.get("steps", []):
            if not isinstance(step, str) or not step.startswith("img/"):
                continue
            image_path = ROOT / step
            page_path = page_for_image(step)
            if not skip_pages:
                pages.append(page_path)
            if not image_path.exists():
                missing_images.append(step)
            if not skip_pages and not page_path.exists():
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
    medicine_pages = [
        "ingredient-explorer.html", "eye_drop_explorer.html", "web/taiwan_medicinal_patch_database_v2.html",
        "spray_medicine_explorer.html", "suppository_medicine_explorer.html", "oral_liquid_medicine_explorer.html",
    ]
    for name in medicine_pages:
        html = read_text(ROOT / name)
        check(
            html.count("medicine-explorer-analytics.js") == 1 and "G-T5R33JYTC0" in read_text(ROOT / "js" / "medicine-explorer-analytics.js"),
            f"{name} has one guarded shared GA loader",
            f"{name} is missing or duplicates the shared GA loader",
            failures,
        )
        check(
            html.count("feedback.html?source=") == 0,
            f"{name} delegates one feedback link to the shared shell",
            f"{name} has a duplicate page-level feedback link",
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


def check_oral_liquid_explorer(failures: list[str]) -> None:
    html_path = ROOT / "oral_liquid_medicine_explorer.html"
    js_path = ROOT / "js" / "oral-liquid-medicine-explorer.js"
    data_path = ROOT / "data" / "oral_liquid_meds_rebuild_20260714" / "final" / "oral_liquid_meds_final.json"
    css_path = ROOT / "css" / "oral-liquid-medicine-explorer.css"
    required = [html_path, js_path, data_path, css_path]
    check(all(path.exists() for path in required), "oral-liquid explorer assets exist", "oral-liquid explorer assets are missing", failures)
    if not all(path.exists() for path in required):
        return
    html = read_text(html_path)
    js = read_text(js_path)
    sw = read_text(ROOT / "sw.js")
    data = load_json(data_path)
    check(data.get("product_count") == 1034 and len(data.get("products", [])) == 1034, "oral-liquid export has 1,034 formal products", "oral-liquid export count is not 1,034", failures)
    summary = data.get("summary", {})
    check(summary.get("ready_to_use") == 963 and summary.get("requires_reconstitution") == 71, "oral-liquid preparation counts match formal data", "oral-liquid preparation counts do not match", failures)
    check(summary.get("unresolved_candidates_excluded") == 105, "oral-liquid unresolved candidates stay excluded", "oral-liquid unresolved candidate count is wrong", failures)
    check(all("錠劑" not in product.get("dosage_form_raw", "") and "膠囊" not in product.get("dosage_form_raw", "") for product in data.get("products", [])), "oral-liquid export excludes tablets and capsules", "oral-liquid export includes a solid oral form", failures)
    shell = read_text(ROOT / "js" / "medicine-explorer-shell.js")
    check("MEDICINE_EXPLORER_PAGE='oral'" in html and "medicine-explorer-shell.js" in html, "oral-liquid explorer uses shared shell", "oral-liquid explorer does not use shared shell", failures)
    check("slice((state.page-1)*20,state.page*20)" in shell, "shared shell paginates results by 20", "shared shell does not paginate results by 20", failures)
    check("官方濃度" in shell and "配製方式" in shell, "oral-liquid explorer keeps concentration/preparation fields", "oral-liquid explorer is missing concentration/preparation fields", failures)
    check("oral_liquid_medicine_explorer.html" in sw and "oral_liquid_meds_final.json" in sw, "service worker includes oral-liquid assets", "service worker misses oral-liquid assets", failures)


def check_medicine_shell(failures: list[str]) -> None:
    shell = read_text(ROOT / "js" / "medicine-explorer-shell.js")
    css = read_text(ROOT / "css" / "medicine-explorer-theme.css")
    for needle in ("依適應症", "依成分", "搜尋產品", "me-return", "me-db-pill", "藥證資料查詢截至民國115年7月", "product_detail_open"):
        check(needle in shell or needle in css, f"shared medicine shell has {needle}", f"shared medicine shell is missing {needle}", failures)
    for banned in ("Breadth Score", "Bridge Score", "Archetype", "Top 5"):
        check(banned not in shell, f"shared medicine shell hides {banned}", f"shared medicine shell exposes {banned}", failures)


def check_medicine_data_regression(failures: list[str]) -> None:
    topical = read_text(ROOT / "ingredient-explorer.html")
    topical_match = re.search(r"window\.EXPLORER_DATA=(\{[\s\S]*?\});\s*\nconst ", topical)
    topical_data = json.loads(topical_match.group(1)) if topical_match else {}
    check(topical_data.get("metadata", {}).get("productCount") == 2250 and topical_data.get("metadata", {}).get("classCount") == 17, "topical data keeps 2,250 products / 17 classes", "topical product or class baseline changed", failures)
    patch_bytes = (ROOT / "web" / "taiwan_medicinal_patch_database_v2.html").read_bytes()
    patch_match = re.search(br'<script id="patch-data" type="application/json">(.*?)</script>', patch_bytes, flags=re.S)
    patch_data = json.loads(patch_match.group(1).decode("utf-8")) if patch_match else {}
    check(len(patch_data.get("products", [])) == 404 and len(patch_data.get("categories", [])) == 15, "patch data keeps 404 products / 15 categories", "patch product or category baseline changed", failures)
    checks = [
        ("eye", "eye_meds_rebuild_20260711/final/eye_meds_final.json", 492, 63),
        ("spray", "spray_meds_rebuild_20260714/final/spray_meds_final.json", 141, 12),
        ("suppository", "suppository_meds_rebuild_20260714/final/suppository_meds_final.json", 148, 14),
        ("oral liquid", "oral_liquid_meds_rebuild_20260714/final/oral_liquid_meds_final.json", 1034, 17),
    ]
    for label, rel_path, count, class_count in checks:
        data = load_json(ROOT / "data" / rel_path)
        products = data.get("products", [])
        if label == "eye":
            classes = {item.get("class_name") for product in products for item in product.get("classes", []) if item.get("class_name")}
        else:
            classes = {item for product in products for item in product.get("therapeutic_classes", [])}
        check(len(products) == count and len(classes) == class_count, f"{label} data keeps {count} products / {class_count} classes", f"{label} product or class baseline changed", failures)


def check_tcm_formula_explorer(failures: list[str]) -> None:
    data_dir = ROOT / "data" / "tcm_formula_explorer"
    required = [
        ROOT / "tcm_formula_explorer.html",
        ROOT / "css" / "tcm-formula-explorer.css",
        ROOT / "js" / "tcm-formula-explorer.js",
        data_dir / "index.json",
        data_dir / "formulas.json",
        data_dir / "relationship_analysis.json",
    ]
    check(all(path.exists() for path in required), "TCM formula explorer assets exist", "TCM formula explorer assets are missing", failures)
    if not all(path.exists() for path in required):
        return
    index = load_json(data_dir / "index.json")
    formulas = load_json(data_dir / "formulas.json")
    chunks = sorted(data_dir.glob("products-*.json"))
    check(index.get("productCount") == 21196 and len(index.get("products", [])) == 21196, "TCM index keeps 21,196 products", "TCM index product count is wrong", failures)
    check(len(formulas.get("formulas", {})) == 204, "TCM formula table keeps 204 formulas", "TCM formula table count is wrong", failures)
    check(len(chunks) == 32, "TCM explorer keeps 32 detail chunks", "TCM explorer detail chunk count is wrong", failures)
    js = read_text(ROOT / "js" / "tcm-formula-explorer.js")
    sw = read_text(ROOT / "sw.js")
    check("products-${String(chunk).padStart(2, '0')}.json" in js and "state.chunks" in js, "TCM details load on demand", "TCM detail chunks are not lazy loaded", failures)
    check("index.json" in sw and "formulas.json" in sw and "relationship_analysis.json" in sw and "products-" not in sw, "TCM core cache excludes detail chunks", "TCM detail chunks are pre-cached", failures)
    check("非歷史源流或製造商聲明" in js, "TCM AI inference notice is present", "TCM AI inference notice is missing", failures)


def main() -> int:
    failures: list[str] = []
    cards, _manual = check_json_files(failures)
    pages = check_card_pages(cards, failures)
    check_home_viewer(failures)
    check_static_card_template(pages, failures)
    check_analytics_guards(failures)
    check_service_worker(failures)
    check_oral_liquid_explorer(failures)
    check_medicine_shell(failures)
    check_medicine_data_regression(failures)
    check_tcm_formula_explorer(failures)

    if failures:
        print("\nSite check failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("\nSite check passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
