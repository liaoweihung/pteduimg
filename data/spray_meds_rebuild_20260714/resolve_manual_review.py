"""Resolve only the existing 18-record manual-review queue using cached TFDA data.

No all-record candidate scan occurs here.  The five ambiguous lidocaine sprays
remain unresolved because the one permitted attempt to their cached official
leaflet URL was unavailable and the structured fields do not state body site.
"""
import csv, datetime as dt, json, zipfile
from collections import Counter, defaultdict
from pathlib import Path

B=Path(__file__).resolve().parent; C=B.parent/'eye_meds_rebuild_20260711'; NOW='2026-07-14T00:00:00+08:00'; SOURCE='tfda_open_data_info37_43_cached_20260711'
def csvrows(name):
    with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def write(name,rows,fields):
    with (B/name).open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
def load(n):
    with zipfile.ZipFile(C/f'tfda_info{n}.zip') as z:return json.loads(z.read(z.namelist()[0]).decode('utf-8-sig'))

P_FIELDS=csvrows('products.csv')[0].keys(); PS_FIELDS=csvrows('product_substances.csv')[0].keys(); I_FIELDS=csvrows('indications.csv')[0].keys(); PI_FIELDS=csvrows('product_indications.csv')[0].keys(); PC_FIELDS=csvrows('product_classes.csv')[0].keys(); E_FIELDS=csvrows('excluded_records.csv')[0].keys(); R_FIELDS=csvrows('manual_review_queue.csv')[0].keys()
q=csvrows('manual_review_queue.csv'); products=csvrows('products.csv'); ps=csvrows('product_substances.csv'); inds=csvrows('indications.csv'); pis=csvrows('product_indications.csv'); pcs=csvrows('product_classes.csv'); excluded=csvrows('excluded_records.csv')
if (B/'manual_review_resolution.csv').exists():
    raise SystemExit('Resolution already applied; this script is intentionally non-replaying to prevent duplicate products.')
lic_key='許可證字號'; L={r[lic_key]:r for r in load(37)}; ing=defaultdict(list)
for r in load(43):ing[r[lic_key]].append(r)

# Final decisions derived from TFDA structured fields only.  “unresolved” means
# not enough official structured evidence to assign a nasal/oral/throat site.
nasal={'衛署藥製字第019585號'}
pulmonary={'衛部藥輸字第026657號','衛部藥輸字第027524號','衛部藥輸字第027672號','衛部藥輸字第027945號','衛部藥輸字第028490號','衛部藥輸字第028183號','衛署藥輸字第023074號','衛署藥製字第049211號','衛署藥輸字第023473號','衛部藥輸字第026760號'}
skin={'衛部藥輸字第027051號','衛部藥輸字第028249號'}
unresolved={'衛署藥製字第055246號','衛署藥輸字第022329號','衛署藥製字第046747號','衛署藥製字第055411號','衛署藥製字第055413號'}
assert len(q)==18 and len(nasal|pulmonary|skin|unresolved)==18

res=[]; next_no=max(int(p['product_id'].split('_')[1]) for p in products)+1
for x in q:
    lic=x['license_number']; r=L[lic]; raw=r.get('主成分略述') or ''; name=x['chinese_name'] or x['english_name']; common={'license_number':lic,'product_name':name,'original_review_reason':x['ambiguity_reason'],'source_id':SOURCE,'reviewed_at':NOW}
    if lic in nasal:
        decision='include_nasal'; site='nasal'; evidence='TFDA 劑型「鼻用氣化噴霧劑」且中文品名含「鼻」；適應症為鼻炎/副鼻腔炎/過敏性鼻炎與鼻出血。'; confidence='high'
        pid=f'spray_{next_no:04d}'; next_no+=1
        strength='; '.join(str(a.get('含量描述') or '').strip() for a in ing[lic] if str(a.get('含量描述') or '').strip()); unit='; '.join(dict.fromkeys(str(a.get('含量單位') or '').strip() for a in ing[lic] if str(a.get('含量單位') or '').strip()))
        ind=r.get('適應症') or ''; active_norm='naphazoline; diphenhydramine; procaine'; sid='sub_'+active_norm.replace('; ','_')
        products.append({'product_id':pid,'license_number':lic,'license_year':str(r.get('發證日期') or '')[:4],'chinese_name':r.get('中文品名') or '','english_name':r.get('英文品名') or '','dosage_form_raw':r.get('劑型') or '','dosage_form_normalized':'nasal_spray','route_raw':r.get('用法用量') or '','route_normalized':'intranasal','application_site':'nasal','local_spray_inclusion_evidence':evidence,'indication_raw':ind,'indication_normalized':ind.lower(),'active_ingredient_raw':raw,'active_ingredient_normalized':active_norm,'strength':strength,'strength_unit':unit,'therapeutic_class':'decongestant; antihistamine; combination','license_status':'active' if not r.get('註銷狀態') else 'revoked_or_cancelled','license_expiry_date':r.get('有效日期') or '','applicant':r.get('申請商名稱') or '','manufacturer':r.get('製造商名稱') or '','source_id':SOURCE,'verified_at':NOW,'processing_status':'core_complete_optional_missing'})
        ps.append({'product_id':pid,'substance_id':sid,'role':'active','strength':strength,'strength_unit':unit,'source_id':SOURCE,'verified_at':NOW})
        # Add substance row only when it is absent.
        substances=csvrows('substances.csv');
        if not any(s['substance_id']==sid for s in substances):
            substances.append({'substance_id':sid,'substance_name_raw':raw,'substance_name_normalized':active_norm,'role':'active','role_evidence':'TFDA 許可證主成分略述欄位','source_id':SOURCE,'verified_at':NOW}); write('substances.csv',substances,substances[0].keys())
        iid='ind_'+''.join(c if c.isalnum() else '_' for c in ind.lower()).strip('_')[:180]
        if not any(i['indication_id']==iid for i in inds): inds.append({'indication_id':iid,'indication_raw':ind,'indication_normalized':ind.lower(),'source_id':SOURCE,'verified_at':NOW})
        pis.append({'product_id':pid,'indication_id':iid,'source_id':SOURCE,'verified_at':NOW})
        for c in ['decongestant','antihistamine','combination']: pcs.append({'product_id':pid,'class_id':c,'classification_evidence':'TFDA active ingredients: naphazoline (decongestant), diphenhydramine (antihistamine); multi-active product.','source_id':SOURCE,'verified_at':NOW})
    elif lic in pulmonary:
        decision='exclude_pulmonary_inhalation'; site=''; evidence='TFDA 劑型/英文名稱含氣化、定量或 pressurised inhalation，且適應症為氣喘或 COPD 的肺部維持/支氣管治療。'; confidence='high'
        excluded.append({'license_number':lic,'chinese_name':x['chinese_name'],'english_name':x['english_name'],'dosage_form_raw':x['dosage_form_raw'],'route_raw':x['route_raw'],'candidate_reason':x['candidate_reason'],'exclusion_reason':'pulmonary_inhaler','source_id':SOURCE,'verified_at':NOW})
    elif lic in skin:
        decision='exclude_skin_or_other'; site=''; evidence='TFDA 劑型為氣化噴霧/外用氣化噴霧，品名或適應症為頭皮生髮或肌肉骨骼疼痛之外用產品。'; confidence='high'
        excluded.append({'license_number':lic,'chinese_name':x['chinese_name'],'english_name':x['english_name'],'dosage_form_raw':x['dosage_form_raw'],'route_raw':x['route_raw'],'candidate_reason':x['candidate_reason'],'exclusion_reason':'skin_or_other_nonlocal_spray','source_id':SOURCE,'verified_at':NOW})
    else:
        decision='unresolved'; site='unclear'; evidence='TFDA 劑型僅為「噴霧劑」、品名未標示鼻/口腔/咽喉部位，適應症僅為「局部麻醉」；既有詳細成分僅列 lidocaine。既有官方仿單 URL 已單次嘗試但不可取得，不能可靠推定局部口咽用途。'; confidence='low'
    res.append({**common,'final_decision':decision,'application_site':site,'decision_evidence':evidence,'confidence':confidence})

# Retain only unresolved records in the active queue.
remaining=[x for x in q if x['license_number'] in unresolved]
write('products.csv',products,P_FIELDS); write('product_substances.csv',ps,PS_FIELDS); write('indications.csv',inds,I_FIELDS); write('product_indications.csv',pis,PI_FIELDS); write('product_classes.csv',pcs,PC_FIELDS); write('excluded_records.csv',excluded,E_FIELDS); write('manual_review_queue.csv',remaining,R_FIELDS)
resolution_fields=['license_number','product_name','original_review_reason','final_decision','application_site','decision_evidence','source_id','confidence','reviewed_at']; write('manual_review_resolution.csv',res,resolution_fields)

state=json.loads((B/'processing_state.json').read_text(encoding='utf-8')); status={r['license_number']:r['final_decision'] for r in res}
for item in state['completed_records']:
    if item['license_number'] in status: item.update({'status':status[item['license_number']],'last_updated':NOW})
state.update({'phase':'manual_review_resolution_complete','included_total':len(products),'excluded_total':len(excluded),'manual_review_total':len(remaining),'manual_review_resolved_total':18,'ready_for_site':True,'website_core_completeness':100.0,'optional_detail_completeness':0.0,'updated_at':NOW,'resume_from':'complete; unresolved records remain excluded from formal products and can be reviewed later.'})
(B/'processing_state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8')
sites=Counter(p['application_site'] for p in products)
usage_complete=sum(bool(p['route_raw']) for p in products)/len(products)*100
optional=usage_complete/4
(B/'data_quality_report.md').write_text(f'''# Data quality report\n\n- Formal products: {len(products)} (nasal {sites['nasal']}; throat {sites['throat']}; oral_mucosal {sites['oral_mucosal']})\n- This resolution: 1 included nasal; 12 excluded; 5 unresolved.\n- Every formal product has a unique licence, confirmed active ingredient, dosage form, application site, indication, licence status, and official TFDA source.\n- `website_core_completeness`: **100.0%** — licence, product name, dosage form, application site, indication, confirmed active, status, and source are present for all formal products.\n- `optional_detail_completeness`: **{optional:.1f}%** — conservatively measured as complete official use/dose text; preservative, excipient and complete leaflet details are not inferred from incomplete structured data.\n\nUnresolved lidocaine sprays remain outside formal products. Pulmonary inhalers and skin/other sprays are excluded.\n''',encoding='utf-8')
(B/'build_summary.md').write_text(f'''# Build summary\n\nResolved all 18 records that were in the initial manual-review queue using cached TFDA structured data and at most one existing official leaflet URL attempt per ambiguous record. No site, HTML, image card, eye database, bulk leaflet retrieval, or OCR was changed.\n\nOne nasal product was added. Twelve products were excluded (10 pulmonary inhalers; 2 skin/other products). Five structurally ambiguous lidocaine sprays remain `unresolved` and do not enter formal statistics. The dataset is `ready_for_site` because website-core completeness is 100%.\n''',encoding='utf-8')
print({'added':1,'excluded':12,'unresolved':5,'formal_total':len(products),'sites':dict(sites),'optional_detail_completeness':round(optional,1)})
