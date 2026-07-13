import csv
import hashlib
import json
import re
import shutil
import unicodedata
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path


BASE = Path(__file__).resolve().parent
CORE = BASE / "core"
ENRICH = BASE / "enrichment"
FINAL = BASE / "final"
CHECKED_AT = datetime.now(timezone(timedelta(hours=8))).replace(microsecond=0).isoformat()

ROLES = {
    "active",
    "preservative",
    "vehicle",
    "buffer",
    "tonicity_agent",
    "viscosity_agent",
    "chelator",
    "surfactant",
    "antioxidant",
    "ph_adjuster",
    "ointment_base",
    "other_excipient",
    "unknown",
}
NON_ACTIVE_ROLES = ROLES - {"active", "unknown"}
SALT_FORM_TOKENS = {
    "acetate",
    "borate",
    "calcium",
    "decahydrate",
    "dihydrate",
    "difumarate",
    "disodium",
    "fumarate",
    "gluconate",
    "hcl",
    "hydrate",
    "hydrochloride",
    "isopropyl",
    "palmitate",
    "phosphate",
    "potassium",
    "sodium",
    "tartrate",
}
NOISE_TOKENS = {
    "as",
    "eq",
    "equiv",
    "equivalent",
    "of",
    "solution",
    "the",
    "to",
    "type",
}


def read_csv(path):
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def clean(value):
    return (value or "").strip()


def compact_space(value):
    return re.sub(r"\s+", " ", clean(value))


def normalize_material_name(value):
    value = unicodedata.normalize("NFKC", clean(value).lower())
    value = value.replace("hydrogen chloride", "hydrochloride")
    value = value.replace("hydrochloride", "hcl")
    value = value.replace("polyvinylpyrrolidone", "polyvinyl pyrrolidone")
    value = value.replace("carboxymethyl cellulose", "carboxymethylcellulose")
    value = re.sub(r"\b(eq\.?|equiv\.?|equivalent)\s+(to|as)\b", " ", value)
    value = re.sub(r"[^a-z0-9]+", " ", value)
    tokens = [token for token in value.split() if token not in NOISE_TOKENS]
    return " ".join(tokens)


def material_variants(*values):
    variants = set()
    for value in values:
        normalized = normalize_material_name(value)
        if not normalized:
            continue
        variants.add(normalized)
        variants.add(re.sub(r"^\d+\s+", "", normalized).strip())
        if normalized.endswith(" hcl"):
            variants.add(normalized[:-4].strip())
        tokens = normalized.split()
        stripped_tokens = [token for token in tokens if token not in SALT_FORM_TOKENS]
        if stripped_tokens:
            variants.add(" ".join(stripped_tokens))
        if "vit" in tokens and "b12" in tokens:
            variants.add(" ".join(token for token in tokens if token not in {"vit", "b12"}))
        if "vitamin" in tokens and "a" in tokens:
            variants.add("vitamin a")
        if normalized.startswith("20 chlorhexidine gluconate"):
            variants.add("chlorhexidine gluconate")
    return {variant for variant in variants if variant}


def row_variants(row):
    return material_variants(
        row.get("substance_raw"),
        row.get("substance_normalized"),
        row.get("standard_name"),
        row.get("base_ingredient_name"),
    )


def create_before_snapshot():
    snapshot = FINAL / "unknown_role_resolution_before_snapshot.zip"
    manifest = FINAL / "unknown_role_resolution_before_snapshot_manifest.json"
    source_files = [
        "substances.csv",
        "product_substances.csv",
        "manual_review_queue.csv",
        "eye_meds_final.json",
        "data_quality_report.md",
        "final_build_summary.md",
    ]
    if snapshot.exists() and manifest.exists():
        return
    entries = []
    with zipfile.ZipFile(snapshot, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for filename in source_files:
            path = FINAL / filename
            if not path.exists():
                continue
            data = path.read_bytes()
            archive.writestr(filename, data)
            entries.append({
                "filename": filename,
                "size_bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            })
    manifest.write_text(json.dumps({
        "created_at": CHECKED_AT,
        "purpose": "Before snapshot for systematic unknown role resolution",
        "snapshot_file": snapshot.name,
        "entries": entries,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_role_dictionary(product_substances):
    dictionary = defaultdict(lambda: {"roles": Counter(), "examples": defaultdict(list)})
    for row in product_substances:
        role = row.get("substance_role", "")
        if role == "unknown" or row.get("confirmed_status") not in {"confirmed", "candidate_needs_review"}:
            continue
        if role not in ROLES:
            continue
        for variant in row_variants(row):
            entry = dictionary[variant]
            entry["roles"][role] += 1
            if len(entry["examples"][role]) < 5:
                entry["examples"][role].append(row)
    return dictionary


def classify_unknown(row, role_dictionary, products_by_license):
    matches = []
    for variant in sorted(row_variants(row)):
        entry = role_dictionary.get(variant)
        if entry:
            matches.append((variant, entry))
    if not matches:
        return None, "no_reliable_match", []

    non_active_matches = [
        (variant, entry) for variant, entry in matches
        if any(role in NON_ACTIVE_ROLES for role in entry["roles"])
    ]
    active_only_matches = [
        (variant, entry) for variant, entry in matches
        if set(entry["roles"]) == {"active"}
    ]
    if non_active_matches:
        return None, "role_conflict_or_non_active_support", matches
    if not active_only_matches:
        return None, "no_active_only_support", matches

    exact_unknown = normalize_material_name(row.get("substance_normalized") or row.get("substance_raw"))
    best_variant, best_entry = max(active_only_matches, key=lambda item: (
        item[1]["roles"]["active"],
        int(item[0] == exact_unknown),
        len(item[0]),
    ))
    support = best_entry["examples"]["active"][0]
    support_license = support.get("license_number", "")
    support_product = products_by_license.get(support_license, {})
    product = products_by_license.get(row.get("license_number", ""), {})
    rule = "A_exact_confirmed_active_only" if best_variant == exact_unknown else "B_salt_or_base_group_active_only"
    if support.get("substance_normalized") == row.get("substance_normalized"):
        rule = "A_exact_confirmed_active_only"
    elif product.get("drug_class") and support_product.get("drug_class") == product.get("drug_class"):
        rule = "C_consistent_active_in_same_class"
    if support.get("substance_raw") and row.get("substance_raw") and support.get("substance_raw").lower() == row.get("substance_raw").lower():
        rule = "D_same_formula_or_raw_component_pattern"
    if row.get("source", "").startswith("TFDA Open Data InfoId=43") and row.get("strength"):
        rule = "E_official_ingredient_with_strength_matches_active_dictionary" if rule.startswith("A_") else rule
    return {
        "new_role": "active",
        "new_confirmed_status": "confirmed",
        "matched_variant": best_variant,
        "matched_standard_substance": support.get("substance_normalized") or support.get("substance_raw") or best_variant,
        "supporting_product": support_license,
        "supporting_product_name": support_product.get("chinese_name", ""),
        "supporting_substance_raw": support.get("substance_raw", ""),
        "rule": rule,
        "confidence": "high",
    }, "resolved", matches


def apply_unknown_role_resolution(product_substances, final_products, existing_substances):
    products_by_license = {row["license_number"]: row for row in final_products}
    role_dictionary = build_role_dictionary(product_substances)
    resolution_rows = []
    resolved_keys = set()
    for row in product_substances:
        if row.get("substance_role") != "unknown":
            continue
        original = dict(row)
        decision, status, matches = classify_unknown(row, role_dictionary, products_by_license)
        match_summary = "; ".join(
            f"{variant}:{dict(entry['roles'])}" for variant, entry in matches[:5]
        )
        resolution_row = {
            "license_number": row.get("license_number", ""),
            "product_id": row.get("product_id", ""),
            "product_substance_id": row.get("product_substance_id", ""),
            "substance_raw": row.get("substance_raw", ""),
            "substance_normalized_before": row.get("substance_normalized", ""),
            "normalized_variants": " | ".join(sorted(row_variants(row))),
            "original_role": "unknown",
            "new_role": "unknown",
            "resolution_status": status,
            "rule": "",
            "matched_standard_substance": "",
            "supporting_product": "",
            "supporting_evidence": match_summary,
            "confidence": "",
            "reason": status,
        }
        if decision:
            row["substance_role"] = decision["new_role"]
            row["confirmed_status"] = decision["new_confirmed_status"]
            row["substance_normalized"] = decision["matched_standard_substance"]
            row["formulation_function"] = "active ingredient"
            resolution_row.update({
                "substance_normalized_after": row["substance_normalized"],
                "new_role": decision["new_role"],
                "resolution_status": "resolved_to_active",
                "rule": decision["rule"],
                "matched_standard_substance": decision["matched_standard_substance"],
                "supporting_product": decision["supporting_product"],
                "supporting_evidence": (
                    f"{decision['supporting_product']} {decision['supporting_product_name']} "
                    f"confirmed active: {decision['supporting_substance_raw']}"
                ),
                "confidence": decision["confidence"],
                "reason": "matched confirmed active dictionary with no non-active role conflict",
            })
            resolved_keys.add((original.get("license_number", ""), normalize_material_name(original.get("substance_raw") or original.get("substance_normalized"))))
        else:
            resolution_row["substance_normalized_after"] = row.get("substance_normalized", "")
        resolution_rows.append(resolution_row)

    substance_lookup = {row["substance_id"]: row for row in existing_substances}
    substance_ids = {}
    substances = []
    for row in product_substances:
        old = substance_lookup.get(row.get("substance_id", ""), {})
        role = row.get("substance_role", "")
        skey = (
            clean(row.get("substance_normalized")).lower(),
            clean(old.get("base_ingredient_name") or row.get("substance_normalized")).lower(),
            clean(old.get("salt_ester_hydrate_form")).lower(),
            role,
        )
        if skey not in substance_ids:
            sid = next_id("sub", len(substance_ids) + 1)
            substance_ids[skey] = sid
            substances.append({
                "substance_id": sid,
                "standard_name": row.get("substance_normalized", "") or old.get("standard_name", ""),
                "chinese_name": old.get("chinese_name", ""),
                "base_ingredient_name": old.get("base_ingredient_name") or row.get("substance_normalized", ""),
                "salt_ester_hydrate_form": old.get("salt_ester_hydrate_form", ""),
                "default_role": role,
            })
        row["substance_id"] = substance_ids[skey]
    return substances, resolution_rows, resolved_keys


def substance_key(row, role):
    return (
        clean(row.get("substance_normalized") or row.get("standard_english_name")).lower(),
        clean(row.get("base_ingredient_name")).lower(),
        clean(row.get("salt_ester_hydrate_form")).lower(),
        role,
    )


def next_id(prefix, seq):
    return f"{prefix}_{seq:04d}"


def main():
    create_before_snapshot()
    core_products = read_csv(CORE / "eye_core_products.csv")
    core_ingredients = read_csv(CORE / "eye_core_ingredients.csv")
    core_product_ingredients = read_csv(CORE / "eye_core_product_ingredients.csv")
    core_indications = read_csv(CORE / "eye_core_indications.csv")
    core_product_indications = read_csv(CORE / "eye_core_product_indications.csv")
    core_classes = read_csv(CORE / "eye_core_classes.csv")
    core_product_classes = read_csv(CORE / "eye_core_product_classes.csv")
    core_unknown = read_csv(CORE / "eye_core_ingredient_review.csv")
    formal_product_substances = read_csv(BASE / "eye_product_substances.csv")
    enrich_products = read_csv(ENRICH / "eye_enrichment_products.csv")
    enrich_substances = read_csv(ENRICH / "eye_enrichment_substances.csv")
    enrich_evidence = read_csv(ENRICH / "eye_enrichment_evidence.csv")
    enrich_reviews = read_csv(ENRICH / "eye_enrichment_review.csv")
    state = json.loads((ENRICH / "eye_enrichment_state.json").read_text(encoding="utf-8"))

    core_by_license = {row["license_number"]: row for row in core_products}
    enrich_by_license = {row["license_number"]: row for row in enrich_products}
    review_by_license = {row["license_number"]: row for row in enrich_reviews}
    evidence_by_license = defaultdict(list)
    for row in enrich_evidence:
        evidence_by_license[row["license_number"]].append(row)

    product_ids = {row["license_number"]: row["product_id"] for row in core_products}

    final_products = []
    source_rows = []
    conflict_rows = []
    for product in core_products:
        license_number = product["license_number"]
        enrich = enrich_by_license.get(license_number, {})
        state_status = state.get("product_status", {}).get(license_number, {})
        core_status = state_status.get("core_processing_status") or enrich.get("core_processing_status") or "core_complete_optional_missing"
        leaflet_available = state_status.get("leaflet_available") or enrich.get("leaflet_available") or "no"
        leaflet_status = "available" if leaflet_available == "yes" else "leaflet_unavailable"
        final_products.append({
            "product_id": product["product_id"],
            "license_number": license_number,
            "license_year": product.get("license_year", ""),
            "chinese_name": product.get("chinese_name", ""),
            "english_name": product.get("english_name", ""),
            "dosage_form_raw": product.get("dosage_form_raw", ""),
            "dosage_form_normalized": product.get("dosage_form_normalized", ""),
            "indication_raw": product.get("indication_raw", ""),
            "drug_class": product.get("therapeutic_class", ""),
            "license_status": product.get("license_status", ""),
            "core_data_status": core_status,
            "leaflet_status": leaflet_status,
            "source_reference": "core + enrichment state",
        })
        source_rows.append({
            "source_id": f"src_{product['product_id']}_core",
            "product_id": product["product_id"],
            "license_number": license_number,
            "source_type": "core_csv",
            "source_name": "Existing core export",
            "source_detail": "data/eye_meds_rebuild_20260711/core/",
            "status": core_status,
            "checked_at": CHECKED_AT,
        })
        source_rows.append({
            "source_id": f"src_{product['product_id']}_enrichment",
            "product_id": product["product_id"],
            "license_number": license_number,
            "source_type": "enrichment_state",
            "source_name": "Existing enrichment state",
            "source_detail": state_status.get("unresolved_reason") or enrich.get("unresolved_reason") or "",
            "status": leaflet_status,
            "checked_at": CHECKED_AT,
        })
        if enrich and clean(enrich.get("chinese_name")) and clean(enrich.get("chinese_name")) != clean(product.get("chinese_name")):
            conflict_rows.append({
                "license_number": license_number,
                "field": "chinese_name",
                "core_value": product.get("chinese_name", ""),
                "enrichment_value": enrich.get("chinese_name", ""),
                "resolution": "core retained for final products",
            })
        if enrich and clean(enrich.get("english_name")) and clean(enrich.get("english_name")) != clean(product.get("english_name")):
            conflict_rows.append({
                "license_number": license_number,
                "field": "english_name",
                "core_value": product.get("english_name", ""),
                "enrichment_value": enrich.get("english_name", ""),
                "resolution": "core retained for final products",
            })

    substance_ids = {}
    substances = []
    product_substances = []

    core_ingredient_by_id = {row["ingredient_id"]: row for row in core_ingredients}
    for row in core_product_ingredients:
        ingredient = core_ingredient_by_id.get(row["ingredient_id"], {})
        skey = (
            clean(ingredient.get("standard_english_name")).lower(),
            clean(ingredient.get("base_ingredient_name")).lower(),
            clean(ingredient.get("salt_ester_hydrate_form")).lower(),
            "active",
        )
        if skey not in substance_ids:
            sid = next_id("sub", len(substance_ids) + 1)
            substance_ids[skey] = sid
            substances.append({
                "substance_id": sid,
                "standard_name": ingredient.get("standard_english_name", ""),
                "chinese_name": ingredient.get("chinese_name", ""),
                "base_ingredient_name": ingredient.get("base_ingredient_name", ""),
                "salt_ester_hydrate_form": ingredient.get("salt_ester_hydrate_form", ""),
                "default_role": "active",
            })
        product_substances.append({
            "product_substance_id": row["product_ingredient_id"],
            "product_id": product_ids[row["license_number"]],
            "license_number": row["license_number"],
            "substance_id": substance_ids[skey],
            "substance_raw": row.get("raw_name", ""),
            "substance_normalized": row.get("standard_english_name", ""),
            "substance_role": "active",
            "strength": row.get("strength", ""),
            "unit": row.get("unit", ""),
            "confirmed_status": "confirmed" if row.get("confirmed") == "yes" else row.get("confirmed", ""),
            "source": row.get("data_source", ""),
            "formulation_function": "",
        })

    for row in formal_product_substances:
        role = row.get("role_in_product", "")
        if role == "active":
            continue
        if role not in ROLES:
            role = "unknown"
        skey = (
            clean(row.get("standard_english_name")).lower(),
            clean(row.get("base_ingredient_name")).lower(),
            clean(row.get("salt_ester_hydrate_form")).lower(),
            role,
        )
        if skey not in substance_ids:
            sid = next_id("sub", len(substance_ids) + 1)
            substance_ids[skey] = sid
            substances.append({
                "substance_id": sid,
                "standard_name": row.get("standard_english_name", ""),
                "chinese_name": row.get("chinese_name", ""),
                "base_ingredient_name": row.get("base_ingredient_name", ""),
                "salt_ester_hydrate_form": row.get("salt_ester_hydrate_form", ""),
                "default_role": role,
            })
        product_substances.append({
            "product_substance_id": row.get("product_substance_id", ""),
            "product_id": product_ids.get(row["license_number"], ""),
            "license_number": row["license_number"],
            "substance_id": substance_ids[skey],
            "substance_raw": row.get("raw_name", ""),
            "substance_normalized": row.get("standard_english_name", ""),
            "substance_role": role,
            "strength": row.get("strength", ""),
            "unit": row.get("unit", ""),
            "confirmed_status": "role_unknown_needs_review" if role == "unknown" else ("confirmed" if row.get("confirmed") == "yes" else row.get("confirmed", "")),
            "source": row.get("data_source", ""),
            "formulation_function": row.get("formulation_function", ""),
        })

    for row in enrich_substances:
        role = row.get("substance_role", "")
        if role == "active":
            continue
        if role not in ROLES:
            role = "unknown"
        skey = substance_key(row, role)
        if skey not in substance_ids:
            sid = next_id("sub", len(substance_ids) + 1)
            substance_ids[skey] = sid
            substances.append({
                "substance_id": sid,
                "standard_name": row.get("substance_normalized", ""),
                "chinese_name": "",
                "base_ingredient_name": row.get("substance_normalized", ""),
                "salt_ester_hydrate_form": "",
                "default_role": role,
            })
        confirmed_status = row.get("confirmed", "")
        if "candidate" in confirmed_status.lower() or row.get("value_status", ""):
            confirmed_status = "candidate_needs_review"
        product_substances.append({
            "product_substance_id": row.get("enrichment_substance_id", ""),
            "product_id": product_ids.get(row["license_number"], ""),
            "license_number": row["license_number"],
            "substance_id": substance_ids[skey],
            "substance_raw": row.get("substance_raw", ""),
            "substance_normalized": row.get("substance_normalized", ""),
            "substance_role": role,
            "strength": row.get("strength", ""),
            "unit": row.get("unit", ""),
            "confirmed_status": confirmed_status,
            "source": row.get("data_source", "TFDA official leaflet PDF OCR evidence"),
            "formulation_function": row.get("formulation_function", ""),
        })

    substances, resolution_rows, resolved_unknown_keys = apply_unknown_role_resolution(
        product_substances,
        final_products,
        substances,
    )

    manual_review = []
    for row in core_unknown:
        review_key = (row.get("license_number", ""), normalize_material_name(row.get("raw_name") or row.get("standard_english_name")))
        if review_key in resolved_unknown_keys:
            continue
        manual_review.append({
            "review_id": f"review_unknown_{len(manual_review) + 1:04d}",
            "license_number": row.get("license_number", ""),
            "product_id": product_ids.get(row.get("license_number", ""), ""),
            "issue_type": "unknown_substance_role",
            "raw_value": row.get("raw_name", ""),
            "standard_value": row.get("standard_english_name", ""),
            "source": "core eye_core_ingredient_review.csv",
            "reason": row.get("review_reason", ""),
        })
    for row in enrich_reviews:
        reason = row.get("failure_reason", "")
        if reason:
            manual_review.append({
                "review_id": f"review_leaflet_{len(manual_review) + 1:04d}",
                "license_number": row.get("license_number", ""),
                "product_id": product_ids.get(row.get("license_number", ""), ""),
                "issue_type": "leaflet_or_optional_data_unavailable",
                "raw_value": reason,
                "standard_value": "",
                "source": "enrichment review",
                "reason": reason,
            })
    for row in conflict_rows:
        manual_review.append({
            "review_id": f"review_conflict_{len(manual_review) + 1:04d}",
            "license_number": row["license_number"],
            "product_id": product_ids.get(row["license_number"], ""),
            "issue_type": "core_enrichment_conflict",
            "raw_value": f"{row['field']}: core={row['core_value']} | enrichment={row['enrichment_value']}",
            "standard_value": row["resolution"],
            "source": "core/enrichment comparison",
            "reason": "value conflict recorded; final retained core product value",
        })

    indications = [{
        "indication_id": row["indication_id"],
        "indication_category": row["indication_category"],
        "definition_note": row.get("definition_note", ""),
    } for row in core_indications]
    product_indications = [{
        "product_id": product_ids[row["license_number"]],
        "license_number": row["license_number"],
        "indication_id": row["indication_id"],
        "indication_category": row["indication_category"],
        "mapping_basis": row.get("mapping_basis", ""),
        "needs_manual_confirmation": row.get("needs_manual_confirmation", ""),
    } for row in core_product_indications]

    class_by_id = {row["class_id"]: row for row in core_classes}
    product_classes = []
    for row in core_product_classes:
        product_classes.append({
            "product_id": product_ids[row["license_number"]],
            "license_number": row["license_number"],
            "class_id": row["class_id"],
            "class_name": row["class_name"],
        })

    # Sources already created above; add evidence-level references without long OCR text.
    for row in enrich_evidence:
        source_rows.append({
            "source_id": f"src_evidence_{len(source_rows) + 1:05d}",
            "product_id": product_ids.get(row["license_number"], ""),
            "license_number": row["license_number"],
            "source_type": "enrichment_evidence",
            "source_name": row.get("extraction_method", ""),
            "source_detail": f"{row.get('document_filename','')} page {row.get('page_number','')}",
            "status": row.get("confidence", ""),
            "checked_at": row.get("checked_at", ""),
        })

    write_csv(FINAL / "products.csv", final_products, [
        "product_id",
        "license_number",
        "license_year",
        "chinese_name",
        "english_name",
        "dosage_form_raw",
        "dosage_form_normalized",
        "indication_raw",
        "drug_class",
        "license_status",
        "core_data_status",
        "leaflet_status",
        "source_reference",
    ])
    write_csv(FINAL / "substances.csv", substances, [
        "substance_id",
        "standard_name",
        "chinese_name",
        "base_ingredient_name",
        "salt_ester_hydrate_form",
        "default_role",
    ])
    write_csv(FINAL / "product_substances.csv", product_substances, [
        "product_substance_id",
        "product_id",
        "license_number",
        "substance_id",
        "substance_raw",
        "substance_normalized",
        "substance_role",
        "strength",
        "unit",
        "confirmed_status",
        "source",
        "formulation_function",
    ])
    write_csv(FINAL / "indications.csv", indications, [
        "indication_id",
        "indication_category",
        "definition_note",
    ])
    write_csv(FINAL / "product_indications.csv", product_indications, [
        "product_id",
        "license_number",
        "indication_id",
        "indication_category",
        "mapping_basis",
        "needs_manual_confirmation",
    ])
    write_csv(FINAL / "sources.csv", source_rows, [
        "source_id",
        "product_id",
        "license_number",
        "source_type",
        "source_name",
        "source_detail",
        "status",
        "checked_at",
    ])
    write_csv(FINAL / "manual_review_queue.csv", manual_review, [
        "review_id",
        "license_number",
        "product_id",
        "issue_type",
        "raw_value",
        "standard_value",
        "source",
        "reason",
    ])
    write_csv(FINAL / "product_classes.csv", product_classes, [
        "product_id",
        "license_number",
        "class_id",
        "class_name",
    ])
    write_csv(FINAL / "classes.csv", core_classes, [
        "class_id",
        "class_name",
        "source_field",
    ])
    write_csv(FINAL / "unknown_role_resolution.csv", resolution_rows, [
        "license_number",
        "product_id",
        "product_substance_id",
        "substance_raw",
        "substance_normalized_before",
        "substance_normalized_after",
        "normalized_variants",
        "original_role",
        "new_role",
        "resolution_status",
        "rule",
        "matched_standard_substance",
        "supporting_product",
        "supporting_evidence",
        "confidence",
        "reason",
    ])
    normalization_rules = [
        {"rule_id": "normalize_case_space_punctuation", "description": "NFKC normalize, lower-case, collapse spaces, remove punctuation for dictionary matching."},
        {"rule_id": "normalize_eq_to_parentheses", "description": "Treat EQ TO, equivalent to/as and parenthetical salt/base descriptions as non-distinguishing matching text."},
        {"rule_id": "normalize_hcl_hydrochloride", "description": "Map hydrochloride and hydrogen chloride to hcl, then compare both salt and salt-stripped variants."},
        {"rule_id": "normalize_salt_hydrate_phosphate_forms", "description": "Generate salt/base variants by removing known salt, hydrate, ester and phosphate tokens only for matching against an existing confirmed active dictionary."},
        {"rule_id": "normalize_vitamin_synonyms", "description": "Generate vitamin A and cyanocobalamin/Vit B12 variants when both names are present in existing official ingredient strings."},
        {"rule_id": "role_conflict_guard", "description": "Do not auto-upgrade when any matched variant has confirmed preservative, vehicle, buffer, viscosity, chelator, surfactant, antioxidant, pH adjuster, ointment base, or other excipient evidence."},
    ]
    write_csv(FINAL / "normalization_rules.csv", normalization_rules, [
        "rule_id",
        "description",
    ])

    products_json = []
    ingredients_by_product = defaultdict(list)
    indications_by_product = defaultdict(list)
    classes_by_product = defaultdict(list)
    sources_by_product = defaultdict(list)
    for row in product_substances:
        ingredients_by_product[row["product_id"]].append(row)
    for row in product_indications:
        indications_by_product[row["product_id"]].append(row)
    for row in product_classes:
        classes_by_product[row["product_id"]].append(row)
    for row in source_rows:
        sources_by_product[row["product_id"]].append(row)
    for product in final_products:
        pid = product["product_id"]
        products_json.append({
            **product,
            "substances": ingredients_by_product.get(pid, []),
            "indications": indications_by_product.get(pid, []),
            "classes": classes_by_product.get(pid, []),
            "sources": sources_by_product.get(pid, []),
        })
    (FINAL / "eye_meds_final.json").write_text(
        json.dumps({
            "built_at": CHECKED_AT,
            "product_count": len(final_products),
            "products": products_json,
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    product_license_counts = Counter(row["license_number"] for row in final_products)
    duplicate_licenses = [lic for lic, count in product_license_counts.items() if count > 1]
    empty_licenses = [row["product_id"] for row in final_products if not clean(row["license_number"])]
    product_ids = {row["product_id"] for row in final_products}
    products_with_rel_substances = {row["product_id"] for row in product_substances}
    products_with_indications = {row["product_id"] for row in product_indications}
    products_with_sources = {row["product_id"] for row in source_rows}
    active_products = {row["product_id"] for row in product_substances if row["substance_role"] == "active" and row["confirmed_status"] == "confirmed"}
    unknown_products = {row["product_id"] for row in product_substances if row["substance_role"] == "unknown"}
    no_substance_products = product_ids - products_with_rel_substances
    only_unknown_products = unknown_products - {row["product_id"] for row in product_substances if row["substance_role"] != "unknown"}
    resolved_ps_ids = {
        row["product_substance_id"] for row in resolution_rows
        if row.get("resolution_status") == "resolved_to_active"
    }
    before_roles_by_product = defaultdict(list)
    for row in product_substances:
        before_role = "unknown" if row.get("product_substance_id") in resolved_ps_ids else row.get("substance_role", "")
        before_status = "role_unknown_needs_review" if before_role == "unknown" else row.get("confirmed_status", "")
        before_roles_by_product[row["product_id"]].append((before_role, before_status))
    active_products_before = {
        pid for pid, rows in before_roles_by_product.items()
        if any(role == "active" and status == "confirmed" for role, status in rows)
    }
    only_unknown_products_before = {
        pid for pid, rows in before_roles_by_product.items()
        if rows and all(role == "unknown" for role, status in rows)
    }
    resolved_unknown_count = len(resolved_ps_ids)
    unresolved_unknown_count = sum(1 for row in resolution_rows if row.get("resolution_status") != "resolved_to_active")
    role_conflict_unresolved_count = sum(1 for row in resolution_rows if row.get("resolution_status") == "role_conflict_or_non_active_support")
    resolution_rule_counts = Counter(row.get("rule", "") for row in resolution_rows if row.get("rule"))
    indication_complete = sum(1 for row in final_products if clean(row["indication_raw"]))
    dosage_complete = sum(1 for row in final_products if clean(row["dosage_form_normalized"]))
    class_complete = sum(1 for row in final_products if clean(row["drug_class"]))
    year_complete = sum(1 for row in final_products if clean(row["license_year"]))
    role_counts = Counter(row["substance_role"] for row in product_substances)
    leaflet_counts = Counter(row["leaflet_status"] for row in final_products)
    quality = {
        "product_count": len(final_products),
        "json_product_count": len(products_json),
        "duplicate_license_count": len(duplicate_licenses),
        "empty_license_count": len(empty_licenses),
        "missing_substance_relation_products": len(product_ids - products_with_rel_substances),
        "missing_indication_relation_products": len(product_ids - products_with_indications),
        "missing_source_relation_products": len(product_ids - products_with_sources),
        "confirmed_active_product_count": len(active_products),
        "confirmed_active_product_count_before_unknown_resolution": len(active_products_before),
        "missing_confirmed_active_product_count": len(final_products) - len(active_products),
        "missing_confirmed_active_product_count_before_unknown_resolution": len(final_products) - len(active_products_before),
        "resolved_unknown_role_count": resolved_unknown_count,
        "unresolved_unknown_role_count": unresolved_unknown_count,
        "role_conflict_unresolved_count": role_conflict_unresolved_count,
        "only_unknown_ingredient_product_count": len(only_unknown_products),
        "only_unknown_ingredient_product_count_before_unknown_resolution": len(only_unknown_products_before),
        "no_ingredient_relation_product_count": len(no_substance_products),
        "indication_raw_complete": f"{indication_complete}/{len(final_products)}",
        "dosage_complete": f"{dosage_complete}/{len(final_products)}",
        "class_complete": f"{class_complete}/{len(final_products)}",
        "license_year_complete": f"{year_complete}/{len(final_products)}",
        "conflict_count": len(conflict_rows),
        "manual_review_count": len(manual_review),
        "role_counts": dict(role_counts),
        "unknown_resolution_rule_counts": dict(resolution_rule_counts),
        "leaflet_status_counts": dict(leaflet_counts),
    }
    report = [
        "# Eye Meds Final Data Quality Report",
        "",
        f"- built_at: {CHECKED_AT}",
        f"- products: {quality['product_count']}",
        f"- JSON products: {quality['json_product_count']}",
        f"- duplicate licenses: {quality['duplicate_license_count']}",
        f"- empty licenses: {quality['empty_license_count']}",
        f"- products missing substance relation: {quality['missing_substance_relation_products']}",
        f"- products missing indication relation: {quality['missing_indication_relation_products']}",
        f"- products missing source relation: {quality['missing_source_relation_products']}",
        f"- confirmed active ingredient products: {quality['confirmed_active_product_count']}",
        f"- confirmed active ingredient products before unknown resolution: {quality['confirmed_active_product_count_before_unknown_resolution']}",
        f"- missing confirmed active products: {quality['missing_confirmed_active_product_count']}",
        f"- missing confirmed active products before unknown resolution: {quality['missing_confirmed_active_product_count_before_unknown_resolution']}",
        f"- unknown role relations resolved: {quality['resolved_unknown_role_count']}",
        f"- unknown role relations remaining: {quality['unresolved_unknown_role_count']}",
        f"- unresolved due to role conflict/non-active support: {quality['role_conflict_unresolved_count']}",
        f"- only unknown ingredient products: {quality['only_unknown_ingredient_product_count']}",
        f"- only unknown ingredient products before unknown resolution: {quality['only_unknown_ingredient_product_count_before_unknown_resolution']}",
        f"- no ingredient relation products: {quality['no_ingredient_relation_product_count']}",
        f"- indication raw completeness: {quality['indication_raw_complete']}",
        f"- dosage completeness: {quality['dosage_complete']}",
        f"- class completeness: {quality['class_complete']}",
        f"- license year completeness: {quality['license_year_complete']}",
        f"- conflict count: {quality['conflict_count']}",
        f"- manual review count: {quality['manual_review_count']}",
        f"- substance role counts: {quality['role_counts']}",
        f"- unknown resolution rule counts: {quality['unknown_resolution_rule_counts']}",
        f"- leaflet status counts: {quality['leaflet_status_counts']}",
        "",
        "## Conflict Handling",
        "- Core product identity fields were retained unless enrichment had stronger confirmed evidence. No confirmed enrichment product-identity replacement was applied.",
        "- OCR candidate values were not upgraded to confirmed.",
        "- Unknown substance roles remain in the manual review queue unless the systematic confirmed-role dictionary resolved them with high confidence.",
    ]
    (FINAL / "data_quality_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")

    summary_rows = Counter(row["resolution_status"] for row in resolution_rows)
    rule_lines = [
        f"- {rule}: {count}" for rule, count in sorted(resolution_rule_counts.items())
    ] or ["- none"]
    conflict_examples = [
        row for row in resolution_rows
        if row["resolution_status"] == "role_conflict_or_non_active_support"
    ][:10]
    resolution_summary = [
        "# Unknown Role Resolution Summary",
        "",
        f"- built_at: {CHECKED_AT}",
        f"- unknown relations reviewed: {len(resolution_rows)}",
        f"- automatically resolved to active: {resolved_unknown_count}",
        f"- remaining unknown: {unresolved_unknown_count}",
        f"- role conflict/non-active support retained as unknown: {role_conflict_unresolved_count}",
        f"- confirmed active products before: {len(active_products_before)}",
        f"- confirmed active products after: {len(active_products)}",
        f"- missing confirmed active products before: {len(final_products) - len(active_products_before)}",
        f"- missing confirmed active products after: {len(final_products) - len(active_products)}",
        f"- only unknown ingredient products before: {len(only_unknown_products_before)}",
        f"- only unknown ingredient products after: {len(only_unknown_products)}",
        "",
        "## Resolution Status Counts",
        *[f"- {status}: {count}" for status, count in sorted(summary_rows.items())],
        "",
        "## Rules Used",
        *rule_lines,
        "",
        "## Conflict Guard Examples",
        *[
            f"- {row['license_number']} {row['substance_raw']}: {row['supporting_evidence']}"
            for row in conflict_examples
        ],
    ]
    (FINAL / "unknown_role_resolution_summary.md").write_text("\n".join(resolution_summary) + "\n", encoding="utf-8")

    summary = [
        "# Eye Meds Final Build Summary",
        "",
        f"- built_at: {CHECKED_AT}",
        f"- source_core_folder: {CORE}",
        f"- source_enrichment_folder: {ENRICH}",
        f"- output_folder: {FINAL}",
        f"- products: {len(final_products)}",
        f"- substances: {len(substances)}",
        f"- product_substances: {len(product_substances)}",
        f"- indications: {len(indications)}",
        f"- product_indications: {len(product_indications)}",
        f"- sources: {len(source_rows)}",
        f"- manual_review_queue: {len(manual_review)}",
        "",
        "## Outputs",
        "- products.csv",
        "- substances.csv",
        "- product_substances.csv",
        "- indications.csv",
        "- product_indications.csv",
        "- sources.csv",
        "- manual_review_queue.csv",
        "- eye_meds_final.json",
        "- data_quality_report.md",
        "- final_build_summary.md",
        "- unknown_role_resolution.csv",
        "- unknown_role_resolution_summary.md",
        "- normalization_rules.csv",
    ]
    (FINAL / "final_build_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(json.dumps(quality, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
