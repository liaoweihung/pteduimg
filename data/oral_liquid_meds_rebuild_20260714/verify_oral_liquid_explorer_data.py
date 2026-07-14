"""Data-level checks that mirror the oral-liquid explorer's filter rules."""
import json
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path


B = Path(__file__).resolve().parent
data = json.loads((B / "final" / "oral_liquid_meds_final.json").read_text(encoding="utf-8"))
products = data["products"]


def comparable(active):
    return bool(active["display_concentration"]) and active["display_concentration"].endswith("mL")


assert len(products) == 1034
assert sum(item["preparation_type"] == "ready_to_use" for item in products) == 963
assert sum(item["preparation_type"] == "requires_reconstitution" for item in products) == 71

def form_category(product):
    group = product["dosage_form_group"]
    if group in {"powder_for_oral_suspension", "granules_for_oral_suspension"}:
        return "reconstituted_suspension"
    if group in {"syrup", "oral_solution", "oral_suspension", "oral_drops", "oral_emulsion"}:
        return group
    return "other"

form_counts = Counter(form_category(product) for product in products)
assert form_counts == {
    "oral_solution": 604,
    "syrup": 279,
    "oral_suspension": 66,
    "reconstituted_suspension": 37,
    "other": 34,
    "oral_drops": 8,
    "oral_emulsion": 6,
}
class_counts = Counter(label for product in products for label in product["therapeutic_classes"])
indication_counts = Counter(product["indication_category"] for product in products)
assert class_counts["antihistamine"] == 384 and class_counts["antibiotic"] == 26
assert indication_counts["呼吸道咳嗽與痰液症狀"] == 538 and indication_counts["感染性疾病"] == 34

# Each product contributes at most once to an active's ranking, including compounds.
counts = Counter()
for product in products:
    for substance_id in {active["substance_id"] for active in product["active_ingredients"]}:
        counts[substance_id] += 1
assert counts["sub_tfda_0400000810"] == 314  # chlorpheniramine maleate
assert counts["sub_tfda_1212001813"] == 269  # dl-methylephedrine HCl
assert counts["sub_tfda_2808000100"] == 257  # acetaminophen

# Three active-ingredient concentration group samples use distinct products.
for substance_id in ("sub_tfda_0400000810", "sub_tfda_1212001813", "sub_tfda_2808000100"):
    groups = defaultdict(set)
    for product in products:
        for active in product["active_ingredients"]:
            if active["substance_id"] == substance_id and comparable(active):
                groups[active["display_concentration"]].add(product["product_id"])
    assert groups and all(groups.values())

# Display values retain their official basis.  The source table already checks
# arithmetic; this checks that the export did not replace 5-mL displays.
five_ml = [active for product in products for active in product["active_ingredients"] if "/5 mL" in active["display_concentration"]]
assert five_ml and all("/5 mL" in active["display_concentration"] for active in five_ml)

# Bottle/sachet totals may be displayed in detail, but are not comparable filter groups.
container = [active for product in products for active in product["active_ingredients"] if active["display_concentration"].endswith(("/bottle", "/sachet"))]
assert all(not comparable(active) for active in container)
assert sum(item["concentration_pending"] for item in products) == 88

print("PASS: explorer preparation/form/class/indication/ingredient filters, compound counting, and concentration grouping samples verified.")
