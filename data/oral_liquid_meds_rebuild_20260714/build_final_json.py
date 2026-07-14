"""Mechanical website export for Taiwan oral-liquid medicines.

This exporter reads only the formal CSV relation tables in this directory.
Manual-review candidates and every non-formal record are intentionally absent.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path


B = Path(__file__).resolve().parent
OUT = B / "final" / "oral_liquid_meds_final.json"


def read(name):
    with (B / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def indication_category(product):
    """Deterministic display grouping from formal indication/class fields."""
    text = f"{product['indication_raw']} {product['therapeutic_class']}".lower()
    rules = [
        ("呼吸道咳嗽與痰液症狀", ("咳", "痰", "cough", "expector", "mucolytic", "broncho")),
        ("過敏與感冒症狀", ("過敏", "allerg", "感冒", "鼻炎", "antihistamine")),
        ("發燒、疼痛與發炎", ("發燒", "疼痛", "痛", "fever", "pain", "analgesic")),
        ("腸胃與排便症狀", ("胃", "腸", "便秘", "腹瀉", "嘔吐", "噁心", "gastro", "laxative", "diarr", "emetic")),
        ("感染性疾病", ("感染", "antibiotic", "antiviral", "antifungal", "抗生素", "抗黴菌")),
        ("維生素、礦物質與營養治療", ("維生素", "礦物", "vitamin", "mineral", "缺鐵", "補充")),
        ("神經、心血管與其他慢性用途", ("癲癇", "神經", "心", "血壓", "neurolog", "cardio")),
    ]
    for label, terms in rules:
        if any(term in text for term in terms):
            return label
    return "其他正式核准適應症"


def active_key(row):
    return (
        row["substance_id"],
        row["raw_name"],
        row["display_concentration"],
        row["strength_raw"],
        row["normalization_status"],
    )


products = read("products.csv")
substances = {row["substance_id"]: row for row in read("substances.csv")}
relations = defaultdict(list)
for row in read("product_substances.csv"):
    if row["role"] == "active" and row["confirmation_status"] == "confirmed":
        relations[row["product_id"]].append(row)
classes = defaultdict(list)
for row in read("product_classes.csv"):
    classes[row["product_id"]].append(row["class_id"])
indications = {row["indication_id"]: row for row in read("indications.csv")}
product_indications = defaultdict(list)
for row in read("product_indications.csv"):
    if row["indication_id"] in indications:
        product_indications[row["product_id"]].append(indications[row["indication_id"]])

out = []
for product in sorted(products, key=lambda row: (row["chinese_name"], row["license_number"])):
    active = []
    seen = set()
    for relation in relations[product["product_id"]]:
        key = active_key(relation)
        if key in seen:
            continue
        seen.add(key)
        substance = substances.get(relation["substance_id"], {})
        active.append(
            {
                "substance_id": relation["substance_id"],
                "name": relation["raw_name"] or substance.get("raw_name", ""),
                "normalized_name": relation["normalized_name"] or substance.get("normalized_name", ""),
                "strength_raw": relation["strength_raw"],
                "display_concentration": relation["display_concentration"],
                "normalized_value_per_ml": relation["normalized_value_per_ml"],
                "normalized_unit_per_ml": relation["concentration_normalized"].split(" ", 1)[1] if " " in relation["concentration_normalized"] else "",
                "normalization_status": relation["normalization_status"],
                "parsing_rule": relation["parsing_rule"],
                "confidence": relation["confidence"],
            }
        )
    assert active, product["license_number"]
    pending = any(item["normalization_status"] == "unresolved" for item in active)
    out.append(
        {
            "product_id": product["product_id"],
            "license_number": product["license_number"],
            "chinese_name": product["chinese_name"],
            "english_name": product["english_name"],
            "dosage_form_raw": product["dosage_form_raw"],
            "dosage_form_group": product["dosage_form_group"],
            "preparation_type": product["preparation_type"],
            "route_normalized": product["route_normalized"],
            "indication": product["indication_raw"],
            "indication_category": indication_category(product),
            "indication_relations": product_indications[product["product_id"]],
            "therapeutic_classes": sorted(set(classes[product["product_id"]] or product["therapeutic_class"].split("; "))),
            "active_ingredients": active,
            "concentration_pending": pending,
            "has_display_concentration": any(item["display_concentration"] for item in active),
            "has_normalized_per_ml": any(item["normalized_value_per_ml"] for item in active),
            "license_year": product["license_year"],
            "license_status": product["license_status"],
            "license_expiry_date": product["license_expiry_date"],
            "legal_category": product["legal_category"],
            "applicant": product["applicant"],
            "manufacturer": product["manufacturer"],
            "source_id": product["source_id"],
            "verified_at": product["verified_at"],
            "route_raw": product["route_raw"],
            "inclusion_evidence": product["oral_liquid_inclusion_evidence"],
        }
    )

preparations = Counter(product["preparation_type"] for product in out)
pending = sum(product["concentration_pending"] for product in out)
display = sum(product["has_display_concentration"] for product in out)
per_ml = sum(product["has_normalized_per_ml"] for product in out)
assert len(out) == 1034
assert preparations == {"ready_to_use": 963, "requires_reconstitution": 71}
assert pending == 88
assert display == 954
assert per_ml == 937
assert all(product["route_normalized"] == "oral" for product in out)

payload = {
    "schema_version": "1.0",
    "generated_from": [
        "products.csv",
        "substances.csv",
        "product_substances.csv",
        "indications.csv",
        "product_indications.csv",
        "product_classes.csv",
    ],
    "product_count": len(out),
    "summary": {
        "formal_active_products": len(out),
        "ready_to_use": preparations["ready_to_use"],
        "requires_reconstitution": preparations["requires_reconstitution"],
        "confirmed_active_products": len(out),
        "products_with_display_concentration": display,
        "products_with_normalized_per_ml": per_ml,
        "concentration_pending_products": pending,
        "unresolved_candidates_excluded": 105,
    },
    "products": out,
}
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {len(out)} formal products to {OUT}")
