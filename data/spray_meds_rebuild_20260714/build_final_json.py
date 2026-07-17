"""Mechanical export of formal spray CSV tables for the website."""
import csv, json
from collections import defaultdict
from pathlib import Path

B=Path(__file__).resolve().parent; OUT=B/'final'/'spray_meds_final.json'
def read(name):
    with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
products=read('products.csv'); ps=read('product_substances.csv'); inds={r['indication_id']:r for r in read('indications.csv')}; pis=defaultdict(list); pcs=defaultdict(list)
for r in read('product_indications.csv'):pis[r['product_id']].append(inds.get(r['indication_id'],{}))
for r in read('product_classes.csv'):pcs[r['product_id']].append(r['class_id'])
def category(p):
    s=(p['indication_raw']+' '+p['therapeutic_class']).lower()
    product_text=(p['chinese_name']+' '+p['english_name']+' '+p['active_ingredient_raw']).lower()
    if any(x in product_text for x in ('spravato','esketamine','imigran','sumatriptan','nicorette','quickmist','nicotine','xylonor')):return '其他'
    if p['application_site']=='nasal':
        if '過敏' in p['indication_raw'] or 'allerg' in s:return '過敏性鼻部症狀'
        if '鼻竇' in p['indication_raw']:return '鼻竇／鼻腔發炎症狀'
        return '鼻塞、流鼻水與其他鼻部症狀'
    if any(x in s for x in ('真菌','鵝口瘡','fungal','nystatin','miconazole')):return '口腔／咽喉感染'
    if any(x in s for x in ('疼痛','痛','pain','analgesic','anti-inflammatory')):return '口腔／咽喉疼痛與發炎'
    if any(x in s for x in ('感染','antiseptic','infective')):return '口腔／咽喉局部感染'
    return '其他口腔／咽喉局部症狀'
out=[]
for p in products:
    # The formal CSV only contains formal, non-unresolved products.
    active=[]
    # TFDA's main-active field separates combination components with ``;;``.
    # Prefer that component boundary over a product-level normalized summary so
    # each confirmed active in a combination is counted separately in the UI.
    raw_parts=(p['active_ingredient_raw'] or '').split(';;')
    parts=raw_parts if len(raw_parts)>1 else (p['active_ingredient_normalized'] or p['active_ingredient_raw']).split(';')
    for name in parts:
        name=name.strip().lower()
        if name and name not in active: active.append(name)
    out.append({
      'product_id':p['product_id'],'license_number':p['license_number'],'chinese_name':p['chinese_name'],'english_name':p['english_name'],'dosage_form':p['dosage_form_raw'],'dosage_form_normalized':p['dosage_form_normalized'],'application_site':p['application_site'],'indication':p['indication_raw'],'indication_category':category(p),'active_ingredients':active,'active_ingredient_raw':p['active_ingredient_raw'],'strength':p['strength'],'strength_unit':p['strength_unit'],'therapeutic_classes':sorted(set(pcs[p['product_id']] or [x.strip() for x in p['therapeutic_class'].split(';') if x.strip()])),'license_year':p['license_year'],'license_status':p['license_status'],'license_expiry_date':p['license_expiry_date'],'applicant':p['applicant'],'manufacturer':p['manufacturer'],'source_id':p['source_id'],'route_raw':p['route_raw'],'inclusion_evidence':p['local_spray_inclusion_evidence']
    })
assert len(out)==141 and {x['application_site'] for x in out} <= {'nasal','throat','oral_mucosal'}
assert sum(x['application_site']=='nasal' for x in out)==97 and sum(x['application_site']=='throat' for x in out)==30 and sum(x['application_site']=='oral_mucosal' for x in out)==14
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'schema_version':'1.0','generated_from':['products.csv','product_substances.csv','indications.csv','product_indications.csv','product_classes.csv'],'product_count':len(out),'products':out},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Wrote {len(out)} formal products to {OUT}')
