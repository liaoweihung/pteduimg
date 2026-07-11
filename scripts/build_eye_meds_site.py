import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HANDOFF_ROOT = ROOT / "research" / "work_handoff"
VERSION = "2026-07-10_v01"
HANDOFF = HANDOFF_ROOT / VERSION
OUT = ROOT / "data" / "eye_meds"

ROLE_LABELS = {
    "active": "有效成分",
    "preservative": "防腐劑／保存劑",
    "vehicle": "基劑或溶媒",
    "buffer": "緩衝劑",
    "tonicity_agent": "等張調節劑",
    "viscosity_agent": "黏度調節劑",
    "chelator": "螯合劑",
    "surfactant": "界面活性劑",
    "antioxidant": "抗氧化劑",
    "ph_adjuster": "酸鹼調節劑",
    "ointment_base": "眼藥膏基劑",
    "other_excipient": "其他賦形劑",
    "unknown": "待確認",
}

DOSAGE_LABELS = {
    "ophthalmic_solution": "點眼液／眼用溶液",
    "ophthalmic_suspension": "眼用懸液",
    "ophthalmic_emulsion": "眼用乳劑",
    "ophthalmic_gel": "眼用凝膠",
    "ophthalmic_ointment": "眼藥膏",
}

PRESERVATIVE_FREE_LABELS = {
    "confirmed_preservative_free": "明確無保存劑",
    "contains_preservative": "確認含保存劑",
    "unknown": "資料不足",
}

EXPECTED_COLUMNS = {
    "products.csv": [
        "product_id", "license_number", "chinese_name", "english_name",
        "dosage_form_raw", "dosage_form_normalized", "route_raw",
        "route_normalized", "ophthalmic_inclusion_evidence", "legal_category",
        "therapeutic_class", "applicant", "manufacturer", "indication_raw",
        "license_status", "license_expiry_date", "status_checked_at",
        "default_include_in_search", "default_include_in_statistics",
        "preservative_free_status", "preservative_free_evidence", "source_id",
        "verified_at",
    ],
    "product_substances.csv": [
        "product_substance_id", "product_id", "substance_id", "raw_name",
        "standardized_name", "chinese_name", "english_name",
        "salt_ester_hydrate_form", "base_substance_group", "amount_raw",
        "amount", "unit", "role", "formulation_function",
        "role_assignment_method", "source_id", "confirmed",
    ],
    "substances.csv": [
        "substance_id", "original_names", "standardized_name", "chinese_name",
        "english_name", "salt_ester_hydrate_form", "base_substance_group",
        "default_analytical_role", "normalization_confirmed", "source_id",
    ],
    "indications.csv": [
        "indication_id", "standardized_name_zh", "standardized_name_en",
        "normalization_method",
    ],
    "product_indications.csv": [
        "product_id", "indication_id", "evidence_text", "mapping_method",
        "source_id", "confirmed",
    ],
    "drug_classes.csv": ["class_id", "code", "class_name", "classification_system"],
    "product_classes.csv": ["product_id", "class_id", "is_primary", "source_id"],
    "excluded_records.csv": [
        "license_number", "chinese_name", "dosage_form_raw", "license_kind",
        "exclusion_reason", "source_id",
    ],
}


def read_csv(name):
    with (HANDOFF / name).open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def read_csv_stream(name):
    with (HANDOFF / name).open("r", encoding="utf-8-sig", newline="") as f:
        yield from csv.DictReader(f)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def truthy(value):
    return str(value).strip().lower() == "true"


def validate_handoff():
    manifest_path = HANDOFF / "HANDOFF_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    checks = []
    ok = manifest.get("status") == "ready"
    checks.append(("manifest_status_ready", ok, manifest.get("status", "")))
    for item in manifest["file_list"]:
        path = HANDOFF / item["name"]
        exists = path.exists()
        size_ok = exists and path.stat().st_size == item["size_bytes"]
        hash_ok = exists and sha256(path) == item["sha256"]
        checks.append((f"{item['name']}:exists", exists, ""))
        checks.append((f"{item['name']}:size", size_ok, str(path.stat().st_size) if exists else "missing"))
        checks.append((f"{item['name']}:sha256", hash_ok, ""))
        if item["name"].endswith(".csv") and exists:
            try:
                with path.open("r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.DictReader(f)
                    headers = reader.fieldnames or []
                    first = next(reader, None)
                readable = bool(headers)
                expected = EXPECTED_COLUMNS.get(item["name"])
                columns_ok = expected is None or headers == expected
                detail = ",".join(headers)
            except Exception as exc:
                readable = False
                columns_ok = False
                detail = repr(exc)
            checks.append((f"{item['name']}:csv_readable", readable, detail))
            checks.append((f"{item['name']}:columns", columns_ok, detail))
    return manifest, checks


def product_status(product):
    return "active" if truthy(product["default_include_in_search"]) else "inactive"


def substance_record(row):
    role = row["role"] or "unknown"
    return {
        "product_substance_id": row["product_substance_id"],
        "substance_id": row["substance_id"],
        "raw_name": row["raw_name"],
        "standardized_name": row["standardized_name"],
        "chinese_name": row["chinese_name"],
        "english_name": row["english_name"],
        "salt_ester_hydrate_form": row["salt_ester_hydrate_form"],
        "base_substance_group": row["base_substance_group"],
        "amount_raw": row["amount_raw"],
        "amount": row["amount"],
        "unit": row["unit"],
        "role": role,
        "role_label": ROLE_LABELS.get(role, "待確認"),
        "formulation_function": row["formulation_function"],
        "source_id": row["source_id"],
        "confirmed": truthy(row["confirmed"]),
    }


def group_by(rows, key):
    data = defaultdict(list)
    for row in rows:
        data[row[key]].append(row)
    return data


def top_counts(counter, limit=30):
    return [{"name": name, "count": count} for name, count in counter.most_common(limit)]


def count_products_by_substance(products, substances, role_filter, product_filter):
    product_ids = {p["product_id"] for p in products if product_filter(p)}
    grouped = defaultdict(set)
    for row in substances:
        if row["product_id"] in product_ids and row["role"] in role_filter:
            grouped[row["base_substance_group"] or row["standardized_name"]].add(row["product_id"])
    denom = len(product_ids) or 1
    result = []
    for name, ids in grouped.items():
        result.append({
            "name": name,
            "product_count": len(ids),
            "proportion": round(len(ids) / denom, 4),
            "product_ids": sorted(ids),
        })
    return sorted(result, key=lambda x: (-x["product_count"], x["name"]))


def build():
    manifest, checks = validate_handoff()
    failed = [c for c in checks if not c[1]]
    if failed:
        raise SystemExit("Handoff validation failed; see generated report after fixing input.")

    OUT.mkdir(parents=True, exist_ok=True)
    products = read_csv("products.csv")
    product_substances = read_csv("product_substances.csv")
    product_indications = read_csv("product_indications.csv")
    indications = {r["indication_id"]: r for r in read_csv("indications.csv")}
    product_classes = read_csv("product_classes.csv")
    classes = {r["class_id"]: r for r in read_csv("drug_classes.csv")}
    sources = {r["source_id"]: r for r in read_csv("sources.csv")}
    manual_review = read_csv("manual_review_queue.csv")

    substances_by_product = defaultdict(lambda: defaultdict(list))
    all_substances_by_product = defaultdict(list)
    for row in product_substances:
        rec = substance_record(row)
        substances_by_product[row["product_id"]][rec["role"]].append(rec)
        all_substances_by_product[row["product_id"]].append(rec)

    indications_by_product = group_by(product_indications, "product_id")
    classes_by_product = group_by(product_classes, "product_id")
    products_by_id = {p["product_id"]: p for p in products}

    clean_products = []
    for p in products:
        pid = p["product_id"]
        ind_rows = indications_by_product.get(pid, [])
        class_rows = classes_by_product.get(pid, [])
        active = substances_by_product[pid].get("active", [])
        preservatives = substances_by_product[pid].get("preservative", [])
        excipients = [
            s for s in all_substances_by_product[pid]
            if s["role"] not in {"active", "preservative"}
        ]
        clean_products.append({
            "product_id": pid,
            "license_number": p["license_number"],
            "chinese_name": p["chinese_name"],
            "english_name": p["english_name"],
            "dosage_form_raw": p["dosage_form_raw"],
            "dosage_form": p["dosage_form_normalized"],
            "dosage_form_label": DOSAGE_LABELS.get(p["dosage_form_normalized"], p["dosage_form_normalized"]),
            "route_raw": p["route_raw"],
            "route": p["route_normalized"],
            "ophthalmic_inclusion_evidence": p["ophthalmic_inclusion_evidence"],
            "legal_category": p["legal_category"],
            "therapeutic_class": p["therapeutic_class"],
            "applicant": p["applicant"],
            "manufacturer": p["manufacturer"],
            "indication_raw": p["indication_raw"],
            "license_status": p["license_status"],
            "status_group": product_status(p),
            "license_expiry_date": p["license_expiry_date"],
            "status_checked_at": p["status_checked_at"],
            "default_include_in_search": truthy(p["default_include_in_search"]),
            "default_include_in_statistics": truthy(p["default_include_in_statistics"]),
            "preservative_free_status": p["preservative_free_status"],
            "preservative_free_label": PRESERVATIVE_FREE_LABELS.get(p["preservative_free_status"], "資料不足"),
            "preservative_free_evidence": p["preservative_free_evidence"],
            "verified_at": p["verified_at"],
            "source_id": p["source_id"],
            "source": sources.get(p["source_id"], {}),
            "active_ingredients": active,
            "preservatives": preservatives,
            "excipients": excipients,
            "substances": all_substances_by_product[pid],
            "standardized_indications": [
                {
                    "indication_id": r["indication_id"],
                    "name_zh": indications.get(r["indication_id"], {}).get("standardized_name_zh", r["indication_id"]),
                    "name_en": indications.get(r["indication_id"], {}).get("standardized_name_en", ""),
                    "evidence_text": r["evidence_text"],
                    "confirmed": truthy(r["confirmed"]),
                }
                for r in ind_rows
            ],
            "drug_classes": [
                {
                    "class_id": r["class_id"],
                    "code": classes.get(r["class_id"], {}).get("code", ""),
                    "class_name": classes.get(r["class_id"], {}).get("class_name", r["class_id"]),
                    "classification_system": classes.get(r["class_id"], {}).get("classification_system", ""),
                    "is_primary": truthy(r["is_primary"]),
                }
                for r in class_rows
            ],
            "search_text": " ".join([
                p["license_number"], p["chinese_name"], p["english_name"],
                p["dosage_form_raw"], p["dosage_form_normalized"], p["legal_category"],
                p["therapeutic_class"], p["applicant"], p["manufacturer"], p["indication_raw"],
                " ".join(s["base_substance_group"] for s in all_substances_by_product[pid]),
                " ".join(s["standardized_name"] for s in all_substances_by_product[pid]),
            ]).lower(),
        })

    active_products = [p for p in clean_products if p["status_group"] == "active"]
    all_product_filter = lambda p: truthy(p["default_include_in_statistics"])

    indication_active = []
    for ind_id, rows in group_by(product_indications, "indication_id").items():
        active_pids = {
            r["product_id"] for r in rows
            if products_by_id.get(r["product_id"], {}).get("default_include_in_statistics") == "true"
        }
        for item in count_products_by_substance(products, product_substances, {"active"}, lambda p, ids=active_pids: p["product_id"] in ids):
            indication_active.append({
                "indication_id": ind_id,
                "indication_name": indications.get(ind_id, {}).get("standardized_name_zh", ind_id),
                **item,
            })

    active_by_therapeutic = defaultdict(Counter)
    active_by_dosage = defaultdict(Counter)
    preservative_by_therapeutic = defaultdict(Counter)
    preservative_by_dosage = defaultdict(Counter)
    excipient_by_role = defaultdict(Counter)
    excipient_by_dosage = defaultdict(Counter)

    for p in active_products:
        pid = p["product_id"]
        for s in p["active_ingredients"]:
            name = s["base_substance_group"] or s["standardized_name"]
            active_by_therapeutic[p["therapeutic_class"]][name] += 1
            active_by_dosage[p["dosage_form"]][name] += 1
        for s in p["preservatives"]:
            name = s["base_substance_group"] or s["standardized_name"]
            preservative_by_therapeutic[p["therapeutic_class"]][name] += 1
            preservative_by_dosage[p["dosage_form"]][name] += 1
        for s in p["excipients"]:
            name = s["base_substance_group"] or s["standardized_name"]
            excipient_by_role[s["role_label"]][name] += 1
            excipient_by_dosage[p["dosage_form"]][name] += 1

    def cooccurrence(role_set):
        pair_counts = Counter()
        pair_products = defaultdict(list)
        for p in active_products:
            names = sorted({
                s["base_substance_group"] or s["standardized_name"]
                for s in p["substances"] if s["role"] in role_set
            })
            for a, b in combinations(names, 2):
                pair_counts[(a, b)] += 1
                pair_products[(a, b)].append(p["product_id"])
        return [
            {
                "substance_a": a,
                "substance_b": b,
                "product_count": count,
                "proportion": round(count / (len(active_products) or 1), 4),
                "product_ids": pair_products[(a, b)],
            }
            for (a, b), count in pair_counts.most_common(100)
        ]

    active_analysis = {
        "by_indication": sorted(indication_active, key=lambda x: (-x["product_count"], x["indication_name"], x["name"])),
        "cooccurrence": cooccurrence({"active"}),
        "by_therapeutic_class": {k: top_counts(v) for k, v in sorted(active_by_therapeutic.items())},
        "by_dosage_form": {k: top_counts(v) for k, v in sorted(active_by_dosage.items())},
        "overall": count_products_by_substance(products, product_substances, {"active"}, all_product_filter),
    }

    preservative_analysis = {
        "overall": count_products_by_substance(products, product_substances, {"preservative"}, all_product_filter),
        "by_therapeutic_class": {k: top_counts(v) for k, v in sorted(preservative_by_therapeutic.items())},
        "by_dosage_form": {k: top_counts(v) for k, v in sorted(preservative_by_dosage.items())},
        "confirmed_preservative_free_products": [
            p for p in clean_products
            if p["status_group"] == "active" and p["preservative_free_status"] == "confirmed_preservative_free"
        ],
        "status_counts": dict(Counter(p["preservative_free_status"] for p in active_products)),
    }

    excipient_roles = set(ROLE_LABELS) - {"active", "preservative"}
    excipient_analysis = {
        "by_role": {k: top_counts(v) for k, v in sorted(excipient_by_role.items())},
        "cooccurrence": cooccurrence(excipient_roles),
        "by_dosage_form": {k: top_counts(v) for k, v in sorted(excipient_by_dosage.items())},
        "completion": {
            "active_products": len(active_products),
            "with_any_excipient": sum(1 for p in active_products if p["excipients"]),
            "rate": round(sum(1 for p in active_products if p["excipients"]) / (len(active_products) or 1), 4),
        },
    }

    excluded_counts = Counter()
    suspicious_rows = []
    suspect_terms = ["口服", "注射", "內服", "錠", "膠囊", "輸注", "植入", "洗眼", "隱形眼鏡"]
    for row in read_csv_stream("excluded_records.csv"):
        excluded_counts[row["exclusion_reason"]] += 1
    for p in clean_products:
        haystack = " ".join([p["chinese_name"], p["english_name"], p["dosage_form_raw"], p["route_raw"], p["indication_raw"]])
        if any(term in haystack for term in suspect_terms):
            suspicious_rows.append({
                "product_id": p["product_id"],
                "license_number": p["license_number"],
                "chinese_name": p["chinese_name"],
                "license_status": p["license_status"],
                "dosage_form_raw": p["dosage_form_raw"],
                "route_raw": p["route_raw"],
                "matched_terms": [term for term in suspect_terms if term in haystack],
            })

    summary = {
        "version": manifest["version"],
        "created_at": manifest["created_at"],
        "source_date_range": manifest["source_date_range"],
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "product_count": len(clean_products),
        "active_product_count": len(active_products),
        "inactive_product_count": len(clean_products) - len(active_products),
        "excluded_raw_material_count": manifest["excluded_raw_material_count"],
        "excluded_non_ophthalmic_count": manifest["excluded_non_ophthalmic_count"],
        "excluded_oral_or_systemic_count": manifest["excluded_oral_or_systemic_count"],
        "manual_review_count": len(manual_review),
        "preservative_completion": {
            "known_products": sum(1 for p in active_products if p["preservative_free_status"] != "unknown"),
            "active_products": len(active_products),
            "rate": round(sum(1 for p in active_products if p["preservative_free_status"] != "unknown") / (len(active_products) or 1), 4),
        },
        "excipient_completion": excipient_analysis["completion"],
        "known_limitations": manifest.get("known_limitations", []),
    }

    facets = {
        "dosage_forms": sorted({p["dosage_form"] for p in clean_products if p["dosage_form"]}),
        "legal_categories": sorted({p["legal_category"] for p in clean_products if p["legal_category"]}),
        "therapeutic_classes": sorted({p["therapeutic_class"] for p in clean_products if p["therapeutic_class"]}),
        "preservatives": sorted({
            s["base_substance_group"] or s["standardized_name"]
            for p in clean_products for s in p["preservatives"]
            if s["base_substance_group"] or s["standardized_name"]
        }),
        "active_ingredients": sorted({
            s["base_substance_group"] or s["standardized_name"]
            for p in clean_products for s in p["active_ingredients"]
            if s["base_substance_group"] or s["standardized_name"]
        }),
        "indications": sorted({
            i["name_zh"] for p in clean_products for i in p["standardized_indications"] if i["name_zh"]
        }),
    }

    site_data = {
        "summary": summary,
        "facets": facets,
        "role_labels": ROLE_LABELS,
        "dosage_labels": DOSAGE_LABELS,
        "preservative_free_labels": PRESERVATIVE_FREE_LABELS,
        "products": clean_products,
        "analyses": {
            "active_ingredients": active_analysis,
            "preservatives": preservative_analysis,
            "excipients": excipient_analysis,
        },
    }

    write_json(OUT / "clean_products.json", clean_products)
    write_json(OUT / "site_data.json", site_data)
    write_json(OUT / "active_ingredient_analysis.json", active_analysis)
    write_json(OUT / "preservative_analysis.json", preservative_analysis)
    write_json(OUT / "excipient_analysis.json", excipient_analysis)
    write_json(OUT / "summary.json", summary)

    import_report(manifest, checks)
    data_audit(summary, excluded_counts, suspicious_rows, manual_review)


def import_report(manifest, checks):
    lines = [
        "# Work 交接包匯入報告",
        "",
        f"- 取得時間：{datetime.now().astimezone().isoformat(timespec='seconds')}",
        f"- Library / Drive 資料夾：眼用藥品資料庫交接包",
        f"- 使用版本：{manifest['version']}",
        f"- created_at：{manifest['created_at']}",
        f"- status：{manifest['status']}",
        f"- materialize 路徑：`research/work_handoff/{manifest['version']}/`",
        "",
        "## 驗證結果",
        "",
    ]
    failed = [c for c in checks if not c[1]]
    lines.append(f"- 必要檔案、大小、SHA-256、CSV 可讀性與欄位檢查：{'通過' if not failed else '未通過'}")
    lines.append(f"- 檢查項目數：{len(checks)}")
    lines.append(f"- 失敗項目數：{len(failed)}")
    lines.extend(["", "## 檔案清單", ""])
    for item in manifest["file_list"]:
        lines.append(f"- `{item['name']}`：{item['size_bytes']} bytes，SHA-256 `{item['sha256']}`")
    if failed:
        lines.extend(["", "## 失敗項目", ""])
        for name, _, detail in failed:
            lines.append(f"- {name}: {detail}")
    (HANDOFF_ROOT / "IMPORT_REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def data_audit(summary, excluded_counts, suspicious_rows, manual_review):
    lines = [
        "# DATA_AUDIT",
        "",
        f"- 資料包版本：{summary['version']}",
        f"- 產生時間：{summary['generated_at']}",
        f"- 有效藥證產品數：{summary['active_product_count']}",
        f"- 失效藥證產品數：{summary['inactive_product_count']}",
        f"- 排除原料藥數量：{summary['excluded_raw_material_count']}",
        f"- 排除非眼用產品數量：{summary['excluded_non_ophthalmic_count']}",
        f"- 排除口服、注射或全身性產品數量：{summary['excluded_oral_or_systemic_count']}",
        f"- 保存劑資料完整率：{summary['preservative_completion']['rate']:.1%}",
        f"- 賦形劑資料完整率：{summary['excipient_completion']['rate']:.1%}",
        f"- 待人工確認數量：{summary['manual_review_count']}",
        "",
        "## 排除紀錄統計",
        "",
    ]
    for reason, count in excluded_counts.most_common():
        lines.append(f"- {reason}: {count}")
    lines.extend(["", "## 程式化非局部眼用混入檢查", ""])
    if suspicious_rows:
        lines.append("下列已收錄產品含有口服、注射、洗眼、植入或隱形眼鏡等提示詞，需人工複核：")
        lines.append("")
        for row in suspicious_rows:
            lines.append(
                f"- {row['license_number']} {row['chinese_name']} "
                f"({row['license_status']})：{','.join(row['matched_terms'])}"
            )
    else:
        lines.append("未在已收錄產品中偵測到口服、注射、全身性、洗眼或隱形眼鏡保養液提示詞。")
    lines.extend(["", "## 待人工確認清單", ""])
    for row in manual_review:
        lines.append(f"- {row['license_number']} {row['chinese_name']}：{row['issue']}；建議：{row['suggested_action']}")
    (ROOT / "DATA_AUDIT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build()
