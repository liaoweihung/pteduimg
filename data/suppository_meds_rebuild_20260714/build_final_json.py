"""Mechanical website export from the formal suppository CSV relation tables."""
import csv, json
from collections import defaultdict
from pathlib import Path

B=Path(__file__).resolve().parent; OUT=B/'final'/'suppository_meds_final.json'
def read(name):
    with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
products=read('products.csv'); substances={r['substance_id']:r for r in read('substances.csv')}
ps=defaultdict(list); pcs=defaultdict(list)
for r in read('product_substances.csv'):
    if r['role']=='active' and r['confirmation_status']=='confirmed': ps[r['product_id']].append(r)
for r in read('product_classes.csv'): pcs[r['product_id']].append(r['class_id'])
def indication_category(p):
    x=(p['indication_raw']+' '+p['therapeutic_class']).lower()
    if p['application_site']=='rectal':
        if 'hemorrhoid' in x or '痔' in x:return '痔瘡與肛門直腸不適'
        if any(v in x for v in ('constipat','便秘','laxative')):return '便秘與排便準備'
        if any(v in x for v in ('fever','發燒','pain','疼痛','anti-inflammatory','diclofenac','acetaminophen')):return '發燒、疼痛與發炎'
        if any(v in x for v in ('nausea','vomit','噁心','嘔吐')):return '噁心與嘔吐'
        return '其他肛門／直腸用途'
    if any(v in x for v in ('fung','candida','念珠','黴菌')):return '陰道黴菌感染'
    if any(v in x for v in ('bacteria','細菌','trichomon','滴蟲')):return '陰道細菌或滴蟲感染'
    if any(v in x for v in ('atrophy','萎縮','hormone','estr')):return '陰道萎縮與荷爾蒙相關用途'
    return '其他陰道用途'
out=[]
for p in products:
    actives=[]
    for rel in ps[p['product_id']]:
        s=substances[rel['substance_id']]
        # Only the explicit confirmed-active relation is exported.  A TFDA
        # semicolon-separated active summary represents distinct combination actives.
        for raw in s['raw_name'].split(';;'):
            raw=raw.strip()
            if raw and raw not in actives:actives.append(raw)
    assert actives, p['license_number']
    out.append({'product_id':p['product_id'],'license_number':p['license_number'],'chinese_name':p['chinese_name'],'english_name':p['english_name'],'dosage_form':p['dosage_form_raw'],'dosage_form_normalized':p['dosage_form_normalized'],'route_raw':p['route_raw'],'route_normalized':p['route_normalized'],'application_site':p['application_site'],'action_scope':p['action_scope'],'indication':p['indication_raw'],'indication_category':indication_category(p),'active_ingredients':actives,'therapeutic_classes':sorted(set(pcs[p['product_id']] or p['therapeutic_class'].split(';'))),'license_year':p['license_year'],'license_status':p['license_status'],'license_expiry_date':p['license_expiry_date'],'applicant':p['applicant'],'manufacturer':p['manufacturer'],'source_id':p['source_id'],'verified_at':p['verified_at'],'inclusion_evidence':p['suppository_inclusion_evidence']})
assert len(out)==148
assert sum(p['application_site']=='rectal' for p in out)==85
assert sum(p['application_site']=='vaginal' for p in out)==63
assert sum(p['action_scope']=='local' for p in out)==83
assert sum(p['action_scope']=='systemic' for p in out)==33
assert sum(p['action_scope']=='unclear' for p in out)==32
OUT.parent.mkdir(exist_ok=True)
OUT.write_text(json.dumps({'schema_version':'1.0','generated_from':['products.csv','substances.csv','product_substances.csv','product_classes.csv'],'product_count':len(out),'products':out},ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Wrote {len(out)} formal products to {OUT}')
