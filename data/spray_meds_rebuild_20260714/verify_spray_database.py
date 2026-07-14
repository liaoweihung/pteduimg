"""Non-mutating quality checks for the phase-1 spray data export."""
import csv
from pathlib import Path

B = Path(__file__).resolve().parent
def rows(name):
    with (B/name).open(encoding="utf-8-sig", newline="") as f: return list(csv.DictReader(f))

products = rows("products.csv")
required = ["license_number","license_year","chinese_name","dosage_form_raw","indication_raw","active_ingredient_raw","license_status","license_expiry_date","source_id"]
assert len({r["license_number"] for r in products}) == len(products), "duplicate included licence"
assert all(r["application_site"] in {"nasal","throat","oral_mucosal","oral_and_throat"} for r in products), "invalid included application site"
assert all(all(r[x] for x in required) for r in products), "missing mandatory product core field"
assert not any("吸入" in r["dosage_form_raw"] for r in products), "pulmonary form included"
for name in ["excluded_records.csv","manual_review_queue.csv"]:
    values=[r["license_number"] for r in rows(name)]
    assert len(values)==len(set(values)), f"duplicate licence in {name}"
print(f"PASS: {len(products)} included products; mandatory core fields present; licence uniqueness and local-site checks passed.")
