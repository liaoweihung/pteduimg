"""Phase 2: rule-based manual-review resolution and concentration parsing.

Only phase-1 CSVs and the existing local TFDA InfoId 37/43 caches are read.
No website files, leaflet downloads, OCR, or broad candidate discovery occur.
The script is idempotent: rerunning it updates records by licence number.
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from zoneinfo import ZoneInfo

from concentration_parser import parse_concentration


B = Path(__file__).resolve().parent
CACHE = B.parent / "eye_meds_rebuild_20260711"
SOURCE37 = "tfda_open_data_info37_cached_20260711"
SOURCE43 = "tfda_open_data_info43_cached_20260711"
NOW = dt.datetime.now(ZoneInfo("Asia/Taipei")).replace(microsecond=0).isoformat()

K = {
    "lic": "許可證字號",
    "kind": "許可證種類",
    "cancel": "註銷狀態",
    "expiry": "有效日期",
    "issued": "發證日期",
    "cn": "中文品名",
    "en": "英文品名",
    "form": "劑型",
    "active": "主成分略述",
    "applicant": "申請商名稱",
    "maker": "製造商名稱",
    "use": "用法用量",
    "ind": "適應症",
}
K43 = {
    "lic": "許可證字號",
    "label": "處方標示",
    "name": "成分名稱",
    "code": "成分代碼",
    "desc": "含量描述",
    "value": "含量",
    "unit": "含量單位",
}

PRODUCT_FIELDS = "product_id license_number license_year chinese_name english_name dosage_form_raw dosage_form_normalized dosage_form_group preparation_type route_raw route_normalized oral_liquid_inclusion_evidence indication_raw indication_normalized therapeutic_class legal_category license_status license_expiry_date applicant manufacturer source_id verified_at".split()
SUBSTANCE_FIELDS = "substance_id raw_name normalized_name base_substance_group source_id".split()
PRODUCT_SUBSTANCE_FIELDS = "product_id substance_id raw_name normalized_name base_substance_group strength_raw numerator_value numerator_unit denominator_value denominator_unit display_concentration normalized_value_per_ml concentration_normalized normalization_status concentration_status parsing_rule confidence role confirmation_status source_id".split()
EXCLUDED_FIELDS = "license_number chinese_name english_name dosage_form_raw route_raw candidate_reason exclusion_reason source_id verified_at".split()
REVIEW_FIELDS = "review_id license_number chinese_name english_name dosage_form_raw route_raw review_type reason recommended_action source_id verified_at".split()
CONCENTRATION_REVIEW_FIELDS = "product_id license_number chinese_name substance_id raw_name strength_raw normalization_status parsing_rule confidence reason source_id".split()

RULES = [
    {
        "rule_id": "MR-A01",
        "priority": 10,
        "decision": "auto_include",
        "description": "TFDA dosage form explicitly says an oral liquid form.",
        "required_evidence": "Explicit oral/enteral wording in dosage_form_raw.",
        "confidence": "high",
    },
    {
        "rule_id": "MR-A02",
        "priority": 20,
        "decision": "auto_include",
        "description": "Generic liquid dosage form plus explicit oral wording in official name or use.",
        "required_evidence": "Compatible liquid form and oral/enteral/swallow/use wording.",
        "confidence": "high",
    },
    {
        "rule_id": "MR-A03",
        "priority": 30,
        "decision": "auto_include",
        "description": "Reconstitution form plus explicit evidence that the resulting liquid is oral.",
        "required_evidence": "Suspension/solution powder or granules and oral wording in official name/use.",
        "confidence": "high",
    },
    {
        "rule_id": "MR-B01",
        "priority": 1,
        "decision": "auto_exclude",
        "description": "TFDA dosage form explicitly identifies a non-oral preparation.",
        "required_evidence": "Eye, ear, nose, inhalation, injection, cavity, dental, gas, topical, or enema dosage form.",
        "confidence": "high",
    },
    {
        "rule_id": "MR-B02",
        "priority": 2,
        "decision": "auto_exclude",
        "description": "Official licence status is inactive or cancelled.",
        "required_evidence": "Non-empty TFDA cancellation status.",
        "confidence": "high",
    },
    {
        "rule_id": "MR-C01",
        "priority": 90,
        "decision": "unresolved",
        "description": "Only product name or indication suggests a liquid; route/form evidence is insufficient.",
        "required_evidence": "No explicit official oral route or oral dosage-form wording.",
        "confidence": "low",
    },
    {
        "rule_id": "MR-C02",
        "priority": 91,
        "decision": "unresolved",
        "description": "Formal website-core fields or confirmed active ingredient are incomplete.",
        "required_evidence": "Missing active, indication, issue date, or official source row.",
        "confidence": "low",
    },
]

NONORAL_FORM_TERMS = (
    "點眼",
    "眼用",
    "眼耳鼻",
    "點耳",
    "點鼻",
    "鼻用",
    "靜脈",
    "注射",
    "體腔",
    "牙科",
    "氣體",
    "吸入",
    "噴霧",
    "外用",
    "灌腸",
    "浣腸",
)
GENERIC_LIQUID_FORMS = ("懸液劑", "懸浮液", "溶液劑", "液劑", "滴劑", "乳劑", "內服懸液劑")
RECON_FORMS = ("懸液用粉劑", "懸液用顆粒劑", "懸浮液用顆粒劑", "溶液用粉劑")
ORAL_NAME_TERMS = ("口服", "內服", "oral solution", "oral suspension", "oral drops", "oral liquid", "for oral")
ORAL_USE_TERMS = ("口服", "內服", "吞服", "服用")


def clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def has(text: str, terms) -> bool:
    lowered = clean(text).lower()
    return any(term.lower() in lowered for term in terms)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", clean(text).lower()).strip("_") or "unknown"


def chemical_key(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", clean(text).upper())


def read_csv(name: str) -> list[dict[str, str]]:
    with (B / name).open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(name: str, rows, fields) -> None:
    with (B / name).open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def read_zip_json(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as archive:
        return json.loads(archive.read(archive.namelist()[0]).decode("utf-8-sig"))


def original_reviews() -> list[dict[str, str]]:
    resolution = B / "manual_review_resolution.csv"
    if not resolution.exists():
        return read_csv("manual_review_queue.csv")
    rows = read_csv("manual_review_resolution.csv")
    return [{field: row.get(field, "") for field in REVIEW_FIELDS} for row in rows]


def use_text_type(text: str) -> str:
    value = clean(text)
    if not value:
        return "blank"
    if value in {"請詳見仿單", "詳如仿單", "詳見仿單"}:
        return "leaflet_reference_only"
    if has(value, ORAL_USE_TERMS):
        return "explicit_oral_use"
    if has(value, ("mL", "ml", "毫升", "公撮", "cc")):
        return "volume_dosing_without_route_word"
    return "other_official_text"


def name_features(row: dict[str, str]) -> str:
    text = f"{row.get('chinese_name', '')} {row.get('english_name', '')}"
    features = []
    if has(text, ORAL_NAME_TERMS):
        features.append("explicit_oral_liquid_name")
    if has(text, ("液", "水", "糖漿", "liquid", "solution", "suspension", "drops")):
        features.append("generic_liquid_name")
    return ";".join(features) or "none"


def normalized_form(form: str) -> tuple[str, str]:
    if "懸浮液用顆粒" in form or "懸液用顆粒" in form:
        return "granules_for_oral_suspension", "requires_reconstitution"
    if "懸液用粉" in form:
        return "powder_for_oral_suspension", "requires_reconstitution"
    if "溶液用粉" in form:
        return "powder_for_oral_solution", "requires_reconstitution"
    if "懸" in form:
        return "oral_suspension", "ready_to_use"
    if "滴" in form:
        return "oral_drops", "ready_to_use"
    if "乳" in form:
        return "oral_emulsion", "ready_to_use"
    return "oral_solution", "ready_to_use"


def classes(active: str, indication: str) -> list[str]:
    text = f"{active} {indication}".lower()
    rules = {
        "antibiotic": ("amoxic", "cefaclor", "cephalex", "azithro", "clarithro", "erythro", "penicillin", "抗生素"),
        "antiviral": ("acyclovir", "oseltamivir"),
        "antifungal": ("nystatin", "fluconazole", "itraconazole"),
        "antipyretic_analgesic": ("acetaminophen", "paracetamol", "ibuprofen", "對乙醯氨基酚"),
        "antihistamine": ("cetirizine", "loratadine", "chlorphen", "diphenhydramine"),
        "cough": ("dextromethorphan", "codeine", "noscapine"),
        "expectorant_mucolytic": ("ambroxol", "bromhexine", "acetylcysteine", "carbocisteine", "guaifenesin"),
        "bronchodilator": ("salbutamol", "theophylline", "terbutaline"),
        "laxative": ("lactulose", "magnesium hydroxide", "sennoside", "bisacodyl"),
        "antidiarrheal": ("loperamide", "diosmectite"),
        "antiemetic": ("domperidone", "metoclopramide", "ondansetron"),
        "acid_suppression": ("famotidine", "omeprazole", "aluminum hydroxide", "magnesium hydroxide"),
        "vitamin_or_mineral_drug": ("vitamin", "維生素", "iron", "ferr", "calcium", "zinc"),
        "corticosteroid": ("prednisolone", "dexamethasone", "betamethasone"),
        "neurologic": ("levetiracetam", "valpro", "gabapentin", "carbamazepine"),
        "cardiovascular": ("digoxin", "propranolol", "amlodipine"),
    }
    out = [label for label, terms in rules.items() if has(text, terms)]
    if has(text, ("胃", "腸", "antacid", "simethicone", "digest")):
        out.append("gastrointestinal")
    return list(dict.fromkeys(out)) or ["other"]


def resolve_candidate(review: dict[str, str], official: dict | None) -> dict[str, str]:
    form = review["dosage_form_raw"]
    names = f"{review['chinese_name']} {review['english_name']}"
    use = review["route_raw"]
    group, preparation = normalized_form(form)
    evidence = f"TFDA dosage form={form}; approved use={use}; names={names}."

    if official and clean(official.get(K["cancel"])):
        decision, rule = "auto_exclude", "MR-B02"
    elif has(form, NONORAL_FORM_TERMS):
        decision, rule = "auto_exclude", "MR-B01"
    elif not official or not all(
        clean(official.get(K[field])) for field in ("active", "ind", "issued")
    ):
        decision, rule = "unresolved", "MR-C02"
    elif form == "內服懸液劑":
        decision, rule = "auto_include", "MR-A01"
    elif has(form, RECON_FORMS) and (has(names, ORAL_NAME_TERMS) or has(use, ORAL_USE_TERMS)):
        decision, rule = "auto_include", "MR-A03"
    elif has(form, GENERIC_LIQUID_FORMS) and (has(names, ORAL_NAME_TERMS) or has(use, ORAL_USE_TERMS)):
        decision, rule = "auto_include", "MR-A02"
    else:
        decision, rule = "unresolved", "MR-C01"

    rule_row = next(item for item in RULES if item["rule_id"] == rule)
    return {
        **review,
        "review_reason": review.get("reason", ""),
        "use_text_type": use_text_type(use),
        "name_features": name_features(review),
        "derived_preparation_type": preparation,
        "decision": decision,
        "dosage_form_group": group if decision == "auto_include" else "",
        "preparation_type": preparation if decision == "auto_include" else "",
        "resolution_rule_id": rule,
        "confidence": rule_row["confidence"],
        "official_evidence": evidence,
        "resolved_at": NOW,
    }


def excipient_role(name: str) -> str:
    text = clean(name).upper()
    mapping = [
        ("preservative", ("METHYLPARABEN", "PROPYLPARABEN", "BENZOATE", "BENZOIC ACID", "SORBATE")),
        ("sweetener", ("SACCHARIN", "SUCROSE", "SORBITOL", "ASPARTAME", "FRUCTOSE", "GLUCOSE")),
        ("flavor", ("FLAVOR", "FLAVOUR", "ESSENCE")),
        ("colorant", ("COLOR", "COLOUR", "DYE", "TARTRAZINE")),
        ("vehicle", ("PURIFIED WATER", "WATER FOR", "GLYCERIN", "PROPYLENE GLYCOL")),
        ("buffer", ("CITRATE", "PHOSPHATE BUFFER", "BUFFER")),
        ("viscosity_agent", ("CELLULOSE", "XANTHAN", "CARBOXYMETHYL")),
    ]
    for role, terms in mapping:
        if any(term in text for term in terms):
            return role
    return ""


def main() -> None:
    reviews = original_reviews()
    products = read_csv("products.csv")
    excluded = read_csv("excluded_records.csv")
    archived = read_csv("archived_or_inactive_products.csv")
    product_indications = read_csv("product_indications.csv")
    indications = read_csv("indications.csv")
    product_classes = read_csv("product_classes.csv")
    sources = read_csv("sources.csv")
    state = json.loads((B / "processing_state.json").read_text(encoding="utf-8"))

    baseline_formal = state.get("phase_2", {}).get("before_formal_total", len(products))
    baseline_manual = state.get("phase_2", {}).get("before_manual_review_total", len(reviews))
    target_licences = {row["license_number"] for row in products} | {row["license_number"] for row in reviews}

    # The caches are read once and immediately restricted to the existing
    # phase-1 product/review licence set.  No new candidate discovery occurs.
    official37 = {}
    for row in read_zip_json(CACHE / "tfda_info37.zip"):
        licence = clean(row.get(K["lic"]))
        if licence not in target_licences:
            continue
        if licence not in official37 or clean(row.get("異動日期")) > clean(official37[licence].get("異動日期")):
            official37[licence] = row

    resolutions = [resolve_candidate(row, official37.get(row["license_number"])) for row in reviews]
    include_resolutions = [row for row in resolutions if row["decision"] == "auto_include"]
    exclude_resolutions = [row for row in resolutions if row["decision"] == "auto_exclude"]
    unresolved_resolutions = [row for row in resolutions if row["decision"] == "unresolved"]

    existing_by_licence = {row["license_number"]: row for row in products}
    next_id = max((int(match.group(1)) for row in products if (match := re.search(r"(\d+)$", row["product_id"]))), default=0) + 1
    new_product_ids = {}
    for resolution in sorted(include_resolutions, key=lambda row: row["license_number"]):
        licence = resolution["license_number"]
        if licence in existing_by_licence:
            new_product_ids[licence] = existing_by_licence[licence]["product_id"]
            continue
        official = official37[licence]
        active = clean(official.get(K["active"]))
        indication = clean(official.get(K["ind"]))
        issued = clean(official.get(K["issued"]))
        product_id = f"oral_liquid_{next_id:05d}"
        next_id += 1
        class_labels = classes(active, indication)
        row = {
            "product_id": product_id,
            "license_number": licence,
            "license_year": issued.split("/", 1)[0],
            "chinese_name": clean(official.get(K["cn"])),
            "english_name": clean(official.get(K["en"])),
            "dosage_form_raw": clean(official.get(K["form"])),
            "dosage_form_normalized": resolution["dosage_form_group"],
            "dosage_form_group": resolution["dosage_form_group"],
            "preparation_type": resolution["preparation_type"],
            "route_raw": clean(official.get(K["use"])),
            "route_normalized": "oral",
            "oral_liquid_inclusion_evidence": f"{resolution['resolution_rule_id']}: {resolution['official_evidence']}",
            "indication_raw": indication,
            "indication_normalized": indication.lower(),
            "therapeutic_class": "; ".join(class_labels),
            "legal_category": clean(official.get(K["kind"])),
            "license_status": "active",
            "license_expiry_date": clean(official.get(K["expiry"])),
            "applicant": clean(official.get(K["applicant"])),
            "manufacturer": clean(official.get(K["maker"])),
            "source_id": SOURCE37,
            "verified_at": NOW,
        }
        products.append(row)
        existing_by_licence[licence] = row
        new_product_ids[licence] = product_id

        indication_id = "ind_" + slug(indication)
        if indication_id not in {item["indication_id"] for item in indications}:
            indications.append(
                {
                    "indication_id": indication_id,
                    "indication_raw": indication,
                    "indication_normalized": indication.lower(),
                    "source_id": SOURCE37,
                }
            )
        product_indications.append({"product_id": product_id, "indication_id": indication_id, "source_id": SOURCE37})
        for label in class_labels:
            product_classes.append(
                {
                    "product_id": product_id,
                    "class_id": label,
                    "classification_evidence": f"Multi-signal rule uses TFDA active summary ({active}); indication corroborates only.",
                    "source_id": SOURCE37,
                }
            )

    excluded_licences = {row["license_number"] for row in excluded}
    archived_licences = {row["license_number"] for row in archived}
    for resolution in exclude_resolutions:
        licence = resolution["license_number"]
        official = official37.get(licence, {})
        if resolution["resolution_rule_id"] == "MR-B02":
            if licence not in archived_licences:
                archived.append(
                    {
                        "product_id": "",
                        "license_number": licence,
                        "license_year": clean(official.get(K["issued"])).split("/", 1)[0],
                        "chinese_name": resolution["chinese_name"],
                        "english_name": resolution["english_name"],
                        "dosage_form_raw": resolution["dosage_form_raw"],
                        "route_raw": resolution["route_raw"],
                        "license_status": "inactive_or_cancelled",
                        "source_id": SOURCE37,
                        "verified_at": NOW,
                    }
                )
                archived_licences.add(licence)
        elif licence not in excluded_licences:
            excluded.append(
                {
                    "license_number": licence,
                    "chinese_name": resolution["chinese_name"],
                    "english_name": resolution["english_name"],
                    "dosage_form_raw": resolution["dosage_form_raw"],
                    "route_raw": resolution["route_raw"],
                    "candidate_reason": "phase1_manual_review_candidate",
                    "exclusion_reason": f"{resolution['resolution_rule_id']}: {resolution['official_evidence']}",
                    "source_id": SOURCE37,
                    "verified_at": NOW,
                }
            )
            excluded_licences.add(licence)

    products.sort(key=lambda row: row["product_id"])
    formal_licences = {row["license_number"] for row in products}
    product_by_licence = {row["license_number"]: row for row in products}

    detail_rows = defaultdict(list)
    for row in read_zip_json(CACHE / "tfda_info43.zip"):
        licence = clean(row.get(K43["lic"]))
        if licence in formal_licences:
            detail_rows[licence].append(row)

    substances = {}
    product_substances = []
    concentration_review = []
    seen_detail = set()
    for licence, product in product_by_licence.items():
        official = official37.get(licence, {})
        active_summary = clean(official.get(K["active"]))
        active_key = chemical_key(active_summary)
        matched_active = 0
        for detail in detail_rows.get(licence, []):
            ingredient = clean(detail.get(K43["name"]))
            code = clean(detail.get(K43["code"]))
            # The official main-active summary is the authoritative role
            # evidence.  Excipients are classified only when they are absent
            # from that active summary; names such as active citrate salts must
            # not be mistaken for buffers merely because they contain CITRATE.
            if chemical_key(ingredient) and chemical_key(ingredient) in active_key:
                role = "active"
                confirmation = "confirmed"
                matched_active += 1
            elif (role := excipient_role(ingredient)):
                confirmation = "official_detail_role_inferred"
            else:
                role = "unknown"
                confirmation = "needs_review"

            parsed = parse_concentration(
                prescription_label=clean(detail.get(K43["label"])),
                amount_description=clean(detail.get(K43["desc"])),
                amount_value=detail.get(K43["value"]),
                amount_unit=clean(detail.get(K43["unit"])),
                ingredient_name=ingredient,
                preparation_type=product["preparation_type"],
                source_id=SOURCE43,
            )
            substance_id = f"sub_tfda_{code}" if code else "sub_" + slug(ingredient)
            dedupe_key = (
                product["product_id"],
                substance_id,
                parsed["numerator_value"],
                parsed["numerator_unit"],
                parsed["denominator_value"],
                parsed["denominator_unit"],
                parsed["normalization_status"],
            )
            if dedupe_key in seen_detail:
                continue
            seen_detail.add(dedupe_key)
            substances.setdefault(
                substance_id,
                {
                    "substance_id": substance_id,
                    "raw_name": ingredient,
                    "normalized_name": ingredient.lower(),
                    "base_substance_group": ingredient.lower(),
                    "source_id": SOURCE43,
                },
            )
            ps = {
                "product_id": product["product_id"],
                "substance_id": substance_id,
                "raw_name": ingredient,
                "normalized_name": ingredient.lower(),
                "base_substance_group": ingredient.lower(),
                **parsed,
                "role": role,
                "confirmation_status": confirmation,
                "source_id": SOURCE43,
            }
            product_substances.append(ps)
            if role == "active" and parsed["normalization_status"] == "unresolved":
                concentration_review.append(
                    {
                        "product_id": product["product_id"],
                        "license_number": licence,
                        "chinese_name": product["chinese_name"],
                        "substance_id": substance_id,
                        "raw_name": ingredient,
                        "strength_raw": parsed["strength_raw"],
                        "normalization_status": "unresolved",
                        "parsing_rule": parsed["parsing_rule"],
                        "confidence": parsed["confidence"],
                        "reason": f"Official detail retained; parser did not infer beyond rule {parsed['parsing_rule']}.",
                        "source_id": SOURCE43,
                    }
                )

        if matched_active == 0:
            # Preserve the phase-1 confirmed-active evidence without inventing
            # a strength when no matching detailed row exists.
            substance_id = "sub_" + slug(active_summary)
            substances.setdefault(
                substance_id,
                {
                    "substance_id": substance_id,
                    "raw_name": active_summary,
                    "normalized_name": active_summary.lower(),
                    "base_substance_group": "",
                    "source_id": SOURCE37,
                },
            )
            fallback = {
                field: "" for field in PRODUCT_SUBSTANCE_FIELDS
            }
            fallback.update(
                {
                    "product_id": product["product_id"],
                    "substance_id": substance_id,
                    "raw_name": active_summary,
                    "normalized_name": active_summary.lower(),
                    "role": "active",
                    "confirmation_status": "confirmed",
                    "normalization_status": "unresolved",
                    "concentration_status": "unresolved",
                    "parsing_rule": "official_detail_row_missing",
                    "confidence": "low",
                    "source_id": SOURCE37,
                }
            )
            product_substances.append(fallback)
            concentration_review.append(
                {
                    "product_id": product["product_id"],
                    "license_number": licence,
                    "chinese_name": product["chinese_name"],
                    "substance_id": substance_id,
                    "raw_name": active_summary,
                    "strength_raw": "",
                    "normalization_status": "unresolved",
                    "parsing_rule": "official_detail_row_missing",
                    "confidence": "low",
                    "reason": "No matching row was found in the existing local TFDA detail cache.",
                    "source_id": SOURCE37,
                }
            )

    resolution_fields = REVIEW_FIELDS + [
        "review_reason",
        "use_text_type",
        "name_features",
        "derived_preparation_type",
        "decision",
        "dosage_form_group",
        "preparation_type",
        "resolution_rule_id",
        "confidence",
        "official_evidence",
        "resolved_at",
    ]
    write_csv("manual_review_resolution.csv", resolutions, resolution_fields)
    write_csv(
        "candidate_resolution_rules.csv",
        RULES,
        ["rule_id", "priority", "decision", "description", "required_evidence", "confidence"],
    )

    summary_groups = defaultdict(Counter)
    for row in resolutions:
        key = (
            row["review_reason"],
            row["dosage_form_raw"],
            row["use_text_type"],
            row["name_features"],
            row["derived_preparation_type"],
            row["reason"],
        )
        summary_groups[key][row["decision"]] += 1
    summary_rows = []
    for key, counts in sorted(summary_groups.items(), key=lambda item: (-sum(item[1].values()), item[0][1])):
        summary_rows.append(
            {
                "review_reason": key[0],
                "dosage_form_raw": key[1],
                "use_text_type": key[2],
                "name_features": key[3],
                "derived_preparation_type": key[4],
                "review_trigger_rule": key[5],
                "record_count": sum(counts.values()),
                "auto_include_count": counts["auto_include"],
                "auto_exclude_count": counts["auto_exclude"],
                "unresolved_count": counts["unresolved"],
            }
        )
    write_csv(
        "manual_review_reason_summary.csv",
        summary_rows,
        [
            "review_reason",
            "dosage_form_raw",
            "use_text_type",
            "name_features",
            "derived_preparation_type",
            "review_trigger_rule",
            "record_count",
            "auto_include_count",
            "auto_exclude_count",
            "unresolved_count",
        ],
    )

    unresolved_queue = [
        {
            **{field: row.get(field, "") for field in REVIEW_FIELDS},
            "reason": f"{row['resolution_rule_id']}: {row['reason']}",
            "recommended_action": "Keep unresolved; do not include in formal data or statistics without stronger official structured evidence.",
        }
        for row in unresolved_resolutions
    ]

    if SOURCE43 not in {row["source_id"] for row in sources}:
        sources.append(
            {
                "source_id": SOURCE43,
                "source_type": "TFDA_open_data_cache",
                "source_name": "TFDA detailed prescription ingredient data",
                "source_detail": "Reused local official InfoId=43 cache and filtered to phase-1 licences; no download or OCR.",
                "official_url": "https://data.gov.tw/",
                "checked_at": NOW,
            }
        )

    write_csv("products.csv", products, PRODUCT_FIELDS)
    write_csv("archived_or_inactive_products.csv", archived, PRODUCT_FIELDS)
    write_csv("substances.csv", substances.values(), SUBSTANCE_FIELDS)
    write_csv("product_substances.csv", product_substances, PRODUCT_SUBSTANCE_FIELDS)
    write_csv("excluded_records.csv", excluded, EXCLUDED_FIELDS)
    write_csv("manual_review_queue.csv", unresolved_queue, REVIEW_FIELDS)
    write_csv("concentration_review_queue.csv", concentration_review, CONCENTRATION_REVIEW_FIELDS)
    write_csv("indications.csv", indications, ["indication_id", "indication_raw", "indication_normalized", "source_id"])
    write_csv("product_indications.csv", product_indications, ["product_id", "indication_id", "source_id"])
    write_csv("product_classes.csv", product_classes, ["product_id", "class_id", "classification_evidence", "source_id"])
    write_csv("sources.csv", sources, ["source_id", "source_type", "source_name", "source_detail", "official_url", "checked_at"])

    product_active = defaultdict(list)
    for row in product_substances:
        if row["role"] == "active" and row["confirmation_status"] == "confirmed":
            product_active[row["product_id"]].append(row)
    strength_products = {pid for pid, rows in product_active.items() if any(row["strength_raw"] for row in rows)}
    display_products = {pid for pid, rows in product_active.items() if any(row["display_concentration"] for row in rows)}
    per_ml_products = {pid for pid, rows in product_active.items() if any(row["normalized_value_per_ml"] for row in rows)}
    concentration_review_products = {row["product_id"] for row in concentration_review}
    main_unparsed = Counter(row["parsing_rule"] for row in concentration_review)
    preparations = Counter(row["preparation_type"] for row in products)

    core_complete = 0
    for product in products:
        core_fields = (
            product["license_number"],
            product["chinese_name"] or product["english_name"],
            product["dosage_form_group"],
            product["preparation_type"],
            product["route_normalized"],
            product["indication_raw"],
            product["therapeutic_class"],
            product["license_year"],
            product["license_status"],
            product["source_id"],
            product_active.get(product["product_id"]),
        )
        core_complete += int(all(core_fields))
    website_core = 100 * core_complete / len(products) if products else 0

    official_dose_products = {
        row["product_id"]
        for row in products
        if clean(row["route_raw"]) and clean(row["route_raw"]) not in {"請詳見仿單", "詳如仿單", "詳見仿單"}
    }
    dosing_points = len(strength_products) + len(display_products) + len(per_ml_products) + len(official_dose_products)
    dosing_completeness = 100 * dosing_points / (4 * len(products)) if products else 0
    ready = bool(products) and core_complete == len(products)

    completed = {row["license_number"]: row for row in state.get("completed_records", [])}
    for row in resolutions:
        licence = row["license_number"]
        if row["decision"] == "auto_include":
            product_id = new_product_ids.get(licence, existing_by_licence.get(licence, {}).get("product_id", ""))
            completed[licence] = {"license_number": licence, "status": "included", "product_id": product_id, "last_updated": NOW}
        elif row["decision"] == "auto_exclude":
            completed[licence] = {"license_number": licence, "status": "excluded", "last_updated": NOW}
        else:
            completed[licence] = {"license_number": licence, "status": "manual_review", "last_updated": NOW}
    state.update(
        {
            "phase": "phase_2_manual_resolution_and_concentration_complete",
            "included_total": len(products),
            "excluded_total": len(excluded),
            "manual_review_total": len(unresolved_queue),
            "completed_records": list(completed.values()),
            "resume_from": "phase 2 complete; rerun resolve_manual_and_concentrations.py safely updates by licence",
            "updated_at": NOW,
            "phase_2": {
                "before_formal_total": baseline_formal,
                "before_manual_review_total": baseline_manual,
                "auto_included_total": len(include_resolutions),
                "auto_excluded_total": len(exclude_resolutions),
                "unresolved_total": len(unresolved_resolutions),
                "after_formal_total": len(products),
                "strength_product_total": len(strength_products),
                "display_concentration_product_total": len(display_products),
                "per_ml_normalized_product_total": len(per_ml_products),
                "concentration_review_product_total": len(concentration_review_products),
                "batch_size_max": 50,
                "source_scope": "existing phase-1 licences only",
                "downloads": 0,
                "ocr_runs": 0,
            },
        }
    )
    (B / "processing_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

    pct = lambda count: 100 * count / len(products) if products else 0
    report = f"""# Data quality report

## Phase 2 outcome

- Formal products before / after: {baseline_formal} / {len(products)}
- Manual-review baseline: {baseline_manual}
- Automatically included: {len(include_resolutions)}
- Automatically excluded: {len(exclude_resolutions)}
- Still unresolved: {len(unresolved_resolutions)}
- Preparation types: {dict(preparations)}
- Products with confirmed active: {len(product_active)} / {len(products)}
- Products with strength_raw: {len(strength_products)} / {len(products)} ({pct(len(strength_products)):.1f}%)
- Products with display_concentration: {len(display_products)} / {len(products)} ({pct(len(display_products)):.1f}%)
- Products normalized per mL: {len(per_ml_products)} / {len(products)} ({pct(len(per_ml_products)):.1f}%)
- Concentration review products: {len(concentration_review_products)}; queue rows: {len(concentration_review)}
- Main unresolved concentration reasons: {dict(main_unparsed)}
- website_core_completeness: {website_core:.1f}%
- dosing_data_completeness: {dosing_completeness:.1f}%
- optional_detail_completeness: 0.0%
- ready_for_site: {'yes' if ready else 'no'}

All manual decisions are rule-based and retain TFDA structured evidence. Official display bases are preserved; bottle/sachet totals are not converted to per mL. Reconstituted products require explicit post-reconstitution wording before a liquid concentration is normalized. No website files, leaflet downloads, or OCR were used.
"""
    (B / "data_quality_report.md").write_text(report, encoding="utf-8")

    build_summary = f"""# Build summary

Phase 2 completed using the phase-1 CSVs plus existing local TFDA InfoId 37 and 43 caches, restricted to existing product/review licences.

- Manual-review resolution: {len(include_resolutions)} included, {len(exclude_resolutions)} excluded, {len(unresolved_resolutions)} unresolved.
- Formal products: {baseline_formal} -> {len(products)}.
- Concentration parser: {len(display_products)} products have an official display concentration; {len(per_ml_products)} have a separately normalized per-mL value.
- No website/HTML/card changes, downloads, leaflet processing, OCR, or new candidate discovery.
"""
    (B / "build_summary.md").write_text(build_summary, encoding="utf-8")

    print(
        json.dumps(
            {
                "formal_before": baseline_formal,
                "formal_after": len(products),
                "auto_included": len(include_resolutions),
                "auto_excluded": len(exclude_resolutions),
                "unresolved": len(unresolved_resolutions),
                "preparation_types": preparations,
                "strength_products": len(strength_products),
                "display_products": len(display_products),
                "per_ml_products": len(per_ml_products),
                "concentration_review_products": len(concentration_review_products),
                "website_core_completeness": round(website_core, 1),
                "dosing_data_completeness": round(dosing_completeness, 1),
                "ready_for_site": ready,
            },
            ensure_ascii=False,
            default=dict,
        )
    )


if __name__ == "__main__":
    main()
