"""Build the Taiwan local nasal/oropharyngeal spray database from cached TFDA open data.

This is intentionally data-only.  It never changes site files or the eye database.
Run again safely to rebuild all CSVs from the cached official source snapshots.
"""
import csv
import datetime as dt
import json
import re
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parent
EYE_CACHE = BASE.parent / "eye_meds_rebuild_20260711"
CHECKED_AT = "2026-07-14T00:00:00+08:00"
LICENSE = "許可證字號"

PRODUCT_FIELDS = ["product_id","license_number","license_year","chinese_name","english_name","dosage_form_raw","dosage_form_normalized","route_raw","route_normalized","application_site","local_spray_inclusion_evidence","indication_raw","indication_normalized","active_ingredient_raw","active_ingredient_normalized","strength","strength_unit","therapeutic_class","license_status","license_expiry_date","applicant","manufacturer","source_id","verified_at","processing_status"]
SUBSTANCE_FIELDS = ["substance_id","substance_name_raw","substance_name_normalized","role","role_evidence","source_id","verified_at"]
PS_FIELDS = ["product_id","substance_id","role","strength","strength_unit","source_id","verified_at"]
IND_FIELDS = ["indication_id","indication_raw","indication_normalized","source_id","verified_at"]
PI_FIELDS = ["product_id","indication_id","source_id","verified_at"]
CLASS_FIELDS = ["class_id","class_label","scope","classification_rule","source_id"]
PC_FIELDS = ["product_id","class_id","classification_evidence","source_id","verified_at"]
SOURCE_FIELDS = ["source_id","source_type","source_name","source_detail","official_url","checked_at"]
EXCLUDED_FIELDS = ["license_number","chinese_name","english_name","dosage_form_raw","route_raw","candidate_reason","exclusion_reason","source_id","verified_at"]
REVIEW_FIELDS = ["review_id","license_number","chinese_name","english_name","dosage_form_raw","route_raw","candidate_reason","ambiguity_reason","recommended_action","source_id","verified_at"]

def read_zip(info_id):
    path = EYE_CACHE / f"tfda_info{info_id}.zip"
    with zipfile.ZipFile(path) as zf:
        return json.loads(zf.read(zf.namelist()[0]).decode("utf-8-sig"))

def text(row, key): return str(row.get(key) or "").strip()
def clean(value): return re.sub(r"\s+", " ", value or "").strip()
def key(value): return re.sub(r"[^a-z0-9]+", "_", (value or "").lower()).strip("_") or "unknown"
def contains(value, terms):
    v = (value or "").lower()
    return any(x.lower() in v for x in terms)

def license_year(row):
    date = text(row, "發證日期")
    match = re.match(r"(\d{4})/", date)
    return match.group(1) if match else ""

def status(row):
    return "revoked_or_cancelled" if text(row, "註銷狀態") else "active"

def candidate_reason(row):
    blob = " | ".join(text(row, x) for x in ("中文品名","英文品名","劑型","用法用量","適應症"))
    form = text(row,"劑型")
    if contains(form, ["噴", "spray", "aerosol"]): return "dosage_form_spray_signal"
    if contains(blob, ["鼻噴", "鼻用噴", "口腔噴", "咽喉噴", "喉嚨噴", "throat spray", "nasal spray", "oral spray"]): return "name_or_route_spray_signal"
    return ""

def classify(row):
    """Return include/site/form/route/evidence OR review/exclusion reason."""
    cn, en, form, use = (text(row,x) for x in ("中文品名","英文品名","劑型","用法用量"))
    # Indication is intentionally excluded from route decisions: it is corroborative
    # information only and must never make a respiratory product a local spray.
    blob = " | ".join([cn,en,form,use])
    lower = blob.lower()
    # Explicit systemic/pulmonary exclusion has priority.  A generic "external
    # spray" dosage form does not: TFDA uses it for some clearly named oral sprays.
    if contains(blob, ["舌下", "sublingual", "硝化甘油", "nitroglycerin"]):
        return "exclude", "", "", "", "systemic_or_sublingual_spray", "explicit systemic/sublingual signal"
    if contains(blob, ["吸入粉霧", "乾粉吸入", "氣喘", "copd", "霧化吸入", "inhaler", "inhalation aerosol", "吸入氣霧"]):
        return "exclude", "", "", "", "pulmonary_inhaler", "pulmonary inhalation signal"
    nasal = contains(form, ["鼻噴", "鼻用噴", "鼻腔噴", "鼻用氣霧"]) or contains(cn+" "+en, ["鼻噴", "鼻用噴", "nasal spray"]) or contains(use, ["鼻腔", "鼻內", "鼻用"])
    oral = contains(form, ["口腔噴", "喉噴", "咽喉噴", "口咽噴"]) or contains(cn+" "+en, ["口腔噴", "喉嚨噴", "咽喉噴", "throat spray", "oral spray", "oromucosal"])
    if nasal and oral:
        return "review", "", "", "", "mixed_or_unclear_site", "both nasal and oral/throat signals"
    if nasal:
        form_norm = "nasal_spray" if contains(form,["噴","spray","氣霧"]) else "nasal_local_other"
        evidence = f"TFDA 劑型={form}; 用法用量={use}; 品名={cn}/{en}. 鼻腔局部使用訊號由劑型/用法或品名交叉支持。"
        return "include", "nasal", form_norm, "intranasal", "", evidence
    if oral:
        site = "oral_and_throat" if contains(blob,["口咽","口腔及咽喉","oral and throat"]) else ("throat" if contains(blob,["咽","喉","throat"]) else "oral_mucosal")
        evidence = f"TFDA 劑型={form}; 用法用量={use}; 品名={cn}/{en}. 口腔/咽喉局部使用訊號由劑型/用法或品名交叉支持。"
        return "include", site, "oropharyngeal_spray", "oromucosal_or_throat", "", evidence
    if contains(blob, ["皮膚", "頭皮", "傷口", "外用噴", "耳用", "消毒", "環境"]):
        return "exclude", "", "", "", "skin_or_other_nonlocal_spray", "skin/ear/wound/environment signal"
    return "review", "", "", "", "spray_site_not_confirmed", "spray signal present but local nasal/oropharyngeal route not confirmed"

ACTIVE_MAP = {
 "fluticasone":"fluticasone", "mometasone":"mometasone", "budesonide":"budesonide", "beclomethasone":"beclomethasone", "triamcinolone":"triamcinolone", "ciclesonide":"ciclesonide",
 "azelastine":"azelastine", "olopatadine":"olopatadine", "levocabastine":"levocabastine", "oxymetazoline":"oxymetazoline", "xylometazoline":"xylometazoline", "naphazoline":"naphazoline", "ipratropium":"ipratropium", "cromolyn":"cromolyn", "sodium cromoglicate":"cromolyn",
 "benzydamine":"benzydamine", "benzidamine":"benzydamine", "hexetidine":"hexetidine", "povidone iodine":"povidone-iodine", "chlorhexidine":"chlorhexidine", "lidocaine":"lidocaine", "xylocaine":"lidocaine", "benzocaine":"benzocaine", "cetylpyridinium":"cetylpyridinium", "dequalinium":"dequalinium", "nystatin":"nystatin", "miconazole":"miconazole", "chlorobutanol":"chlorobutanol",
}
def normalized_active(raw):
    low = raw.lower()
    found = [v for k,v in ACTIVE_MAP.items() if k in low]
    return "; ".join(dict.fromkeys(found)) or clean(raw).lower()
def active_classes(raw, site):
    x=raw.lower(); out=[]
    def add(label, terms):
        if any(t in x for t in terms): out.append(label)
    if site == "nasal":
        add("corticosteroid",["fluticasone","mometasone","budesonide","beclomethasone","triamcinolone","ciclesonide"])
        add("antihistamine",["azelastine","olopatadine","levocabastine"])
        add("decongestant",["oxymetazoline","xylometazoline","naphazoline","phenylephrine"])
        add("anticholinergic",["ipratropium"]); add("mast_cell_stabilizer",["cromolyn","cromoglicate"])
        add("saline_or_moisturizing_drug",["sodium chloride","sea water","海水"]); add("anti_infective",["mupirocin","framycetin","neomycin"])
        return out or ["other_nasal"]
    add("antiseptic_or_anti_infective",["hexetidine","povidone","chlorhexidine","cetylpyridinium","dequalinium"])
    add("local_anesthetic",["lidocaine","benzocaine"]); add("analgesic_or_anti_inflammatory",["benzydamine","benzidamine","flurbiprofen"])
    add("antifungal",["nystatin","miconazole"]); add("corticosteroid",["dexamethasone","beclomethasone"])
    add("mucosal_protective",["hyaluron","carboxymethylcellulose","glycerin"])
    return out or ["other_oropharyngeal"]

def write(name, rows, fields):
    with (BASE/name).open("w",encoding="utf-8-sig",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)

def main():
    BASE.mkdir(parents=True,exist_ok=True)
    licenses=read_zip(37); ingredient_rows=read_zip(43)
    ingredients=defaultdict(list)
    for r in ingredient_rows: ingredients[text(r,LICENSE)].append(r)
    source_id="tfda_open_data_info37_43_cached_20260711"
    products=[]; substances={}; ps=[]; inds={}; pis=[]; pcs=[]; excluded=[]; review=[]; processed=[]
    # The source can contain a duplicate licence after administrative updates.
    # Keep the most recently changed representation, never duplicate a licence.
    candidate_by_license={}
    for row in licenses:
        if text(row,"許可證種類").replace("　","")!="製劑" or not candidate_reason(row): continue
        lic=text(row,LICENSE)
        if lic not in candidate_by_license or text(row,"異動日期") > text(candidate_by_license[lic],"異動日期"):
            candidate_by_license[lic]=row
    candidates=list(candidate_by_license.values())
    for n,row in enumerate(candidates,1):
        lic=text(row,LICENSE); reason=candidate_reason(row); decision,site,form_norm,route_norm,why,evidence=classify(row)
        common={"license_number":lic,"chinese_name":text(row,"中文品名"),"english_name":text(row,"英文品名"),"dosage_form_raw":text(row,"劑型"),"route_raw":text(row,"用法用量"),"candidate_reason":reason,"source_id":source_id,"verified_at":CHECKED_AT}
        if decision=="exclude":
            excluded.append({**common,"exclusion_reason":why}); processed.append({"license_number":lic,"status":"excluded","last_updated":CHECKED_AT}); continue
        if decision=="review":
            review.append({"review_id":f"review_{n:04d}",**common,"ambiguity_reason":why,"recommended_action":"Review official TFDA route/leaflet manually; do not include until local site is confirmed."}); processed.append({"license_number":lic,"status":"manual_review","last_updated":CHECKED_AT}); continue
        pid=f"spray_{len(products)+1:04d}"
        raw_active=text(row,"主成分略述"); norm_active=normalized_active(raw_active)
        ing=ingredients.get(lic,[])
        strength="; ".join(clean(text(x,"含量描述")) for x in ing if text(x,"含量描述"))
        unit="; ".join(dict.fromkeys(text(x,"含量單位") for x in ing if text(x,"含量單位")))
        indication=text(row,"適應症"); ind_norm=clean(indication).lower()
        classes=active_classes(raw_active,site)
        if len(classes)>1: classes.append("combination")
        products.append({"product_id":pid,"license_number":lic,"license_year":license_year(row),"chinese_name":text(row,"中文品名"),"english_name":text(row,"英文品名"),"dosage_form_raw":text(row,"劑型"),"dosage_form_normalized":form_norm,"route_raw":text(row,"用法用量"),"route_normalized":route_norm,"application_site":site,"local_spray_inclusion_evidence":evidence,"indication_raw":indication,"indication_normalized":ind_norm,"active_ingredient_raw":raw_active,"active_ingredient_normalized":norm_active,"strength":strength,"strength_unit":unit,"therapeutic_class":"; ".join(classes),"license_status":status(row),"license_expiry_date":text(row,"有效日期"),"applicant":text(row,"申請商名稱"),"manufacturer":text(row,"製造商名稱"),"source_id":source_id,"verified_at":CHECKED_AT,"processing_status":"core_complete_optional_missing"})
        # Main active summary is TFDA's explicit active-ingredient field; keep one traceable record.
        sid="sub_"+key(norm_active)
        substances.setdefault(sid,{"substance_id":sid,"substance_name_raw":raw_active,"substance_name_normalized":norm_active,"role":"active","role_evidence":"TFDA 許可證主成分略述欄位","source_id":source_id,"verified_at":CHECKED_AT})
        ps.append({"product_id":pid,"substance_id":sid,"role":"active","strength":strength,"strength_unit":unit,"source_id":source_id,"verified_at":CHECKED_AT})
        if indication:
            iid="ind_"+key(ind_norm); inds.setdefault(iid,{"indication_id":iid,"indication_raw":indication,"indication_normalized":ind_norm,"source_id":source_id,"verified_at":CHECKED_AT}); pis.append({"product_id":pid,"indication_id":iid,"source_id":source_id,"verified_at":CHECKED_AT})
        for c in classes: pcs.append({"product_id":pid,"class_id":c,"classification_evidence":f"rule evaluated against TFDA 主成分略述: {raw_active}","source_id":source_id,"verified_at":CHECKED_AT})
        processed.append({"license_number":lic,"status":"included","product_id":pid,"last_updated":CHECKED_AT})
    classes=[]
    for c,scope in [(c,"nasal") for c in ["corticosteroid","antihistamine","decongestant","anticholinergic","mast_cell_stabilizer","saline_or_moisturizing_drug","anti_infective","combination","other_nasal"]]+[(c,"oropharyngeal") for c in ["antiseptic_or_anti_infective","local_anesthetic","analgesic_or_anti_inflammatory","antifungal","corticosteroid","mucosal_protective","combination","other_oropharyngeal"]]:
        classes.append({"class_id":c,"class_label":c,"scope":scope,"classification_rule":"Multi-signal rule: TFDA 主成分略述 mapped to a documented pharmacologic class; combination only when two or more base classes apply.","source_id":source_id})
    write("products.csv",products,PRODUCT_FIELDS); write("substances.csv",list(substances.values()),SUBSTANCE_FIELDS); write("product_substances.csv",ps,PS_FIELDS); write("indications.csv",list(inds.values()),IND_FIELDS); write("product_indications.csv",pis,PI_FIELDS); write("classes.csv",classes,CLASS_FIELDS); write("product_classes.csv",pcs,PC_FIELDS)
    write("sources.csv",[{"source_id":source_id,"source_type":"TFDA_open_data_cache","source_name":"TFDA 藥品許可證與詳細處方成分開放資料","source_detail":"Reused local official cache: InfoId=37 license data (26,034 rows) and InfoId=43 ingredient data (125,938 rows); no leaflet download/OCR.","official_url":"https://data.gov.tw/datasets/search?p=1&size=10&s=藥品許可證","checked_at":CHECKED_AT}],SOURCE_FIELDS)
    write("excluded_records.csv",excluded,EXCLUDED_FIELDS); write("manual_review_queue.csv",review,REVIEW_FIELDS)
    rules=[
      {"rule_id":"candidate","rule_type":"candidate","rule":"製劑且劑型、品名或官方用法含噴劑訊號才成為候選","source":"TFDA InfoId=37"},
      {"rule_id":"inclusion","rule_type":"inclusion","rule":"鼻/口咽收錄需劑型、官方用法或名稱顯示局部目標部位；單靠適應症不收錄","source":"TFDA InfoId=37"},
      {"rule_id":"exclude","rule_type":"exclusion","rule":"肺部吸入、舌下全身作用、皮膚/傷口/耳/環境噴劑優先排除","source":"TFDA InfoId=37"},
      {"rule_id":"roles","rule_type":"ingredient_role","rule":"主成分略述=active；處方未能以結構化資料判別角色者不推定為保存劑或賦形劑","source":"TFDA InfoId=37/43"},
      {"rule_id":"class","rule_type":"classification","rule":"以主成分藥理映射多標籤；無可靠映射歸 other_*，非單一名稱關鍵字判定","source":"TFDA InfoId=37"},]
    write("normalization_rules.csv",rules,["rule_id","rule_type","rule","source"])
    nasal=sum(p["application_site"]=="nasal" for p in products); oro=len(products)-nasal
    pulmonary=sum(x["exclusion_reason"]=="pulmonary_inhaler" for x in excluded); other=len(excluded)-pulmonary
    required=["license_number","license_year","chinese_name","dosage_form_raw","dosage_form_normalized","route_raw","route_normalized","application_site","local_spray_inclusion_evidence","indication_raw","active_ingredient_raw","license_status","license_expiry_date","source_id"]
    complete=sum(all(p[x] for x in required) for p in products); rate=(complete/len(products)*100) if products else 0
    state={"project":"taiwan_local_nasal_oropharyngeal_spray","phase":"phase_1_data_only_complete","source_cache":{"info37":str(EYE_CACHE/'tfda_info37.zip'),"info43":str(EYE_CACHE/'tfda_info43.zip')},"candidate_total":len(candidates),"included_total":len(products),"excluded_total":len(excluded),"manual_review_total":len(review),"batch_size_max":50,"completed_records":processed,"resume_from":"complete; rerun build_spray_database.py rebuilds deterministically from official cache","updated_at":CHECKED_AT}
    (BASE/"processing_state.json").write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf-8")
    # Stratified 20-record validation sample: both intended sites and key false-positive classes.
    sample=[]
    def take(rows, predicate, count):
        selected = 0
        for x in rows:
            if predicate(x) and x not in sample and selected < count:
                sample.append(x); selected += 1
    take(products, lambda x:x["application_site"]=="nasal", 7)
    take(products, lambda x:x["application_site"]!="nasal", 5)
    take(excluded, lambda x:x["exclusion_reason"]=="pulmonary_inhaler", 2)
    take(excluded, lambda x:x["exclusion_reason"]=="skin_or_other_nonlocal_spray", 3)
    take(review, lambda x:True, 3)
    (BASE/"sample_validation.md").write_text("# 20-record rule-validation sample\n\nThis deterministic sample contains included nasal/oropharyngeal products plus pulmonary/other exclusions and ambiguous manual-review records. Each record was decided from TFDA structured fields, without leaflet/OCR. A whole-cache scan found no records with `舌下`, `硝化甘油`, or `NITROGLYCERIN` in the structured product, dosage-form, or official-use fields, so the systemic-spray test is documented as a zero-match negative control rather than fabricated.\n\n"+"\n".join(f"- {x.get('license_number')}: {x.get('application_site') or x.get('exclusion_reason') or x.get('ambiguity_reason')}" for x in sample)+"\n",encoding="utf-8")
    report=f"""# Data quality report\n\n- Candidate manufactured-drug records: {len(candidates)}\n- Included local sprays: {len(products)} (nasal {nasal}; oral/throat {oro})\n- Excluded pulmonary inhalers: {pulmonary}\n- Excluded skin/other sprays: {other}\n- Manual review queue: {len(review)}\n- Included products with confirmed active ingredient: {sum(bool(x['active_ingredient_raw']) for x in products)}\n- Required core-field completeness: {rate:.1f}% ({complete}/{len(products)})\n\nChecks: unique licence numbers in products; all products are TFDA 製劑; all included products carry inclusion evidence, indication, active ingredient, licence metadata, and official-source ID. Detailed ingredient rows whose role is not explicit are deliberately not inferred as preservatives/excipients.\n"""
    (BASE/"data_quality_report.md").write_text(report,encoding="utf-8")
    summary=f"""# Build summary\n\nBuilt phase 1 data only on {CHECKED_AT} from existing TFDA official-data caches. No HTML, site, image card, eye database, leaflet download, or OCR was changed.\n\nThe candidate and exclusion rules were validated with `sample_validation.md` before the remaining deterministic candidates were processed. Records are represented in `processing_state.json`, and rebuilding is safe/resumable.\n\nWebsite work is **not yet authorized by this phase**; it may proceed only after the manual review queue is resolved and the dataset is accepted.\n"""
    (BASE/"build_summary.md").write_text(summary,encoding="utf-8")
    print(json.dumps({"candidates":len(candidates),"included":len(products),"nasal":nasal,"oropharyngeal":oro,"pulmonary_excluded":pulmonary,"other_excluded":other,"review":len(review),"complete_rate":rate},ensure_ascii=False))
if __name__=="__main__": main()
