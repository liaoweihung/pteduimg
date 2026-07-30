#!/usr/bin/env python3
"""Build a local-only composition analysis for TCM external patches/products.

This deliberately analyses the official prescription text of the selected
external products.  It neither downloads data nor attempts to assign any oral
traditional mother formula.
"""
from __future__ import annotations

import csv
import json
import re
import shutil
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "tcm_formula_explorer"
OUT = ROOT / "data" / "tcm_external_formula_patterns_20260730"
PATCH_FORM = "藥膠布劑"
RX_CLASS = "須由中醫師處方使用"
RX_FORMS = {"油膏劑", "外用粉劑", "軟膏劑", "硬膏劑"}
TRADITIONAL = "traditional_medicinal_material"

# Only unambiguous spelling variants are merged.  The raw source name remains
# in product_materials.csv; anything not confidently classifiable is queued.
NORMALIZE = {
    "黃蘗": "黃柏", "黃苓": "黃芩", "白芨": "白及", "官桂": "肉桂",
    "元參": "玄參", "木鱉子": "木鼈子", "烏賊骨": "海螵蛸",
    "川白芷": "白芷", "懷牛膝": "牛膝", "製南星": "天南星",
    "生天南星": "天南星", "生半夏": "半夏", "製半夏": "半夏",
    "製甘遂": "甘遂", "製大戟": "大戟",
}
TOPICAL_VOLATILES = {
    "薄荷腦", "冰片", "冬綠油", "樟腦", "薄荷油", "桉油", "桉葉油",
    "尤加利油", "丁香油", "松節油", "薰衣草油", "樟腦油", "丁香醇",
    "桂花油", "葡萄柚油", "辣椒精油",
}
VEHICLE_TERMS = (
    "橡膠", "樹脂", "松脂", "松香", "膠質", "膠布", "基劑", "凡士林", "羊毛脂", "鯨蠟醇",
    "麻油", "芝麻油", "清油", "蜂蠟", "石蠟", "硬脂酸", "聚乙烯", "聚丙烯",
    "聚山梨醇", "聚乙二醇", "純水", "蒸餾水", "乙醇", "酒精", "甘油", "硬脂醇", "單硬脂酸甘油酯", "黃蠟", "白蠟", "凡士林", "基質", "瀝青", "沙拉油", "蓖麻子油", "牛皮膠", "米醋", "薑汁", "葱汁", "蔥汁", "香油",
)
EXCIPIENT_TERMS = ("氧化鋅", "氧化鉛", "色素", "活性碳", "二氧化鈦", "碳黑", "食用", "麗基")
NONTRADITIONAL_TERMS = (
    "Diphenhydramine", "DIPHENHYDRAMINE", "二苯安明", "對羥基苯甲酸",
    "苯甲酸", "BHA", "BHT", "抗氧化劑", "防腐劑", "氯化", "硫酸", "鹽酸",
    "Methylparaben", "Propylparaben", "Paraben", "氫氯酸鋁",
)
INGREDIENT_RE = re.compile(r"^\s*(?P<name>.*?)\s*\((?P<amount>[^)]*)\)\s*$")
TRAILING_AMOUNT_RE = re.compile(r"\s*\d+(?:\.\d+)?\s*(?:mg|g|mcg|%)\s*$", re.I)


def source_paths() -> list[Path]:
    paths = [SOURCE / "formulas.json"]
    paths.extend(SOURCE / f"products-{number:02d}.json" for number in range(32))
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required source files:\n" + "\n".join(missing))
    return paths


def split_name(value: str) -> tuple[str, str]:
    lines = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    return (lines[0] if lines else "", " ".join(lines[1:]))


def clean_material_name(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" ：:")
    value = TRAILING_AMOUNT_RE.sub("", value).strip()
    return value


def category_for(raw: str) -> str:
    if not raw or "?" in raw or "\uf21f" in raw or "浸膏" in raw or "加至" in raw or "香料" in raw or "香精" in raw or "淨香油" in raw or "遠紅外線" in raw or raw in {"以上生藥製成", "以上生藥"}:
        return "unresolved"
    if raw in TOPICAL_VOLATILES or "精油" in raw or raw.endswith("酚"):
        return "topical_active_or_volatile"
    if any(term in raw for term in EXCIPIENT_TERMS) or "氧化" in raw or "碳酸鈣" in raw or ("色" in raw and ("號" in raw or "紅" in raw or "黃" in raw or "藍" in raw or "綠" in raw)):
        return "excipient_or_colour"
    if any(term in raw for term in VEHICLE_TERMS):
        return "vehicle_or_patch_base"
    if any(term.lower() in raw.lower() for term in NONTRADITIONAL_TERMS) or any(term in raw for term in ("羥基", "甲酯", "丙酯", "鈉", "鉀")) or re.search(r"[A-Za-z]", raw):
        return "nontraditional_active_or_preservative"
    return TRADITIONAL


def parse_prescription(text: str) -> list[tuple[str, str, str]]:
    records: list[tuple[str, str, str]] = []
    for line in str(text or "").splitlines():
        line = line.strip()
        if not line or line.startswith(("處方", "每公克", "每100公克", "每一公克")):
            continue
        match = INGREDIENT_RE.match(line)
        if not match:
            if line:
                records.append((line, "", "unresolved"))
            continue
        raw = clean_material_name(match.group("name"))
        amount = match.group("amount").strip()
        if raw:
            records.append((raw, amount, category_for(raw)))
    return records


def jaccard(left: set[str], right: set[str]) -> float:
    return len(left & right) / len(left | right) if left or right else 0.0


class UnionFind:
    def __init__(self, size: int):
        self.parent = list(range(size))

    def find(self, value: int) -> int:
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left: int, right: int) -> None:
        left, right = self.find(left), self.find(right)
        if left != right:
            self.parent[right] = left


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    paths = source_paths()
    # formulas.json is intentionally validated as a supplied source; it is not
    # used to identify parent formulas or to change product materials.
    json.loads((SOURCE / "formulas.json").read_text(encoding="utf-8"))
    raw_products: list[dict] = []
    for number in range(32):
        raw_products.extend(json.loads((SOURCE / f"products-{number:02d}.json").read_text(encoding="utf-8"))["products"])
    selected = [row for row in raw_products if row.get("form") == PATCH_FORM]
    selected += [row for row in raw_products if row.get("class") == RX_CLASS and row.get("form") in RX_FORMS]
    patch_count = sum(row.get("form") == PATCH_FORM for row in selected)
    rx_count = len(selected) - patch_count
    if len(selected) != 577 or patch_count != 564 or rx_count != 13:
        raise ValueError(f"Selection validation failed: total={len(selected)}, patch={patch_count}, rx={rx_count}")
    if any(row.get("class") != RX_CLASS for row in selected if row.get("form") != PATCH_FORM):
        raise ValueError("Non-patch selection contains a non-prescription product")

    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    product_rows: list[dict] = []
    material_rows: list[dict] = []
    traditional_sets: list[set[str]] = []
    material_products: dict[tuple[str, str], set[str]] = defaultdict(set)
    review: dict[str, dict] = {}
    for product in selected:
        name_zh, name_en = split_name(product.get("name", ""))
        group = "中藥外用貼布" if product.get("form") == PATCH_FORM else "處方外用藥"
        product_rows.append({
            "license": product.get("license", ""), "name_zh": name_zh, "name_en": name_en,
            "group": group, "is_prescription_product": group == "處方外用藥",
            "dosage_form": product.get("form", ""), "regulatory_classification": product.get("class", ""),
            "license_status": product.get("licenseStatus", ""), "official_indications_raw": product.get("indications", ""),
            "official_prescription_raw": product.get("prescription", ""), "source_url": product.get("sourceUrl", ""),
        })
        traditional: set[str] = set()
        for position, (raw, amount, category) in enumerate(parse_prescription(product.get("prescription", "")), start=1):
            normalized = NORMALIZE.get(raw, raw)
            material_rows.append({
                "license": product.get("license", ""), "material_position": position,
                "material_original": raw, "material_normalized": normalized,
                "amount_raw": amount, "material_category": category,
                "official_prescription_raw": product.get("prescription", ""),
            })
            material_products[(normalized, category)].add(product.get("license", ""))
            if category == TRADITIONAL:
                traditional.add(normalized)
            if category == "unresolved":
                review.setdefault(raw, {"material_original": raw, "suggested_normalized": normalized, "reason": "無法由官方處方原文可靠判斷材料或其分類", "product_licenses": set()})["product_licenses"].add(product.get("license", ""))
        traditional_sets.append(traditional)

    # Similarity groups use only traditional materials and require at least two
    # shared materials, so bases/colourants/nontraditional substances never
    # create a group.
    uf = UnionFind(len(selected))
    for left, right in combinations(range(len(selected)), 2):
        shared = traditional_sets[left] & traditional_sets[right]
        if len(shared) >= 2 and jaccard(traditional_sets[left], traditional_sets[right]) >= 0.70:
            uf.union(left, right)
    components: dict[int, list[int]] = defaultdict(list)
    for index in range(len(selected)):
        components[uf.find(index)].append(index)
    ordered_components = sorted(components.values(), key=lambda values: (-len(values), product_rows[values[0]]["license"]))
    cluster_by_index: dict[int, dict] = {}
    clusters: list[dict] = []
    for order, members in enumerate(ordered_components, start=1):
        count = len(members)
        occurrences = Counter(name for index in members for name in traditional_sets[index])
        core = sorted(name for name, value in occurrences.items() if value / count >= .80)
        additions = sorted(name for name, value in occurrences.items() if .20 <= value / count < .80)
        rare = sorted(name for name, value in occurrences.items() if value / count < .20 and len(material_products[(name, TRADITIONAL)]) <= 3)
        cluster = {"cluster_id": f"EFP-{order:03d}", "product_count": count, "member_licenses": [product_rows[index]["license"] for index in members], "core_traditional_materials": core, "common_added_traditional_materials": additions, "rare_or_unique_traditional_materials": rare}
        clusters.append(cluster)
        for index in members:
            cluster_by_index[index] = cluster
    cluster_rows = []
    for index, product in enumerate(product_rows):
        cluster = cluster_by_index[index]
        cluster_rows.append({"license": product["license"], "cluster_id": cluster["cluster_id"], "cluster_product_count": cluster["product_count"], "traditional_materials": "|".join(sorted(traditional_sets[index])), "core_traditional_materials": "|".join(cluster["core_traditional_materials"]), "common_added_traditional_materials": "|".join(cluster["common_added_traditional_materials"]), "rare_or_unique_traditional_materials": "|".join(cluster["rare_or_unique_traditional_materials"])})

    category_counts = Counter(row["material_category"] for row in material_rows)
    frequency_rows = []
    for (name, category), licenses in sorted(material_products.items(), key=lambda item: (-len(item[1]), item[0][0])):
        frequency_rows.append({"material_normalized": name, "material_category": category, "product_count": len(licenses), "percent_of_577": round(len(licenses) / 577 * 100, 3), "product_licenses": "|".join(sorted(licenses))})
    pair_counts: Counter[tuple[str, str]] = Counter()
    for names in traditional_sets:
        pair_counts.update(combinations(sorted(names), 2))
    pair_rows = [{"material_a": a, "material_b": b, "product_count": count, "percent_of_577": round(count / 577 * 100, 3)} for (a, b), count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0])) if count >= 2]
    rare_rows = [{"material_normalized": name, "product_count": len(licenses), "product_licenses": "|".join(sorted(licenses))} for (name, category), licenses in sorted(material_products.items()) if category == TRADITIONAL and len(licenses) <= 3]
    review_rows = [{**value, "product_count": len(value["product_licenses"]), "product_licenses": "|".join(sorted(value["product_licenses"]))} for value in review.values()]

    write_csv(OUT / "products.csv", product_rows, list(product_rows[0]))
    write_csv(OUT / "product_materials.csv", material_rows, list(material_rows[0]))
    write_csv(OUT / "material_frequency.csv", frequency_rows, list(frequency_rows[0]))
    write_csv(OUT / "common_material_pairs.csv", pair_rows, ["material_a", "material_b", "product_count", "percent_of_577"])
    write_csv(OUT / "composition_clusters.csv", cluster_rows, list(cluster_rows[0]))
    write_csv(OUT / "rare_traditional_materials.csv", rare_rows, ["material_normalized", "product_count", "product_licenses"])
    write_csv(OUT / "material_normalization_review_queue.csv", review_rows, ["material_original", "suggested_normalized", "reason", "product_count", "product_licenses"])
    analysis = {"metadata": {"title": "中藥外用貼布與處方外用藥：配方組合分析", "scope": {"total": 577, "patch": 564, "prescription_non_patch": 13}, "method": "依官方處方原文解析材料；相似群只用傳統藥材的 Jaccard 相似度（至少共同兩味、相似度至少 0.70）。", "limitations": "核心、添加與少用成分是統計結果，不是療效證據、傳統母方、歷史源流或臨床推薦。"}, "clusters": clusters, "top_traditional_pairs": pair_rows[:50], "material_categories": category_counts}
    (OUT / "external_formula_pattern_analysis.json").write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (OUT / "README.md").write_text("# 中藥外用貼布與處方外用藥：配方組合分析\n\n本資料包分析現代產品的官方處方原文，並保留每個材料的原始名稱與原始處方。它不重新抓取官方資料，也不配對口服傳統母方。\n\n- 範圍固定為 577 張：564 張藥膠布劑、13 張須由中醫師處方使用的非貼布外用產品。\n- 13 張處方外用藥保留處方藥身分，不能視為 OTC 或成藥。\n- 核心／添加／少用成分僅依群內產品的傳統藥材統計；不是療效證據、傳統母方或臨床推薦。\n- 基質、色素、西藥／防腐成分與無法判定項目會另行分類，絕不混入藥材核心。\n\n重建：`python scripts/build_tcm_external_formula_patterns.py`\n", encoding="utf-8")
    category_summary = "；".join(f"{name} {count}" for name, count in sorted(category_counts.items()))
    (OUT / "data_quality_report.md").write_text(f"# 資料品質報告\n\n- 總產品：{len(product_rows)}（藥膠布劑 {patch_count}；處方外用非貼布 {rx_count}）。\n- 解析材料列：{len(material_rows)}。\n- 材料分類列數：{category_summary}。\n- 未解析／需複核名稱：{len(review_rows)}。\n- 配方群：{len(clusters)}（相似度分群只使用傳統藥材）。\n- 驗證：所有非貼布選入產品的法規分類均為「{RX_CLASS}」。\n", encoding="utf-8")
    zip_name = "tcm_external_formula_patterns_20260730.zip"
    state = {"status": "complete", "script": "scripts/build_tcm_external_formula_patterns.py", "source_files": [str(path.relative_to(ROOT)) for path in paths], "validation": {"total": len(product_rows), "patch": patch_count, "prescription_non_patch": rx_count, "non_patch_all_prescription": True}, "outputs": sorted([path.name for path in OUT.iterdir()] + [zip_name])}
    (OUT / "processing_state.json").write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zip_path = OUT / zip_name
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(OUT.iterdir()):
            if path != zip_path:
                archive.write(path, path.name)
    print(f"Built {OUT.relative_to(ROOT)}: 577 products, {len(material_rows)} material rows, {len(clusters)} clusters.")


if __name__ == "__main__":
    main()
