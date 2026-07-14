"""Invariant checks for the mechanical oral-liquid website export."""
import json
from collections import Counter
from pathlib import Path

B = Path(__file__).resolve().parent
data = json.loads((B / "final" / "oral_liquid_meds_final.json").read_text(encoding="utf-8"))
products = data["products"]
assert data["product_count"] == len(products) == 1034
assert Counter(item["preparation_type"] for item in products) == {"ready_to_use": 963, "requires_reconstitution": 71}
assert sum(item["concentration_pending"] for item in products) == 88
assert sum(item["has_display_concentration"] for item in products) == 954
assert sum(item["has_normalized_per_ml"] for item in products) == 937
assert len({item["license_number"] for item in products}) == 1034
assert all(item["route_normalized"] == "oral" and item["active_ingredients"] for item in products)
blocked = ("點眼", "眼用", "點耳", "點鼻", "鼻用", "靜脈", "注射", "吸入", "灌腸", "浣腸", "漱口", "外用")
assert not any(any(term in item["dosage_form_raw"] for term in blocked) for item in products)
for item in products:
    for active in item["active_ingredients"]:
        if active["display_concentration"] and "/5 mL" in active["display_concentration"]:
            assert "/5 mL" in active["display_concentration"], "5-mL display basis was lost"
        assert not (active["normalized_unit_per_ml"] and active["normalized_unit_per_ml"].endswith("/mL") and active["display_concentration"].endswith("/bottle"))
print("PASS: oral-liquid website export invariants verified.")
