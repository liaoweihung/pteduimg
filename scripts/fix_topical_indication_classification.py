import csv
import itertools
import json
import math
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path
from xml.sax.saxutils import escape


ROOT = Path(__file__).resolve().parents[1]
SOURCE_HTML = ROOT / "ingredient-explorer.html"
DATE_SUFFIX = "20260710"


def extract_explorer_data(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    marker = "window.EXPLORER_DATA="
    start = text.index(marker) + len(marker)
    brace = 0
    in_string = False
    escaped = False
    end = None
    for idx, char in enumerate(text[start:], start):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
        else:
            if char == '"':
                in_string = True
            elif char == "{":
                brace += 1
            elif char == "}":
                brace -= 1
                if brace == 0:
                    end = idx + 1
                    break
    if end is None:
        raise ValueError("Could not locate EXPLORER_DATA JSON object")
    return json.loads(text[start:end]), text, start, end


def split_summary(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("；") if part.strip()]


def unique(items: list[str]) -> list[str]:
    out = []
    for item in items:
        if item and item not in out:
            out.append(item)
    return out


def has_any(text: str, terms: list[str]) -> bool:
    lower = text.lower()
    return any(term.lower() in lower for term in terms)


def has_herpes(text: str) -> bool:
    lower = text.lower()
    if "herpes" in lower or "herpetic" in lower:
        return True
    # Avoid treating 膿疱疹/膿庖疹 as herpes. Those are infection/pustular contexts.
    return bool(re.search(r"(?<!膿)(疱疹|皰疹|泡疹|庖疹)", text))


HERPES_TERMS = ["疱疹", "皰疹", "泡疹", "庖疹", "herpes", "herpetic"]
RING_HERPES_TERMS = ["環狀疱疹", "環狀皰疹", "環狀泡疹", "環狀庖疹"]
BACTERIAL_TERMS = ["細菌", "化膿", "膿皮症", "膿痂疹", "bacterial", "pyoderma", "impetigo"]
WART_TERMS = ["疣", "尋常疣", "病毒疣", "wart", "verruca"]
GENITAL_WART_TERMS = ["生殖器", "外陰", "陰部", "肛門", "肛周", "尖圭濕疣", "尖形濕疣", "尖性濕疣", "genital", "anogenital", "condyloma", "condylomata"]
FUNGAL_TERMS = ["黴菌", "念珠菌", "白癬", "足癬", "股癬", "體癬", "頭癬", "皮癬菌", "tinea", "dermatophyte", "fungal infection", "candida", "candidiasis"]
CORN_TERMS = ["雞眼", "胼胝", "硬皮", "角質增厚", "corn", "callus", "hyperkeratosis"]
PSORIASIS_TERMS = ["牛皮癬", "乾癬", "psoriasis"]
LICHEN_TERMS = ["扁平苔癬", "lichen planus"]
CUT_TERMS = ["刀傷"]

BACTERIAL_LABELS = {"細菌感染", "抗菌", "bacterial infection"}
FUNGAL_LABELS = {"黴菌感染", "香港腳／股癬／體癬／黴菌感染"}
CORN_LABELS = {"雞眼", "角質／雞眼"}
VIRAL_HERPES_LABELS = {"疱疹／病毒感染"}
REMOVED_LABELS = CORN_LABELS | VIRAL_HERPES_LABELS

CATEGORY_MAP = {
    "病毒感染": "病毒感染／抗病毒相關",
    "抗病毒相關": "病毒感染／抗病毒相關",
    "病毒疣": "病毒疣外用治療",
    "生殖器疣": "生殖器疣外用治療",
    "黴菌感染": "香港腳／股癬／體癬／黴菌感染",
    "自體免疫／免疫發炎相關皮膚疾病": "自體免疫／免疫發炎相關皮膚疾病",
    "乾癬／牛皮癬": "乾癬／牛皮癬",
    "扁平苔癬": "扁平苔癬",
    "細菌感染": "細菌感染／膿皰／傷口感染",
    "膿皰": "細菌感染／膿皰／傷口感染",
    "傷口": "燙傷／傷口照護",
    "刀傷": "刀傷外用藥",
    "燙傷": "燙傷／傷口照護",
    "青春痘": "青春痘外用藥",
    "皮膚炎": "濕疹／皮膚炎",
    "濕疹": "濕疹／皮膚炎",
    "異位性皮膚炎": "異位性皮膚炎",
    "搔癢": "蕁麻疹／搔癢",
    "痔瘡": "痔瘡外用藥",
    "消炎止痛": "疼痛／消炎止痛外用藥",
}


def categorize(summary: list[str]) -> str:
    cats = unique(CATEGORY_MAP.get(item, "") for item in summary)
    return "；".join(cats) if cats else "其他常見皮膚外用藥"


def fix_product(product: dict) -> tuple[dict, list[str]]:
    fixed = dict(product)
    text = fixed.get("fullIndication", "") or ""
    original_summary = split_summary(fixed.get("indicationSummary", ""))
    summary = list(original_summary)
    notes = []

    is_psoriasis = has_any(text, PSORIASIS_TERMS)
    is_lichen = has_any(text, LICHEN_TERMS)
    is_ring_herpes = has_any(text, RING_HERPES_TERMS)
    is_herpes = has_herpes(text) and not is_ring_herpes
    has_bacterial = has_any(text, BACTERIAL_TERMS)
    is_wart = has_any(text, WART_TERMS)
    is_genital_wart = is_wart and has_any(text, GENITAL_WART_TERMS)
    is_fungal = (is_ring_herpes or has_any(text, FUNGAL_TERMS)) and not (is_psoriasis or is_lichen)
    is_corn = has_any(text, CORN_TERMS)
    is_cut = has_any(text, CUT_TERMS)

    if not has_bacterial:
        summary = [s for s in summary if s not in BACTERIAL_LABELS]

    if is_psoriasis:
        summary = [s for s in summary if s not in FUNGAL_LABELS]
        summary.extend(["自體免疫／免疫發炎相關皮膚疾病", "乾癬／牛皮癬"])
        notes.append("依完整適應症判斷為乾癬／牛皮癬，已排除黴菌感染分類。")

    if is_lichen:
        summary = [s for s in summary if s not in FUNGAL_LABELS]
        summary.extend(["自體免疫／免疫發炎相關皮膚疾病", "扁平苔癬"])
        notes.append("依完整適應症判斷為扁平苔癬，已排除黴菌感染分類。")

    if is_herpes:
        summary.extend(["病毒感染", "抗病毒相關"])
        notes.append("依完整適應症判斷為疱疹／皰疹相關病毒感染。")

    if is_ring_herpes:
        summary = [s for s in summary if s not in VIRAL_HERPES_LABELS]
        summary.append("黴菌感染")
        notes.append("依完整適應症判斷為環狀疱疹，歸入黴菌感染，不列為疱疹病毒感染。")

    if is_genital_wart:
        summary = [s for s in summary if s not in CORN_LABELS and s not in FUNGAL_LABELS and s != "病毒疣"]
        summary.append("生殖器疣")
        notes.append("依完整適應症判斷為生殖器相關疣，獨立列為生殖器疣。")
    elif is_wart:
        summary = [s for s in summary if s not in CORN_LABELS and s not in FUNGAL_LABELS]
        summary.append("病毒疣")
        notes.append("依完整適應症判斷為疣／病毒疣，不列為雞眼或黴菌感染。")
    elif is_fungal:
        summary = [s for s in summary if s not in CORN_LABELS]
        summary.append("黴菌感染")
        notes.append("依完整適應症明確含感染性癬類或黴菌感染。")
    elif is_corn:
        summary = [s for s in summary if s not in FUNGAL_LABELS]
        summary.append("待人工確認")
        notes.append("角質／雞眼分類已停用；含雞眼／胼胝／角質增厚文字者改列待人工確認。")

    if is_cut:
        summary.append("刀傷")
        notes.append("完整適應症含刀傷，獨立列為刀傷類別。")

    ambiguous_corn = is_corn and (is_wart or is_fungal)
    if ambiguous_corn:
        summary.append("待人工確認")
        notes.append("雞眼相關文字同時出現多個可能分類，需人工確認。")

    summary = unique(s for s in summary if s not in REMOVED_LABELS)
    fixed["indicationSummary"] = "；".join(summary) if summary else "待人工確認"
    fixed["useCategory"] = categorize(summary)
    if notes:
        old_notes = fixed.get("notes", "")
        fixed["notes"] = "；".join(unique([old_notes] + notes if old_notes else notes))
    return fixed, notes


def representative(product: dict) -> dict:
    return {
        "name": product.get("name", ""),
        "englishName": product.get("englishName", ""),
        "license": product.get("license", ""),
        "dosageForm": product.get("dosageForm", ""),
        "drugClass": product.get("drugClass", ""),
        "indicationSummary": product.get("indicationSummary", ""),
        "useCategory": product.get("useCategory", ""),
        "isValid": product.get("isValid", ""),
    }


def score(count: int, total: int) -> float:
    return round(count / total, 4) if total else 0.0


def rebuild_data(data: dict, products: dict) -> dict:
    out = dict(data)
    out["products"] = products
    out["metadata"] = dict(data.get("metadata", {}))
    out["metadata"]["version"] = f"{data.get('metadata', {}).get('version', 'v2')}_classification_fix_{DATE_SUFFIX}"

    ingredient_products = defaultdict(list)
    indication_products = defaultdict(list)
    class_products = defaultdict(list)
    for license_id, product in products.items():
        for ing in product.get("ingredients", []):
            ingredient_products[ing].append(product)
        for ind in split_summary(product.get("indicationSummary", "")):
            indication_products[ind].append(product)
        for ing in product.get("ingredients", []):
            # filled after ingredient class lookup is created
            pass

    old_ingredients = {item["ingredient"]: item for item in data.get("ingredients", [])}
    ingredient_class = {name: item.get("ingredientClass", "") for name, item in old_ingredients.items()}
    ingredient_display = {name: item.get("classDisplay", "") for name, item in old_ingredients.items()}

    for product in products.values():
        for ing in product.get("ingredients", []):
            class_products[ingredient_class.get(ing, "其他")].append(product)

    rebuilt_ingredients = []
    all_indications = sorted(indication_products, key=lambda x: (-len(indication_products[x]), x))
    for ing, plist in sorted(ingredient_products.items(), key=lambda item: (-len(item[1]), item[0])):
        old = old_ingredients.get(ing, {})
        ind_counts = Counter(ind for p in plist for ind in split_summary(p.get("indicationSummary", "")))
        co_counts = Counter(other for p in plist for other in p.get("ingredients", []) if other != ing)
        top = [{"name": k, "score": score(v, len(plist))} for k, v in ind_counts.most_common(8)]
        related = [{"name": k, "score": score(v, len(plist))} for k, v in ind_counts.most_common(8) if v > 0]
        co = [{"ingredient": k, "count": v, "ratio": score(v, len(plist))} for k, v in co_counts.most_common(12)]
        top_names = "、".join(k for k, _ in ind_counts.most_common(3)) or "待人工確認"
        rebuilt_ingredients.append({
            **old,
            "ingredient": ing,
            "productCount": len(plist),
            "topIndications": top,
            "relatedIndications": related,
            "coOccurringIngredients": co,
            "representativeProducts": [representative(p) for p in plist[:10]],
            "summary": f"此成分在資料中主要與{top_names}相關。",
        })
    out["ingredients"] = rebuilt_ingredients

    rebuilt_indications = []
    for ind in all_indications:
        plist = indication_products[ind]
        ing_counts = Counter(ing for p in plist for ing in p.get("ingredients", []))
        class_counts = Counter(ingredient_class.get(ing, "其他") for ing in ing_counts)
        common_ingredients = []
        for ing, count in ing_counts.most_common(12):
            common_ingredients.append({
                "ingredient": ing,
                "ingredientClass": ingredient_class.get(ing, ""),
                "classDisplay": ingredient_display.get(ing, ""),
                "count": count,
                "associationScore": score(count, len(plist)),
                "breadthScore": old_ingredients.get(ing, {}).get("breadthScore", 0),
                "archetype": old_ingredients.get(ing, {}).get("archetype", ""),
            })
        rebuilt_indications.append({
            "name": ind,
            "displayName": ind,
            "canonicalIndications": [ind],
            "aliases": [ind],
            "productCount": len(plist),
            "commonIngredients": common_ingredients,
            "commonClasses": [{"ingredientClass": k, "count": v, "ratio": score(v, len(plist))} for k, v in class_counts.most_common(10)],
            "productLicenses": [p.get("license", "") for p in plist],
            "summary": f"{ind} 相關產品共 {len(plist)} 項。",
        })
    out["indications"] = rebuilt_indications
    out["metadata"]["ingredientCount"] = len(rebuilt_ingredients)
    out["metadata"]["productCount"] = len(products)
    out["metadata"]["indicationCount"] = len(rebuilt_indications)
    return out


def write_csv(path: Path, rows: list[dict], columns: list[str]):
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def output_tables(data: dict):
    products = list(data["products"].values())
    product_columns = [
        "商品名", "英文品名", "許可證字號", "藥品分類", "劑型", "規格", "主要成分",
        "適應症摘要", "推定用途分類", "適應症完整原文", "持有廠商", "是否有效", "備註", "資料來源",
    ]
    product_rows = [
        {
            "商品名": p.get("name", ""),
            "英文品名": p.get("englishName", ""),
            "許可證字號": p.get("license", ""),
            "藥品分類": p.get("drugClass", ""),
            "劑型": p.get("dosageForm", ""),
            "規格": p.get("spec", ""),
            "主要成分": "；".join(p.get("ingredients", [])),
            "適應症摘要": p.get("indicationSummary", ""),
            "推定用途分類": p.get("useCategory", ""),
            "適應症完整原文": p.get("fullIndication", ""),
            "持有廠商": p.get("holder", ""),
            "是否有效": p.get("isValid", ""),
            "備註": p.get("notes", ""),
            "資料來源": p.get("sources", ""),
        }
        for p in products
    ]
    write_csv(ROOT / f"topical_meds_tw_raw_{DATE_SUFFIX}.csv", product_rows, product_columns)
    write_csv(ROOT / f"product_profiles_{DATE_SUFFIX}.csv", product_rows, product_columns)

    indications = [item["name"] for item in data["indications"]]
    ingredients = [item["ingredient"] for item in data["ingredients"]]
    by_ing = defaultdict(list)
    by_ind = defaultdict(list)
    for p in products:
        for ing in p.get("ingredients", []):
            by_ing[ing].append(p)
        for ind in split_summary(p.get("indicationSummary", "")):
            by_ind[ind].append(p)

    matrix_rows = []
    for ing in ingredients:
        row = {"Ingredient": ing, "Product Count": len(by_ing[ing])}
        ing_licenses = {p.get("license", "") for p in by_ing[ing]}
        for ind in indications:
            row[ind] = sum(1 for p in by_ind[ind] if p.get("license", "") in ing_licenses)
        matrix_rows.append(row)
    write_csv(ROOT / f"ingredient_indication_matrix_{DATE_SUFFIX}.csv", matrix_rows, ["Ingredient", "Product Count"] + indications)

    ing_rows = []
    for item in data["ingredients"]:
        ing_rows.append({
            "Ingredient": item.get("ingredient", ""),
            "Ingredient Class": item.get("ingredientClass", ""),
            "Class Display": item.get("classDisplay", ""),
            "Product Count": item.get("productCount", 0),
            "Top Indications": "；".join(f"{x['name']}({x['score']})" for x in item.get("topIndications", [])),
            "Related Indications": "；".join(f"{x['name']}({x['score']})" for x in item.get("relatedIndications", [])),
            "Co-occurring Ingredients": "；".join(f"{x['ingredient']}({x['count']})" for x in item.get("coOccurringIngredients", [])),
            "Representative Products": "；".join(p.get("name", "") for p in item.get("representativeProducts", [])),
            "Summary": item.get("summary", ""),
        })
    write_csv(ROOT / f"ingredient_profiles_{DATE_SUFFIX}.csv", ing_rows, [
        "Ingredient", "Ingredient Class", "Class Display", "Product Count", "Top Indications",
        "Related Indications", "Co-occurring Ingredients", "Representative Products", "Summary",
    ])

    ind_rows = []
    for item in data["indications"]:
        ind_rows.append({
            "Indication": item.get("name", ""),
            "Product Count": item.get("productCount", 0),
            "Common Ingredients": "；".join(f"{x['ingredient']}({x['count']})" for x in item.get("commonIngredients", [])),
            "Common Classes": "；".join(f"{x['ingredientClass']}({x['count']})" for x in item.get("commonClasses", [])),
            "Product Licenses": "；".join(item.get("productLicenses", [])),
            "Summary": item.get("summary", ""),
        })
    write_csv(ROOT / f"indication_profiles_{DATE_SUFFIX}.csv", ind_rows, [
        "Indication", "Product Count", "Common Ingredients", "Common Classes", "Product Licenses", "Summary",
    ])


def write_xlsx(csv_path: Path, xlsx_path: Path):
    rows = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        for row in csv.reader(f):
            rows.append(row)
    sheet_xml = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">',
                 '<sheetData>']
    for r_idx, row in enumerate(rows, 1):
        sheet_xml.append(f'<row r="{r_idx}">')
        for c_idx, value in enumerate(row, 1):
            col = ""
            n = c_idx
            while n:
                n, rem = divmod(n - 1, 26)
                col = chr(65 + rem) + col
            ref = f"{col}{r_idx}"
            sheet_xml.append(f'<c r="{ref}" t="inlineStr"><is><t>{escape(value)}</t></is></c>')
        sheet_xml.append("</row>")
    sheet_xml.append("</sheetData></worksheet>")
    files = {
        "[Content_Types].xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/><Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>''',
        "_rels/.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>''',
        "xl/workbook.xml": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Raw Database" sheetId="1" r:id="rId1"/></sheets></workbook>''',
        "xl/_rels/workbook.xml.rels": '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/></Relationships>''',
        "xl/worksheets/sheet1.xml": "".join(sheet_xml),
    }
    with zipfile.ZipFile(xlsx_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, content in files.items():
            zf.writestr(name, content)


def update_html(original_text: str, start: int, end: int, data: dict):
    raw = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    out = original_text[:start] + raw + original_text[end:]
    (ROOT / f"ingredient_explorer_{DATE_SUFFIX}.html").write_text(out, encoding="utf-8")


def main():
    data, html_text, json_start, json_end = extract_explorer_data(SOURCE_HTML)
    products = {}
    changed = []
    for key, product in data["products"].items():
        fixed, notes = fix_product(product)
        products[key] = fixed
        if fixed.get("indicationSummary") != product.get("indicationSummary") or fixed.get("useCategory") != product.get("useCategory"):
            changed.append({
                "license": fixed.get("license", key),
                "name": fixed.get("name", ""),
                "from": product.get("indicationSummary", ""),
                "to": fixed.get("indicationSummary", ""),
                "useCategory": fixed.get("useCategory", ""),
                "notes": "；".join(notes),
            })
    rebuilt = rebuild_data(data, products)
    (ROOT / f"ingredient_explorer_data_{DATE_SUFFIX}.json").write_text(
        json.dumps(rebuilt, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    output_tables(rebuilt)
    write_xlsx(ROOT / f"topical_meds_tw_raw_{DATE_SUFFIX}.csv", ROOT / f"topical_meds_tw_{DATE_SUFFIX}.xlsx")
    update_html(html_text, json_start, json_end, rebuilt)
    print(json.dumps({
        "products": len(products),
        "changedProducts": len(changed),
        "indications": len(rebuilt["indications"]),
        "ingredients": len(rebuilt["ingredients"]),
        "examples": changed[:12],
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
