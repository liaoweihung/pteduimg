#!/usr/bin/env python3
"""Build the compact TCM external patch and prescription topical dataset.

This script deliberately uses only the checked-in tcm_formula_explorer source
files.  It does not fetch or enrich data from the network.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "data" / "tcm_formula_explorer"
OUTPUT = ROOT / "data" / "tcm_external_patch_rx_20260730.json"
REPORT = ROOT / "data_quality_report_tcm_external_patch_rx.md"
README = ROOT / "README_tcm_external_patch_rx.md"
PATCH_FORM = "藥膠布劑"
RX_CLASS = "須由中醫師處方使用"
RX_FORMS = {"油膏劑", "外用粉劑", "軟膏劑", "硬膏劑"}
DISCLAIMER = "母方與加減藥材為既有組成相似度推測，不是歷史源流、製造商聲明或確定處方來源。"


def require_sources() -> list[Path]:
    paths = [SOURCE_DIR / "index.json", SOURCE_DIR / "formulas.json"]
    paths.extend(SOURCE_DIR / f"products-{index:02d}.json" for index in range(32))
    missing = [str(path.relative_to(ROOT)) for path in paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing required source files:\n" + "\n".join(missing))
    return paths


def split_name(value: str) -> tuple[str, str]:
    lines = [line.strip() for line in str(value or "").splitlines() if line.strip()]
    return (lines[0] if lines else "", " ".join(lines[1:]))


def load_rows() -> tuple[list[dict], dict]:
    require_sources()
    formulas = json.loads((SOURCE_DIR / "formulas.json").read_text(encoding="utf-8")).get("formulas", {})
    rows: list[dict] = []
    for index in range(32):
        path = SOURCE_DIR / f"products-{index:02d}.json"
        rows.extend(json.loads(path.read_text(encoding="utf-8")).get("products", []))
    return rows, formulas


def compact_product(product: dict, formulas: dict, group: str) -> dict:
    reliable = product.get("status") == "inferred_candidate_available" and bool(product.get("formulaId"))
    formula = formulas.get(product.get("formulaId"), {}) if reliable else {}
    zh_name, en_name = split_name(product.get("name", ""))
    warnings = [DISCLAIMER]
    if product.get("cautions"):
        warnings.append(product["cautions"])
    if not reliable:
        warnings.append("尚無可靠母方候選；未強行配對。")
    return {
        "group": group,
        "is_prescription_product": group == "處方外用藥",
        "license": product.get("license", ""),
        "name_zh": zh_name,
        "name_en": en_name,
        "dosage_form": product.get("form", ""),
        "regulatory_classification": product.get("class", ""),
        "license_status": product.get("licenseStatus", ""),
        "official_indications": product.get("indications", ""),
        "official_prescription": product.get("prescription", ""),
        "inferred_parent": {
            "name": product.get("formula", "") if reliable else "尚無可靠母方候選",
            "source": formula.get("source", "") if reliable else "",
            "original_prescription": formula.get("prescription", "") if reliable else "",
            "ingredients": formula.get("ingredients", "") if reliable else "",
            "relationship": product.get("relationship", "") if reliable else "",
        },
        "inferred_added_herbs": product.get("added", "") if reliable else "",
        "inferred_removed_herbs": product.get("removed", "") if reliable else "",
        "specification_difference": product.get("specDiff", "") if reliable else "",
        "inference_confidence": product.get("confidence", "") if reliable else "",
        "inference_basis": product.get("basis", "") if reliable else "",
        "warnings": warnings,
        "data_source": product.get("sourceUrl", ""),
    }


def main() -> None:
    rows, formulas = load_rows()
    patches = [row for row in rows if row.get("form") == PATCH_FORM]
    prescription_topicals = [
        row for row in rows
        if row.get("class") == RX_CLASS and row.get("form") in RX_FORMS
    ]
    if len(patches) != 564 or len(prescription_topicals) != 13:
        raise ValueError(f"Selection validation failed: patches={len(patches)}, prescription_topicals={len(prescription_topicals)}")
    products = [compact_product(row, formulas, "中藥外用貼布") for row in patches]
    products.extend(compact_product(row, formulas, "處方外用藥") for row in prescription_topicals)
    if len(products) != 577 or any(item["is_prescription_product"] and item["regulatory_classification"] != RX_CLASS for item in products):
        raise ValueError("Final validation failed: product count or prescription classification is invalid")
    payload = {
        "metadata": {
            "dataset": "中藥外用貼布與處方外用藥",
            "built_from": ["data/tcm_formula_explorer/index.json", "data/tcm_formula_explorer/formulas.json", "data/tcm_formula_explorer/products-00.json ～ products-31.json"],
            "selection_rule": "藥膠布劑全部產品，加上須由中醫師處方使用且劑型為油膏劑、外用粉劑、軟膏劑或硬膏劑的產品。",
            "disclaimer": DISCLAIMER,
            "counts": {"total": 577, "patch": 564, "prescription_topical": 13},
        },
        "products": products,
    }
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rx_forms = Counter(item["dosage_form"] for item in products if item["is_prescription_product"])
    REPORT.write_text(
        "# 中藥外用貼布與處方外用藥資料品質報告\n\n"
        "- 來源：既有 `data/tcm_formula_explorer/` 的索引、母方表與 32 個產品分檔；未重新抓取官方資料。\n"
        "- 藥膠布劑：564 筆。\n"
        "- 處方外用藥：13 筆。\n"
        "- 總計：577 筆。\n"
        "- 處方外用藥劑型：" + "、".join(f"{name} {count} 筆" for name, count in sorted(rx_forms.items())) + "。\n"
        "- 驗證：13 筆均保留法規分類「須由中醫師處方使用」，不會標示為成藥或 OTC。\n"
        "- 母方與加減藥材僅沿用既有組成相似度推測；無可靠候選者一律標示「尚無可靠母方候選」。\n",
        encoding="utf-8",
    )
    README.write_text(
        "# 中藥外用貼布與處方外用藥資料集\n\n"
        "本資料集只從專案既有的中成藥資料分檔重建，供 `tcm_external_patch_explorer.html` 使用。\n\n"
        "```powershell\npython scripts/build_tcm_external_patch_rx.py\n```\n\n"
        "輸出固定為 577 筆：564 筆藥膠布劑與 13 筆須由中醫師處方使用的外用產品（油膏劑、外用粉劑、軟膏劑、硬膏劑）。\n\n"
        + DISCLAIMER + "\n",
        encoding="utf-8",
    )
    print("Built 577 products: 564 patches + 13 prescription topicals.")


if __name__ == "__main__":
    main()
