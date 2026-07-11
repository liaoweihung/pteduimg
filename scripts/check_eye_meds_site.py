import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "eye_meds" / "site_data.json"


def fail(message):
    raise SystemExit(message)


def main():
    if not DATA.exists():
        fail("Missing data/eye_meds/site_data.json; run scripts/build_eye_meds_site.py first.")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    products = data["products"]
    active = [p for p in products if p["status_group"] == "active"]
    inactive = [p for p in products if p["status_group"] != "active"]
    summary = data["summary"]

    if summary["active_product_count"] != len(active):
        fail("Active product count does not match products.")
    if summary["inactive_product_count"] != len(inactive):
        fail("Inactive product count does not match products.")
    if not active:
        fail("No active products found.")
    if any(p["status_group"] != "active" and p["default_include_in_search"] for p in products):
        fail("Inactive product marked as default include in search.")
    if any(s["role"] == "preservative" for p in products for s in p["active_ingredients"]):
        fail("Preservative leaked into active ingredient list.")
    if any(s["role"] == "active" for p in products for s in p["preservatives"]):
        fail("Active ingredient leaked into preservative list.")
    if any(s["role"] in {"active", "preservative"} for p in products for s in p["excipients"]):
        fail("Active ingredient or preservative leaked into excipient list.")

    required = [
        ROOT / "eye-meds.html",
        ROOT / "css" / "eye-meds.css",
        ROOT / "scripts" / "eye_meds_app.js",
        ROOT / "DATA_AUDIT.md",
        ROOT / "research" / "work_handoff" / "IMPORT_REPORT.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.exists()]
    if missing:
        fail("Missing required files: " + ", ".join(missing))

    print("eye meds site checks passed")


if __name__ == "__main__":
    main()
