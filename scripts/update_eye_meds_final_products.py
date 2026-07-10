import csv
import html
import itertools
import json
import re
import shutil
from collections import Counter, defaultdict
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
SOURCE_DIR = Path(r"C:\Users\liaow\Documents\Codex\2026-07-08\task-1-1-tfda-2-tfda\work\source_data")
LICENSE_FILE = SOURCE_DIR / "tfda_info_37_active_drug_licenses.json"
LEAFLET_FILE = SOURCE_DIR / "tfda_info_39_drug_leaflet_package_links.json"
INGREDIENT_FILE = SOURCE_DIR / "tfda_info_43_eye_candidate_ingredients.json"

RAW_CSV = REPO / "eye_meds_tw_raw.csv"
EXCLUDED_CSV = REPO / "excluded_eye_products.csv"
TABLES_JSON = REPO / "eye_meds_tables.json"

LICENSE_QUERY_URL = "https://lmspiq.fda.gov.tw/web/DRPIQ/DRPIQ"

INCLUDE_KEYWORDS = [
    "眼", "點眼", "眼藥水", "眼用", "眼科", "結膜炎", "角膜炎", "角膜潰瘍",
    "角膜損傷", "乾眼", "眼睛乾澀", "眼睛疲勞", "眼睛癢", "眼睛紅", "過敏性結膜炎",
    "感染性結膜炎", "麥粒腫", "青光眼", "白內障術後", "散瞳", "睫狀肌麻痺",
    "ophthalmic", "eye drop", "eye drops", "conjunctivitis", "keratitis",
    "dry eye", "allergic conjunctivitis", "glaucoma", "mydriatic", "ocular",
]

FINAL_DOSAGE_KEYWORDS = [
    "眼藥水", "點眼液", "點眼懸液", "眼用液", "眼用懸液", "眼用凝膠", "眼用軟膏",
    "點眼", "眼膏", "眼耳鼻用液", "ophthalmic solution", "ophthalmic suspension",
    "eye drops", "eye drop", "ophthalmic gel", "ophthalmic ointment",
]

RAW_MATERIAL_KEYWORDS = [
    "原料藥", "藥品原料", "原料", "中間體", "製劑用原料", "非最終銷售製劑",
    "active pharmaceutical ingredient", " api ", "bulk drug substance",
    "drug substance", "bulk", "intermediate", "for formulation",
]

NON_EYE_EXCLUDE_PATTERNS = [
    ("口服或非眼科固體劑型", r"錠|膠囊|口服|內服|咀嚼|膜衣|口溶|顆粒|散劑"),
    ("注射劑", r"注射|針劑|輸注|靜脈|肌肉注射"),
    ("耳鼻用製劑", r"耳滴|耳用|鼻噴|鼻用|鼻滴"),
    ("皮膚外用但非眼科", r"皮膚|乳膏|軟膏(?!.*眼)|凝膠(?!.*眼)|外用液"),
    ("醫療器材或隱形眼鏡保養相關描述", r"隱形眼鏡|保養液|沖洗液|醫療器材"),
]

MAIN_COLUMNS = [
    "商品名", "英文品名", "許可證字號", "許可證持有廠商", "是否有效",
    "藥品分類", "分類依據", "是否中藥", "劑型", "規格", "包裝",
    "適應症完整原文", "適應症摘要", "推定用途分類", "全部成分原文", "主要成分",
    "防腐劑成分，若有", "是否含防腐劑", "是否為複方", "資料來源", "備註",
]

EXCLUDED_COLUMNS = [
    "商品名", "英文品名", "許可證字號", "許可證種類", "劑型", "規格", "包裝",
    "適應症", "排除原因", "命中關鍵字",
]

COMPARE_PREFIX = [
    "商品名", "英文品名", "許可證字號", "藥品分類", "分類依據", "推定用途分類",
    "劑型", "規格", "是否含防腐劑", "防腐劑成分，若有",
]

COMPARE_SUFFIX = ["適應症摘要", "適應症完整原文", "全部成分原文", "備註"]

PRESERVATIVES = {
    "BENZALKONIUM CHLORIDE": "Benzalkonium chloride",
    "CHLOROBUTANOL": "Chlorobutanol",
    "THIMEROSAL": "Thimerosal",
    "THIOMERSAL": "Thimerosal",
    "BENZODODECINIUM BROMIDE": "Benzododecinium bromide",
    "POLYQUATERNIUM-1": "Polyquaternium-1",
    "POLYQUAD": "Polyquaternium-1",
    "STABILIZED OXYCHLORO COMPLEX": "Stabilized oxychloro complex",
    "SODIUM CHLORITE": "Stabilized oxychloro complex",
}

STANDARD_COMPONENTS = {
    "SODIUM HYALURONATE": "Sodium hyaluronate",
    "HYALURONATE SODIUM": "Sodium hyaluronate",
    "CARBOXYMETHYLCELLULOSE": "Carboxymethylcellulose",
    "CARMELLOSE": "Carboxymethylcellulose",
    "HPMC": "Hypromellose",
    "HYDROXYPROPYL METHYLCELLULOSE": "Hypromellose",
    "HYPROMELLOSE": "Hypromellose",
    "POLYVINYL ALCOHOL": "Polyvinyl alcohol",
    "POVIDONE": "Povidone",
    "CARBOMER": "Carbomer",
    "POLYETHYLENE GLYCOL": "Polyethylene glycol",
    "PROPYLENE GLYCOL": "Propylene glycol",
    "TREHALOSE": "Trehalose",
    "OLOPATADINE": "Olopatadine",
    "KETOTIFEN": "Ketotifen",
    "LEVOCABASTINE": "Levocabastine",
    "EMEDASTINE": "Emedastine",
    "CROMOLYN": "Cromolyn sodium",
    "CROMOGLICATE": "Sodium cromoglicate",
    "NAPHAZOLINE": "Naphazoline",
    "TETRAHYDROZOLINE": "Tetrahydrozoline",
    "PHENYLEPHRINE": "Phenylephrine",
    "CHLORAMPHENICOL": "Chloramphenicol",
    "GENTAMICIN": "Gentamicin",
    "TOBRAMYCIN": "Tobramycin",
    "OFLOXACIN": "Ofloxacin",
    "LEVOFLOXACIN": "Levofloxacin",
    "MOXIFLOXACIN": "Moxifloxacin",
    "FUSIDIC": "Fusidic acid",
    "SULFACETAMIDE": "Sulfacetamide",
    "FLUOROMETHOLONE": "Fluorometholone",
    "DEXAMETHASONE": "Dexamethasone",
    "PREDNISOLONE": "Prednisolone",
    "LOTEPREDNOL": "Loteprednol",
    "BETAMETHASONE": "Betamethasone",
    "DICLOFENAC": "Diclofenac",
    "KETOROLAC": "Ketorolac",
    "BROMFENAC": "Bromfenac",
    "NEPAFENAC": "Nepafenac",
    "TIMOLOL": "Timolol",
    "BETAXOLOL": "Betaxolol",
    "BRIMONIDINE": "Brimonidine",
    "DORZOLAMIDE": "Dorzolamide",
    "BRINZOLAMIDE": "Brinzolamide",
    "LATANOPROST": "Latanoprost",
    "TRAVOPROST": "Travoprost",
    "BIMATOPROST": "Bimatoprost",
    "TAFLUPROST": "Tafluprost",
    "TROPICAMIDE": "Tropicamide",
    "CYCLOPENTOLATE": "Cyclopentolate",
    "ATROPINE": "Atropine",
    "CHONDROITIN": "Chondroitin sulfate",
    "FLAVIN ADENINE DINUCLEOTIDE": "Flavin adenine dinucleotide",
    "SODIUM CHLORIDE": "Sodium chloride",
    "VITAMIN A": "Vitamin A",
    "RETINOL": "Vitamin A",
    "DEXPANTHENOL": "Dexpanthenol",
    **PRESERVATIVES,
}

INDICATION_SUMMARY_RULES = [
    ("乾眼", ["乾眼", "乾性角結膜炎", "dry eye"]),
    ("眼睛乾澀", ["乾澀", "眼乾"]),
    ("眼睛疲勞", ["疲勞", "眼精疲勞", "調節"]),
    ("過敏性結膜炎", ["過敏性結膜炎", "allergic conjunctivitis"]),
    ("眼睛癢", ["搔癢", "眼睛癢", "癢"]),
    ("眼睛紅", ["充血", "眼睛紅", "紅眼"]),
    ("結膜炎", ["結膜炎", "conjunctivitis"]),
    ("角膜炎", ["角膜炎", "keratitis"]),
    ("角膜潰瘍", ["角膜潰瘍"]),
    ("麥粒腫", ["麥粒腫", "針眼"]),
    ("術後發炎", ["術後", "手術後", "白內障術後"]),
    ("青光眼", ["青光眼", "glaucoma"]),
    ("降眼壓", ["眼壓", "降眼壓"]),
    ("散瞳", ["散瞳", "mydri"]),
    ("睫狀肌麻痺", ["睫狀肌麻痺", "cyclople"]),
    ("角膜修復", ["角膜損傷", "角膜修復", "上皮"]),
    ("抗病毒", ["病毒", "herpes", "acyclovir"]),
    ("抗菌", ["感染", "細菌", "抗菌", "抗生素"]),
    ("消炎", ["發炎", "炎症", "消炎"]),
    ("潤滑保濕", ["潤滑", "保濕", "人工淚液", "淚液"]),
]

COMPONENT_CATEGORY_RULES = [
    ("人工淚液／潤滑型", ["Sodium hyaluronate", "Carboxymethylcellulose", "Hypromellose", "Polyvinyl alcohol", "Povidone", "Carbomer", "Polyethylene glycol", "Propylene glycol", "Trehalose"]),
    ("抗過敏型", ["Olopatadine", "Ketotifen", "Levocabastine", "Emedastine", "Cromolyn sodium", "Sodium cromoglicate"]),
    ("退紅／血管收縮型", ["Naphazoline", "Tetrahydrozoline", "Phenylephrine"]),
    ("抗菌型", ["Chloramphenicol", "Gentamicin", "Tobramycin", "Ofloxacin", "Levofloxacin", "Moxifloxacin", "Fusidic acid", "Sulfacetamide"]),
    ("類固醇消炎型", ["Fluorometholone", "Dexamethasone", "Prednisolone", "Loteprednol", "Betamethasone"]),
    ("NSAID 消炎型", ["Diclofenac", "Ketorolac", "Bromfenac", "Nepafenac"]),
    ("青光眼用藥", ["Timolol", "Betaxolol", "Brimonidine", "Dorzolamide", "Brinzolamide", "Latanoprost", "Travoprost", "Bimatoprost", "Tafluprost"]),
    ("散瞳／睫狀肌麻痺", ["Tropicamide", "Cyclopentolate", "Atropine", "Phenylephrine"]),
    ("角膜修復／促進上皮修復", ["Chondroitin sulfate", "Flavin adenine dinucleotide", "Vitamin A", "Dexpanthenol"]),
]

COMPONENT_CATEGORIES = {
    "人工淚液／潤滑成分": ["Sodium hyaluronate", "Carboxymethylcellulose", "Hypromellose", "Hydroxypropyl methylcellulose", "Polyvinyl alcohol", "Povidone", "Carbomer", "Polyethylene glycol", "Propylene glycol", "Trehalose", "Sodium chloride"],
    "抗過敏成分": ["Olopatadine", "Ketotifen", "Levocabastine", "Emedastine", "Cromolyn sodium", "Sodium cromoglicate", "Chlorpheniramine Maleate", "Mequitazine", "Loratadine"],
    "退紅／血管收縮成分": ["Naphazoline", "Tetrahydrozoline", "Phenylephrine"],
    "抗菌成分": ["Chloramphenicol", "Gentamicin", "Tobramycin", "Ofloxacin", "Levofloxacin", "Moxifloxacin", "Fusidic acid", "Sulfacetamide", "Neomycin Sulfate"],
    "類固醇成分": ["Fluorometholone", "Dexamethasone", "Prednisolone", "Loteprednol", "Betamethasone"],
    "NSAID 成分": ["Diclofenac", "Ketorolac", "Bromfenac", "Nepafenac"],
    "青光眼成分": ["Timolol", "Betaxolol", "Brimonidine", "Dorzolamide", "Brinzolamide", "Latanoprost", "Travoprost", "Bimatoprost", "Tafluprost", "Carteolol HCL"],
    "散瞳／睫狀肌麻痺成分": ["Tropicamide", "Cyclopentolate", "Atropine", "Phenylephrine"],
    "角膜修復／其他成分": ["Chondroitin sulfate", "Flavin adenine dinucleotide", "Vitamin A", "Dexpanthenol", "Panthenol"],
    "防腐劑": ["Benzalkonium chloride", "Chlorobutanol", "Thimerosal", "Benzododecinium bromide", "Polyquaternium-1", "Stabilized oxychloro complex"],
}

SYNONYMS = {
    "乾眼": ["乾眼", "眼睛乾澀", "dry eye", "眼乾", "乾澀"],
    "過敏": ["過敏", "過敏性結膜炎", "眼睛癢", "搔癢", "allergic conjunctivitis"],
    "退紅": ["退紅", "眼睛紅", "充血", "紅眼"],
    "抗菌": ["抗菌", "感染", "結膜炎", "角膜炎", "麥粒腫"],
    "青光眼": ["青光眼", "降眼壓", "眼壓", "glaucoma"],
    "散瞳": ["散瞳", "睫狀肌麻痺", "mydriatic", "cycloplegia"],
    "人工淚液": ["人工淚液", "潤滑", "保濕", "眼睛乾澀"],
    "疲勞": ["疲勞", "眼睛疲勞", "調節"],
}


def clean_text(value) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def text_for_screening(row: dict) -> str:
    fields = ["中文品名", "英文品名", "適應症", "劑型", "包裝", "主成分略述", "用法用量", "許可證種類"]
    return " ".join(clean_text(row.get(k)) for k in fields).lower()


def matched_keywords(text: str) -> list[str]:
    return [kw for kw in INCLUDE_KEYWORDS if kw.lower() in text]


def is_raw_material(row: dict) -> bool:
    kind = re.sub(r"\s+", "", clean_text(row.get("許可證種類")).replace("　", ""))
    text = " " + text_for_screening(row) + " "
    if kind and kind != "製劑":
        return True
    return any(keyword.lower() in text for keyword in RAW_MATERIAL_KEYWORDS)


def exclusion_reason(row: dict, text: str, keywords: list[str]) -> str:
    if is_raw_material(row):
        return "原料藥／非最終製劑"
    if not clean_text(row.get("許可證字號")):
        return "缺少明確藥品許可證字號"
    if not (clean_text(row.get("中文品名")) or clean_text(row.get("英文品名"))):
        return "缺少商品名或製劑名稱"
    if not clean_text(row.get("適應症")):
        return "缺少明確適應症"
    dosage_text = " ".join(clean_text(row.get(k)) for k in ["劑型", "中文品名", "英文品名"]).lower()
    if not any(keyword.lower() in dosage_text for keyword in FINAL_DOSAGE_KEYWORDS):
        return "非眼科外用最終劑型"
    for label, pattern in NON_EYE_EXCLUDE_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            if not re.search(r"眼|ophthalmic|eye", text, flags=re.IGNORECASE):
                return label
    return ""


def normalize_component(name: str) -> str:
    text = clean_text(name)
    if not text:
        return ""
    upper = re.sub(r"[^A-Z0-9]+", " ", text.upper()).strip()
    for key, standard in STANDARD_COMPONENTS.items():
        key_norm = re.sub(r"[^A-Z0-9]+", " ", key.upper()).strip()
        if key_norm and key_norm in upper:
            return standard
    return text.title().replace("Hcl", "HCL").replace("Eq To", "EQ TO")


def summarize_indications(text: str) -> list[str]:
    lower = clean_text(text).lower()
    found = []
    for label, terms in INDICATION_SUMMARY_RULES:
        if any(term.lower() in lower for term in terms):
            found.append(label)
    return found


def infer_usage_category(components: list[str], indications: list[str], dosage: str, full_text: str) -> str:
    comp_set = set(components)
    for category, names in COMPONENT_CATEGORY_RULES:
        if any(name in comp_set for name in names):
            return category
    joined = " ".join(indications) + " " + clean_text(dosage) + " " + full_text
    if "藥膏" in joined or "軟膏" in joined or "ointment" in joined.lower():
        return "眼藥膏"
    if "抗病毒" in joined or "病毒" in joined or "acyclovir" in joined.lower():
        return "抗病毒眼藥"
    if "疲勞" in joined or "調節" in joined:
        return "疲勞／調節改善型"
    if "乾" in joined or "人工淚液" in joined or "潤滑" in joined:
        return "人工淚液／潤滑型"
    if len(components) > 1:
        return "複方眼藥"
    return "其他眼科外用藥"


def component_category(component: str) -> str:
    lower = component.lower()
    for category, names in COMPONENT_CATEGORIES.items():
        if any(name.lower() == lower for name in names):
            return category
    for category, names in COMPONENT_CATEGORIES.items():
        if any(name.lower() in lower or lower in name.lower() for name in names):
            return category
    return "其他成分"


def find_preservatives(components: list[str]) -> list[str]:
    found = []
    for component in components:
        upper = component.upper()
        for key, standard in PRESERVATIVES.items():
            if key in upper and standard not in found:
                found.append(standard)
    return found


def classify_drug_type(value) -> tuple[str, str]:
    text = clean_text(value)
    if not text:
        return "待人工確認", "TFDA 藥品類別欄位空白"
    if "處方" in text:
        return "處方藥", text
    if "指示" in text:
        return "指示藥", text
    if "成藥" in text:
        return "成藥", text
    return text, text


def split_semicolon(value: str) -> list[str]:
    return [part.strip() for part in (value or "").split("；") if part.strip()]


def one_line_product(row: dict) -> str:
    return (
        f"{row['商品名']} 屬於 {row['推定用途分類']}，常見用途為 "
        f"{row['適應症摘要'] or '適應症待確認'}，防腐劑狀態為{row['是否含防腐劑']}。"
    )


def write_csv(path: Path, rows: list[dict], columns: list[str]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_primary_database():
    licenses = load_json(LICENSE_FILE)
    leaflet_rows = load_json(LEAFLET_FILE) if LEAFLET_FILE.exists() and LEAFLET_FILE.stat().st_size else []
    leaflet_map = {clean_text(r.get("許可證字號")): r for r in leaflet_rows}
    ingredient_rows = load_json(INGREDIENT_FILE)

    candidate_map = {}
    excluded = []
    for row in licenses:
        text = text_for_screening(row)
        keywords = matched_keywords(text)
        if not keywords:
            continue
        reason = exclusion_reason(row, text, keywords)
        if reason:
            excluded.append({
                "商品名": clean_text(row.get("中文品名")),
                "英文品名": clean_text(row.get("英文品名")),
                "許可證字號": clean_text(row.get("許可證字號")),
                "許可證種類": clean_text(row.get("許可證種類")),
                "劑型": clean_text(row.get("劑型")),
                "規格": clean_text(row.get("主成分略述")),
                "包裝": clean_text(row.get("包裝")),
                "適應症": clean_text(row.get("適應症")),
                "排除原因": reason,
                "命中關鍵字": "；".join(keywords),
            })
            continue
        lic = clean_text(row.get("許可證字號"))
        if lic in candidate_map:
            existing = candidate_map[lic]
            for key in ["包裝", "製造商名稱", "製造廠廠址", "製造廠國別"]:
                old = clean_text(existing.get(key))
                new = clean_text(row.get(key))
                if new and new not in old:
                    existing[key] = "；".join(x for x in [old, new] if x)
        else:
            candidate_map[lic] = dict(row)

    ingredient_map = defaultdict(list)
    for ing in ingredient_rows:
        ingredient_map[clean_text(ing.get("許可證字號"))].append(ing)

    raw_rows = []
    component_presence = Counter()
    product_components = {}
    for row in candidate_map.values():
        lic = clean_text(row.get("許可證字號"))
        ing_rows = ingredient_map.get(lic, [])
        components = []
        ingredient_raw_parts = []
        for ing in ing_rows:
            name = normalize_component(ing.get("成分名稱"))
            if name:
                components.append(name)
            piece = " ".join(clean_text(ing.get(k)) for k in ["處方標示", "成分名稱", "含量描述", "含量", "含量單位"] if clean_text(ing.get(k)))
            if piece:
                ingredient_raw_parts.append(piece)
        components_unique = sorted(set(components), key=components.index)
        for comp in set(components_unique):
            component_presence[comp] += 1
        product_components[lic] = components_unique

        drug_type, drug_basis = classify_drug_type(row.get("藥品類別"))
        indication_full = clean_text(row.get("適應症"))
        indication_summary = summarize_indications(indication_full)
        full_text = text_for_screening(row) + " " + " ".join(components_unique)
        category = infer_usage_category(components_unique, indication_summary, clean_text(row.get("劑型")), full_text)
        preservatives = find_preservatives(components_unique)
        is_preserved = "是" if preservatives else ("待確認" if not components_unique else "否")
        leaflet = leaflet_map.get(lic, {})
        leaflet_links = []
        for key in ["仿單圖檔連結", "外盒圖檔連結"]:
            link = clean_text(leaflet.get(key))
            if link:
                leaflet_links.append(f"{key}:{link}")
        source = "TFDA open data InfoId=37; InfoId=43"
        if leaflet_links:
            source += "; InfoId=39 " + " | ".join(leaflet_links)
        source += f"; 查詢入口:{LICENSE_QUERY_URL}"
        note = "成分資料未列於 TFDA 詳細處方成分檔，需人工確認" if not components_unique else ""
        raw_rows.append({
            "商品名": clean_text(row.get("中文品名")),
            "英文品名": clean_text(row.get("英文品名")),
            "許可證字號": lic,
            "許可證持有廠商": clean_text(row.get("申請商名稱")),
            "是否有效": "是",
            "藥品分類": drug_type,
            "分類依據": drug_basis,
            "是否中藥": "是" if "中藥" in clean_text(row.get("許可證種類")) else "否",
            "劑型": clean_text(row.get("劑型")),
            "規格": clean_text(row.get("主成分略述")),
            "包裝": clean_text(row.get("包裝")),
            "適應症完整原文": indication_full,
            "適應症摘要": "；".join(indication_summary) if indication_summary else "待人工確認",
            "推定用途分類": category,
            "全部成分原文": "；".join(ingredient_raw_parts) if ingredient_raw_parts else clean_text(row.get("主成分略述")),
            "主要成分": "；".join(components_unique) if components_unique else "待人工確認",
            "防腐劑成分，若有": "；".join(preservatives),
            "是否含防腐劑": is_preserved,
            "是否為複方": "是" if len(components_unique) > 1 else ("待確認" if not components_unique else "否"),
            "資料來源": source,
            "備註": note,
        })

    raw_rows.sort(key=lambda r: (r["推定用途分類"], r["商品名"]))
    excluded.sort(key=lambda r: (r["排除原因"], r["商品名"]))

    component_columns = [name for name, _ in component_presence.most_common()]
    compare_rows = []
    for row in raw_rows:
        comps = set(product_components.get(row["許可證字號"], []))
        compare = {k: row.get(k, "") for k in COMPARE_PREFIX + COMPARE_SUFFIX}
        for comp in component_columns:
            compare[comp] = "✓" if comp in comps else ""
        compare_rows.append(compare)

    component_frequency = [
        {
            "成分": comp,
            "產品數": count,
            "占比": round(count / len(raw_rows), 4) if raw_rows else 0,
            "成分類別": component_category(comp),
        }
        for comp, count in component_presence.most_common()
    ]

    category_summary = [{"推定用途分類": k, "產品數": v} for k, v in Counter(r["推定用途分類"] for r in raw_rows).most_common()]
    rx_otc_summary = [{"藥品分類": k, "產品數": v} for k, v in Counter(r["藥品分類"] for r in raw_rows).most_common()]
    preservative_summary = [
        {"是否含防腐劑": k, "產品數": v, "占比": round(v / len(raw_rows), 4) if raw_rows else 0}
        for k, v in Counter(r["是否含防腐劑"] for r in raw_rows).most_common()
    ]

    write_csv(RAW_CSV, raw_rows, MAIN_COLUMNS)
    write_csv(EXCLUDED_CSV, excluded, EXCLUDED_COLUMNS)
    return raw_rows, excluded, {
        "Raw Database": {"columns": MAIN_COLUMNS, "rows": raw_rows},
        "Compare Table": {"columns": COMPARE_PREFIX + component_columns + COMPARE_SUFFIX, "rows": compare_rows},
        "Component Frequency": {"columns": ["成分", "產品數", "占比", "成分類別"], "rows": component_frequency},
        "Category Summary": {"columns": ["推定用途分類", "產品數"], "rows": category_summary},
        "Rx OTC Summary": {"columns": ["藥品分類", "產品數"], "rows": rx_otc_summary},
        "Preservative Summary": {"columns": ["是否含防腐劑", "產品數", "占比"], "rows": preservative_summary},
        "Excluded Products": {"columns": EXCLUDED_COLUMNS, "rows": excluded},
    }


def build_explorer_data(rows: list[dict]):
    products = []
    component_counts = Counter()
    indication_counts = Counter()
    category_counts = Counter()
    dosage_counts = Counter()
    drug_counts = Counter()
    preservative_counts = Counter()

    for idx, row in enumerate(rows):
        components = split_semicolon(row["主要成分"])
        indications = split_semicolon(row["適應症摘要"])
        product = {
            "id": idx,
            "name": row["商品名"],
            "englishName": row["英文品名"],
            "license": row["許可證字號"],
            "holder": row["許可證持有廠商"],
            "valid": row["是否有效"],
            "drugClass": row["藥品分類"],
            "classBasis": row["分類依據"],
            "isTcm": row["是否中藥"],
            "dosageForm": row["劑型"],
            "spec": row["規格"],
            "package": row["包裝"],
            "indicationFull": row["適應症完整原文"],
            "indicationSummary": indications,
            "usageCategory": row["推定用途分類"],
            "ingredientFull": row["全部成分原文"],
            "components": components,
            "preservativeIngredients": split_semicolon(row["防腐劑成分，若有"]),
            "preservativeStatus": row["是否含防腐劑"],
            "isCombination": row["是否為複方"],
            "source": row["資料來源"],
            "note": row["備註"],
            "oneLine": one_line_product(row),
            "searchText": " ".join([
                row["商品名"], row["英文品名"], row["許可證字號"], row["許可證持有廠商"],
                row["藥品分類"], row["劑型"], row["規格"], row["適應症完整原文"],
                row["適應症摘要"], row["推定用途分類"], row["全部成分原文"], row["主要成分"],
            ]).lower(),
        }
        products.append(product)
        component_counts.update(components)
        indication_counts.update(indications)
        category_counts[row["推定用途分類"]] += 1
        dosage_counts[row["劑型"]] += 1
        drug_counts[row["藥品分類"]] += 1
        preservative_counts[row["是否含防腐劑"]] += 1

    component_categories = {name: component_category(name) for name in component_counts}
    return {
        "products": products,
        "components": sorted(component_counts.keys(), key=lambda c: (-component_counts[c], c)),
        "indications": sorted(indication_counts.keys(), key=lambda c: (-indication_counts[c], c)),
        "usageCategories": sorted(category_counts.keys(), key=lambda c: (-category_counts[c], c)),
        "dosageForms": sorted(dosage_counts.keys(), key=lambda c: (-dosage_counts[c], c)),
        "drugClasses": sorted(drug_counts.keys(), key=lambda c: (-drug_counts[c], c)),
        "preservativeStatuses": sorted(preservative_counts.keys(), key=lambda c: (-preservative_counts[c], c)),
        "componentCategories": component_categories,
        "synonyms": SYNONYMS,
        "summary": {
            "productCount": len(products),
            "componentCount": len(component_counts),
            "indicationCount": len(indication_counts),
            "categoryCounts": dict(sorted(category_counts.items())),
            "drugCounts": dict(sorted(drug_counts.items())),
            "preservativeCounts": dict(sorted(preservative_counts.items())),
        },
    }


def write_analysis_files(data: dict):
    products = data["products"]
    components = list(data["components"])
    indications = list(data["indications"])
    component_categories = data.get("componentCategories", {})
    by_component = defaultdict(list)
    by_indication = defaultdict(list)
    for p in products:
        for comp in p.get("components", []):
            by_component[comp].append(p)
        for ind in p.get("indicationSummary", []):
            by_indication[ind].append(p)

    def join(values):
        return "；".join(str(v) for v in values if str(v).strip())

    matrix_rows = []
    for comp in components:
        comp_products = by_component.get(comp, [])
        comp_ids = {p["id"] for p in comp_products}
        row = {"Ingredient": comp, "Product Count": len(comp_products)}
        for ind in indications:
            row[ind] = sum(1 for p in by_indication.get(ind, []) if p["id"] in comp_ids)
        matrix_rows.append(row)
    write_csv(REPO / "eye_ingredient_indication_matrix.csv", matrix_rows, ["Ingredient", "Product Count"] + indications)

    profile_rows = []
    for comp in components:
        comp_products = by_component.get(comp, [])
        indication_counter = Counter(ind for p in comp_products for ind in p.get("indicationSummary", []))
        drug_counter = Counter(p.get("drugClass", "") for p in comp_products)
        preservative_counter = Counter(p.get("preservativeStatus", "") for p in comp_products)
        co_counter = Counter(other for p in comp_products for other in p.get("components", []) if other != comp)
        max_ind = max(indication_counter.values(), default=0)
        specificity = round((max_ind / len(comp_products)) * 100, 1) if comp_products else 0
        profile_rows.append({
            "Ingredient": comp,
            "Ingredient Class": component_categories.get(comp, "其他成分"),
            "Product Count": len(comp_products),
            "Top Indications": join([f"{k}({v})" for k, v in indication_counter.most_common(8)]),
            "Indication Profile": join([f"{k}:{v}" for k, v in indication_counter.most_common()]),
            "Breadth Score": len(indication_counter),
            "Specificity Score": specificity,
            "Most Related Indication": indication_counter.most_common(1)[0][0] if indication_counter else "",
            "Rx Count": drug_counter.get("處方藥", 0),
            "OTC Count": drug_counter.get("指示藥", 0) + drug_counter.get("成藥", 0),
            "待人工確認 Count": drug_counter.get("待人工確認", 0),
            "中藥 Count": sum(1 for p in comp_products if p.get("isTcm") == "是"),
            "含防腐劑 Count": preservative_counter.get("是", 0),
            "Common Co-occurring Ingredients": join([f"{k}({v})" for k, v in co_counter.most_common(8)]),
            "Representative Products": join([p.get("name", "") for p in comp_products[:8]]),
            "Notes": "依 TFDA 開放資料與規則分類自動整理，藥品分類欄位待人工確認時請回查原始許可證。",
        })
    write_csv(REPO / "eye_ingredient_profiles.csv", profile_rows, [
        "Ingredient", "Ingredient Class", "Product Count", "Top Indications", "Indication Profile",
        "Breadth Score", "Specificity Score", "Most Related Indication", "Rx Count", "OTC Count",
        "待人工確認 Count", "中藥 Count", "含防腐劑 Count", "Common Co-occurring Ingredients",
        "Representative Products", "Notes",
    ])

    co_rows = []
    product_by_pair = defaultdict(list)
    for p in products:
        comps = sorted(set(p.get("components", [])))
        for a, b in itertools.combinations(comps, 2):
            product_by_pair[(a, b)].append(p)
    for (a, b), pair_products in sorted(product_by_pair.items(), key=lambda item: (-len(item[1]), item[0][0], item[0][1])):
        denom = min(len(by_component.get(a, [])), len(by_component.get(b, []))) or 1
        shared_indications = Counter(ind for p in pair_products for ind in p.get("indicationSummary", []))
        co_rows.append({
            "Ingredient A": a,
            "Ingredient B": b,
            "Co-occurring Product Count": len(pair_products),
            "Co-occurrence Rate": round(len(pair_products) / denom, 4),
            "Shared Product Names": join([p.get("name", "") for p in pair_products[:20]]),
            "Shared Indications": join([f"{k}({v})" for k, v in shared_indications.most_common(10)]),
            "Notes": "同一產品主要成分欄位共同出現。",
        })
    write_csv(REPO / "eye_ingredient_cooccurrence.csv", co_rows, [
        "Ingredient A", "Ingredient B", "Co-occurring Product Count", "Co-occurrence Rate",
        "Shared Product Names", "Shared Indications", "Notes",
    ])

    ind_rows = []
    for ind in indications:
        ind_products = by_indication.get(ind, [])
        comp_counter = Counter(comp for p in ind_products for comp in p.get("components", []))
        class_counter = Counter(component_categories.get(comp, "其他成分") for comp in comp_counter)
        drug_counter = Counter(p.get("drugClass", "") for p in ind_products)
        preservative_counter = Counter(p.get("preservativeStatus", "") for p in ind_products)
        related = Counter(other for p in ind_products for other in p.get("indicationSummary", []) if other != ind)
        top_comp = comp_counter.most_common(1)[0][0] if comp_counter else "待人工確認"
        ind_rows.append({
            "Indication": ind,
            "Product Count": len(ind_products),
            "Top Ingredients": join([f"{k}({v})" for k, v in comp_counter.most_common(10)]),
            "Top Ingredient Classes": join([f"{k}({v})" for k, v in class_counter.most_common(8)]),
            "Top Products": join([p.get("name", "") for p in ind_products[:10]]),
            "Rx / 指示藥 / 成藥 / 待確認": join([f"{k}:{v}" for k, v in drug_counter.most_common()]),
            "Preservative Summary": join([f"{k}:{v}" for k, v in preservative_counter.most_common()]),
            "Related Indications": join([f"{k}({v})" for k, v in related.most_common(8)]),
            "Summary Sentence": f"{ind} 相關產品共 {len(ind_products)} 項，常見成分以 {top_comp} 為代表。",
        })
    write_csv(REPO / "eye_indication_profiles.csv", ind_rows, [
        "Indication", "Product Count", "Top Ingredients", "Top Ingredient Classes", "Top Products",
        "Rx / 指示藥 / 成藥 / 待確認", "Preservative Summary", "Related Indications", "Summary Sentence",
    ])

    class_rows = []
    for comp in components:
        cls = component_categories.get(comp, "其他成分")
        count = len(by_component.get(comp, []))
        confidence = "高" if cls != "其他成分" else ("中" if count >= 3 else "低")
        reason = "依已建立眼科常見成分分類表對應。" if cls != "其他成分" else "未命中主要分類表，依產品用途與共現資料保留為其他成分。"
        class_rows.append({
            "Ingredient": comp,
            "Ingredient Class": cls,
            "Class Confidence": confidence,
            "Classification Reason": reason,
        })
    write_csv(REPO / "eye_ingredient_classification.csv", class_rows, [
        "Ingredient", "Ingredient Class", "Class Confidence", "Classification Reason",
    ])


def update_html_data(data: dict):
    for filename in ["eye_drop_explorer.html", "eye_drop_explorer_v2.html"]:
        path = REPO / filename
        text = path.read_text(encoding="utf-8")
        replacement = "const APP_DATA = " + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n  const state"
        text = re.sub(r"const APP_DATA = .*?;\n\s*const state", replacement, text, count=1, flags=re.S)
        path.write_text(text, encoding="utf-8")


def write_report(rows: list[dict], excluded: list[dict], data: dict):
    raw_excluded = sum(1 for r in excluded if r["排除原因"] == "原料藥／非最終製劑")
    category_lines = "\n".join(f"- {k}：{v}" for k, v in data["summary"]["categoryCounts"].items())
    preservative_lines = "\n".join(f"- {k}：{v}" for k, v in data["summary"]["preservativeCounts"].items())
    report = f"""# 台灣眼科外用藥品資料庫驗證報告

## 1. 納入條件
本資料庫只納入「有明確藥品許可證、可作為市售藥品使用的眼科外用產品」。

納入主表需同時符合：
- 有明確藥品許可證字號
- 有商品名或製劑名稱
- 有眼科外用劑型，例如眼藥水、點眼液、眼用懸液、眼用凝膠、眼用軟膏
- 有明確適應症
- 是最終藥品製劑，不是原料藥

判斷優先欄位：許可證種類、劑型、適應症、包裝／規格、商品名、英文品名。

## 2. 排除條件
已排除原料藥、藥品原料、Active Pharmaceutical Ingredient / API、bulk drug substance、中間體、製劑用原料、非最終銷售製劑，以及缺少明確商品名、劑型、規格或適應症的品項。

判斷為原料藥或非最終製劑者，不放入主表，改列於 `excluded_eye_products.csv`，排除原因為「原料藥／非最終製劑」。

## 3. 更新後資料量
- 主表產品數：{len(rows)}
- 排除產品數：{len(excluded)}
- 其中原料藥／非最終製劑：{raw_excluded}
- 成分數：{data['summary']['componentCount']}
- 適應症摘要數：{data['summary']['indicationCount']}

## 4. 推定用途分類
{category_lines}

## 5. 防腐劑摘要
{preservative_lines}

## 6. 產出檔案
- eye_meds_tw_raw.csv
- eye_meds_tw.xlsx
- eye_ingredient_indication_matrix.csv
- eye_ingredient_profiles.csv
- eye_ingredient_cooccurrence.csv
- eye_indication_profiles.csv
- eye_explorer_data.json
- eye_drop_explorer_data.json
- verification_report_eye_meds.md
- excluded_eye_products.csv

## 7. 資料來源
- TFDA 藥品有效許可證資料 InfoId=37
- TFDA 藥品詳細處方成分資料 InfoId=43
- TFDA 仿單與外盒連結資料 InfoId=39
- 查詢入口：{LICENSE_QUERY_URL}

## 8. 注意事項
本資料庫依 TFDA 開放資料欄位與規則自動整理，藥品分類、成分標準化與適應症摘要仍建議在實務使用前回查原始許可證與仿單。
"""
    (REPO / "verification_report_eye_meds.md").write_text(report, encoding="utf-8")


def main():
    rows, excluded, tables = build_primary_database()
    TABLES_JSON.write_text(json.dumps(tables, ensure_ascii=False, indent=2), encoding="utf-8")

    data = build_explorer_data(rows)
    for filename in ["eye_drop_explorer_data.json", "eye_explorer_data.json"]:
        (REPO / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    write_analysis_files(data)
    update_html_data(data)
    write_report(rows, excluded, data)

    # Keep v2 support notes synchronized with this stricter inclusion update.
    (REPO / "eye_drop_explorer_v2_update_notes.md").write_text(
        "# Eye Drop Explorer v2 Update Notes\n\n"
        "- Updated inclusion criteria to keep only final marketed ophthalmic external drug products.\n"
        "- Excluded raw materials, APIs, bulk drug substances, intermediates, formulation raw materials, and non-final dosage forms.\n"
        "- Added `excluded_eye_products.csv` with exclusion reasons, including `原料藥／非最終製劑`.\n"
        "- Rebuilt raw CSV, explorer JSON, analysis CSV files, HTML embedded data, and verification report.\n",
        encoding="utf-8",
    )
    shutil.copy2(REPO / "eye_drop_explorer_readme.md", REPO / "eye_drop_explorer_v2_readme.md")
    print(json.dumps({
        "included": len(rows),
        "excluded": len(excluded),
        "raw_material_excluded": sum(1 for r in excluded if r["排除原因"] == "原料藥／非最終製劑"),
        "components": data["summary"]["componentCount"],
        "indications": data["summary"]["indicationCount"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
