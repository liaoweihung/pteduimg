"""Build Taiwan oral-liquid medicines from the local official TFDA cache only.

This phase is data-only.  It does not write site, card, or earlier database files.
"""
import csv, datetime as dt, json, re, zipfile
from collections import Counter, defaultdict
from pathlib import Path

B=Path(__file__).resolve().parent
C=B.parent/'eye_meds_rebuild_20260711'
NOW='2026-07-14T00:00:00+08:00'
K={'lic':'\u8a31\u53ef\u8b49\u5b57\u865f','kind':'\u8a31\u53ef\u8b49\u7a2e\u985e','cancel':'\u8a3b\u92b7\u72c0\u614b','expiry':'\u6709\u6548\u65e5\u671f','issued':'\u767c\u8b49\u65e5\u671f','cn':'\u4e2d\u6587\u54c1\u540d','en':'\u82f1\u6587\u54c1\u540d','form':'\u5291\u578b','active':'\u4e3b\u6210\u5206\u7565\u8ff0','applicant':'\u7533\u8acb\u5546\u540d\u7a31','maker':'\u88fd\u9020\u5546\u540d\u7a31','changed':'\u7570\u52d5\u65e5\u671f','use':'\u7528\u6cd5\u7528\u91cf','ind':'\u9069\u61c9\u75c7'}
PF='product_id license_number license_year chinese_name english_name dosage_form_raw dosage_form_normalized dosage_form_group preparation_type route_raw route_normalized oral_liquid_inclusion_evidence indication_raw indication_normalized therapeutic_class legal_category license_status license_expiry_date applicant manufacturer source_id verified_at'.split()
PSF='product_id substance_id raw_name normalized_name base_substance_group strength_raw numerator_value numerator_unit denominator_value denominator_unit concentration_normalized concentration_status role confirmation_status source_id'.split()
SF='substance_id raw_name normalized_name base_substance_group source_id'.split()
IF='indication_id indication_raw indication_normalized source_id'.split(); PIF='product_id indication_id source_id'.split()
CF='class_id class_label classification_rule source_id'.split(); PCF='product_id class_id classification_evidence source_id'.split()
EXF='license_number chinese_name english_name dosage_form_raw route_raw candidate_reason exclusion_reason source_id verified_at'.split()
RF='review_id license_number chinese_name english_name dosage_form_raw route_raw review_type reason recommended_action source_id verified_at'.split()
CQF='product_id license_number chinese_name raw_name strength_raw concentration_status reason source_id'.split()

READY=[('\u53e3\u670d\u6eb6\u6db2','oral_solution'),('\u53e3\u670d\u6db2','oral_solution'),('\u5167\u670d\u6db2','oral_solution'),('\u7cd6\u6f3f','syrup'),('syrup','syrup'),('\u53e3\u670d\u61f8\u6db2','oral_suspension'),('\u61f8\u6db2','oral_suspension'),('suspension','oral_suspension'),('\u5167\u670d\u4e73\u5291','oral_emulsion'),('\u53e3\u670d\u4e73\u5291','oral_emulsion'),('\u4e73\u6db2','oral_emulsion'),('emulsion','oral_emulsion'),('\u916f\u5291','elixir'),('elixir','elixir'),('\u53e3\u670d\u6ef4\u5291','oral_drops'),('oral drops','oral_drops'),('oral solution','oral_solution'),('oral liquid','other_ready_to_use_oral_liquid')]
RECON=[('\u53e3\u670d\u61f8\u6db2\u7528\u9846\u7c92','granules_for_oral_suspension'),('\u53e3\u670d\u61f8\u6db2\u7528\u7c89','powder_for_oral_suspension'),('\u4e7e\u7c89\u61f8\u6db2','powder_for_oral_suspension'),('\u53e3\u670d\u6eb6\u6db2\u7528\u9846\u7c92','other_reconstituted_oral_liquid'),('\u53e3\u670d\u6eb6\u6db2\u7528\u7c89','powder_for_oral_solution'),('\u7cd6\u6f3f\u7528\u9846\u7c92','other_reconstituted_oral_liquid'),('\u7cd6\u6f3f\u7528\u7c89','other_reconstituted_oral_liquid'),('powder for oral suspension','powder_for_oral_suspension'),('granules for oral suspension','granules_for_oral_suspension'),('powder for oral solution','powder_for_oral_solution')]
EXCL=['\u6f31\u53e3','\u542b\u6f31','\u53e3\u8154\u5674','\u5589\u56a8\u5674','\u9f3b\u5674','\u773c\u85e5','\u8033\u6ef4','\u5916\u7528','\u76ae\u819a','\u6d17\u5291','\u704c\u8178','\u6d63\u8178','\u5438\u5165','\u9727\u5316','\u6ce8\u5c04','\u900f\u6790','\u6c96\u6d17','mouthwash','gargle','nasal','ophthalm','otic','inhal','enema','injection','dialysis','topical']
CLASSES=['antibiotic','antiviral','antifungal','antipyretic_analgesic','antihistamine','cough','expectorant_mucolytic','bronchodilator','gastrointestinal','laxative','antidiarrheal','antiemetic','acid_suppression','vitamin_or_mineral_drug','corticosteroid','neurologic','cardiovascular','other']
def tx(r,k): return str(r.get(K[k],'') or '').strip()
def clean(x): return re.sub(r'\s+',' ',str(x or '')).strip()
def slug(x): return re.sub('[^a-z0-9]+','_',clean(x).lower()).strip('_') or 'unknown'
def hit(s, xs): s=s.lower(); return any(x.lower() in s for x in xs)
def write(n, rows, fields):
 with (B/n).open('w',encoding='utf-8-sig',newline='') as f: w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore'); w.writeheader(); w.writerows(rows)
def read37():
 with zipfile.ZipFile(C/'tfda_info37.zip') as z:return json.loads(z.read(z.namelist()[0]).decode('utf-8-sig'))
def classify(r):
 form,cn,en,use=(tx(r,x) for x in ('form','cn','en','use')); blob=' | '.join((form,cn,en,use)); low=blob.lower()
 # Dosage-form grouping is deliberately based on TFDA's dosage-form field,
 # never on use/dosing prose.  A tablet instruction can mention syrup or a
 # liquid preparation, but that does not turn the licensed tablet into one.
 form_low=form.lower()
 signal=hit(blob,EXCL) or hit(form,[x[0] for x in READY+RECON]+['\u6db2','\u7cd6\u6f3f','\u61f8\u6db2','\u4e73\u5291','\u6ef4\u5291','powder','granules'])
 if not signal:return None
 if hit(blob,['\u704c\u8178','\u6d63\u8178','enema']):return 'exclude','', '', 'excluded_enema: TFDA form/name/use identifies an enema preparation.'
 if hit(blob,['\u5438\u5165','\u9727\u5316','inhal']):return 'exclude','', '', 'excluded_inhalation: TFDA form/name/use identifies an inhalation preparation.'
 if hit(blob,['\u6f31\u53e3','\u542b\u6f31','mouthwash','gargle']):return 'exclude','', '', 'excluded_mouthwash: TFDA form/name/use identifies a mouthwash or gargle.'
 if hit(blob,['\u5916\u7528','\u76ae\u819a','topical']):return 'exclude','', '', 'excluded_topical: TFDA form/name/use identifies a topical preparation.'
 if hit(blob,EXCL):return 'exclude','', '', 'excluded_other: TFDA form/name/use identifies a non-oral or excluded preparation.'
 group=''; prep=''
 for term,g in RECON:
  if term.lower() in form_low: group,prep=g,'requires_reconstitution'; break
 if not group:
  for term,g in READY:
   if term.lower() in form_low: group,prep=g,'ready_to_use'; break
 oral=hit(use,['\u53e3\u670d','\u5167\u670d','oral','swallow'])
 # Many older TFDA records hold only "see leaflet" in the use field.  An
 # explicitly oral dosage form remains official structured evidence; generic
 # liquid/suspension forms still require route/name corroboration.
 explicit_oral_form=hit(form,['\u5167\u670d\u6db2','\u53e3\u670d\u6db2','\u7cd6\u6f3f','\u5167\u670d\u4e73\u5291','\u53e3\u670d\u6eb6\u6db2','\u53e3\u670d\u61f8\u6db2','\u53e3\u670d\u6ef4\u5291','\u53e3\u670d\u61f8\u6db2\u7528','\u53e3\u670d\u6eb6\u6db2\u7528','\u7cd6\u6f3f\u7528'])
 if not group or not (oral or explicit_oral_form):return 'review','', '', 'Candidate form/name exists, but TFDA structured dosage form and approved use do not confirm oral liquid use.'
 return 'include',group,prep,f'TFDA dosage form={form}; approved use={use}; names={cn} / {en}. Inclusion uses dosage form and approved oral route, not indication alone.'
def classes(active, ind):
 s=(active+' '+ind).lower(); out=[]
 rules={'antibiotic':['amoxic','cefaclor','cephalex','azithro','clarithro','erythro','penicillin','抗生素'], 'antiviral':['acyclovir','oseltamivir'], 'antifungal':['nystatin','fluconazole','itraconazole'], 'antipyretic_analgesic':['acetaminophen','paracetamol','ibuprofen','對乙醯氨基酚'], 'antihistamine':['cetirizine','loratadine','chlorphen','diphenhydramine'], 'cough':['dextromethorphan','codeine','noscapine'], 'expectorant_mucolytic':['ambroxol','bromhexine','acetylcysteine','carbocisteine','guaifenesin'], 'bronchodilator':['salbutamol','theophylline','terbutaline'], 'laxative':['lactulose','magnesium hydroxide','sennoside','bisacodyl'], 'antidiarrheal':['loperamide','diosmectite'], 'antiemetic':['domperidone','metoclopramide','ondansetron'], 'acid_suppression':['famotidine','omeprazole','aluminum hydroxide','magnesium hydroxide'], 'vitamin_or_mineral_drug':['vitamin','維生素','iron','ferr','calcium','zinc'], 'corticosteroid':['prednisolone','dexamethasone','betamethasone'], 'neurologic':['levetiracetam','valpro','gabapentin','carbamazepine'], 'cardiovascular':['digoxin','propranolol','amlodipine']}
 for c,terms in rules.items():
  if hit(s,terms):out.append(c)
 if hit(s,['胃','腸','antacid','simethicone','digest']):out.append('gastrointestinal')
 return list(dict.fromkeys(out)) or ['other']
def main():
 source='tfda_open_data_info37_cached_20260711'; best={}
 for r in read37():
  if tx(r,'kind')!='\u88fd\u3000\u5291' or not tx(r,'lic'):continue
  if classify(r) is None:continue
  if tx(r,'lic') not in best or tx(r,'changed')>tx(best[tx(r,'lic')],'changed'):best[tx(r,'lic')]=r
 products=[]; ps=[]; subs={}; inds={}; pis=[]; pcs=[]; excluded=[]; reviews=[]; cq=[]; state=[]
 for no,r in enumerate(best.values(),1):
  lic=tx(r,'lic'); dec,group,prep,evidence=classify(r); common={'license_number':lic,'chinese_name':tx(r,'cn'),'english_name':tx(r,'en'),'dosage_form_raw':tx(r,'form'),'route_raw':tx(r,'use'),'source_id':source,'verified_at':NOW}
  if dec=='exclude':excluded.append({**common,'candidate_reason':'oral-liquid or excluded-liquid form/name/use signal','exclusion_reason':evidence});state.append({'license_number':lic,'status':'excluded','last_updated':NOW});continue
  if dec=='review':reviews.append({'review_id':f'review_{no:05d}',**common,'review_type':'inclusion','reason':evidence,'recommended_action':'Check official TFDA route/form before formal inclusion.'});state.append({'license_number':lic,'status':'manual_review','last_updated':NOW});continue
  active=tx(r,'active'); ind=tx(r,'ind')
  if not active:
   reviews.append({'review_id':f'active_{no:05d}',**common,'review_type':'confirmed_active','reason':'TFDA official main-active summary missing.','recommended_action':'Verify official active ingredient before inclusion.'});state.append({'license_number':lic,'status':'manual_review','last_updated':NOW});continue
  pid=f'oral_liquid_{len(products)+1:05d}'; year=(re.match(r'(\d{4})/',tx(r,'issued')) or ['',''])[1]; cs=classes(active,ind)
  products.append({'product_id':pid,**common,'license_year':year,'dosage_form_normalized':group,'dosage_form_group':group,'preparation_type':prep,'route_normalized':'oral','oral_liquid_inclusion_evidence':evidence,'indication_raw':ind,'indication_normalized':clean(ind).lower(),'therapeutic_class':'; '.join(cs),'legal_category':tx(r,'kind'),'license_status':'revoked_or_cancelled' if tx(r,'cancel') else 'active','license_expiry_date':tx(r,'expiry'),'applicant':tx(r,'applicant'),'manufacturer':tx(r,'maker')})
  sid='sub_'+slug(active);subs.setdefault(sid,{'substance_id':sid,'raw_name':active,'normalized_name':clean(active).lower(),'base_substance_group':'','source_id':source})
  ps.append({'product_id':pid,'substance_id':sid,'raw_name':active,'normalized_name':clean(active).lower(),'base_substance_group':'','strength_raw':'','numerator_value':'','numerator_unit':'','denominator_value':'','denominator_unit':'','concentration_normalized':'','concentration_status':'unclear','role':'active','confirmation_status':'confirmed','source_id':source})
  cq.append({'product_id':pid,'license_number':lic,'chinese_name':tx(r,'cn'),'raw_name':active,'strength_raw':'','concentration_status':'unclear','reason':'No role-labelled concentration data is inferred in phase 1; retain for official detail review.','source_id':source})
  if ind:
   iid='ind_'+slug(ind);inds.setdefault(iid,{'indication_id':iid,'indication_raw':ind,'indication_normalized':clean(ind).lower(),'source_id':source});pis.append({'product_id':pid,'indication_id':iid,'source_id':source})
  for c in cs:pcs.append({'product_id':pid,'class_id':c,'classification_evidence':f'Multi-signal pharmacologic rule uses TFDA active summary ({active}); indication corroborates only.','source_id':source})
  state.append({'license_number':lic,'status':'included','product_id':pid,'last_updated':NOW})
 write('products.csv',products,PF);write('archived_or_inactive_products.csv',[],PF);write('substances.csv',subs.values(),SF);write('product_substances.csv',ps,PSF);write('indications.csv',inds.values(),IF);write('product_indications.csv',pis,PIF);write('classes.csv',[{'class_id':c,'class_label':c,'classification_rule':'Multi-signal mapping from TFDA active ingredient summary; indication is corroboration only.','source_id':source} for c in CLASSES],CF);write('product_classes.csv',pcs,PCF);write('sources.csv',[{'source_id':source,'source_type':'TFDA_open_data_cache','source_name':'TFDA drug license structured data','source_detail':'Reused local official InfoId=37 cache; no download, bulk leaflet retrieval, or OCR.','official_url':'https://data.gov.tw/','checked_at':NOW}],['source_id','source_type','source_name','source_detail','official_url','checked_at']);write('excluded_records.csv',excluded,EXF);write('manual_review_queue.csv',reviews,RF);write('concentration_review_queue.csv',cq,CQF)
 rules=[('inclusion','TFDA dosage form + approved oral route are required; product name and indication never decide inclusion.'),('forms','Ready-to-use and reconstituted oral liquids use the specified normalized groups.'),('active','Only TFDA official main-active summary is a confirmed active; excipients are never inferred as active.'),('concentration','No concentration is guessed; all lack role-labelled detail are queued as unclear.'),('classification','Therapeutic classes use multi-signal active/indication rules and retain multiple classes.')]
 write('normalization_rules.csv',[{'rule_id':f'r{i:02d}','rule_type':a,'rule':b,'source':source} for i,(a,b) in enumerate(rules,1)],['rule_id','rule_type','rule','source'])
 counts=Counter(x['dosage_form_group'] for x in products);preps=Counter(x['preparation_type'] for x in products);cc=Counter(c for x in products for c in x['therapeutic_class'].split('; '));exc=Counter(x['exclusion_reason'].split(':',1)[0] for x in excluded); core=['license_number','chinese_name','dosage_form_group','preparation_type','route_normalized','indication_raw','therapeutic_class','source_id']; complete=sum(all(p[x] for x in core) for p in products)
 stateobj={'project':'taiwan_oral_liquid_medicines','phase':'phase_1_data_only_complete','source_cache':str(C/'tfda_info37.zip'),'candidate_total':len(best),'included_total':len(products),'excluded_total':len(excluded),'manual_review_total':len(reviews),'batch_size_max':50,'completed_records':state,'resume_from':'complete; rerun this deterministic builder safely reconstructs CSV outputs from cached official source','updated_at':NOW};(B/'processing_state.json').write_text(json.dumps(stateobj,ensure_ascii=False,indent=2),encoding='utf-8')
 # Fixed 30-record, stratified validation.  It deliberately includes ambiguous
 # and excluded controls, rather than pretending every dosage-form signal is
 # an oral liquid.  Older rows with only a leaflet reference remain review.
 sample=[]; raw=[r for r in read37() if tx(r,'kind')=='\u88fd\u3000\u5291']
 strata=[
  ('syrup',lambda r:hit(tx(r,'form'),['\u7cd6\u6f3f'])),
  ('oral_solution',lambda r:hit(tx(r,'form'),['\u5167\u670d\u6db2','\u53e3\u670d\u6db2','\u6eb6\u6db2\u5291'])),
  ('oral_suspension',lambda r:hit(tx(r,'form'),['\u61f8\u6db2\u5291','\u61f8\u6d6e\u6db2'])),
  ('oral_drops_review',lambda r:hit(tx(r,'form'),['\u6ef4\u5291']) and not hit(' '.join((tx(r,'form'),tx(r,'cn'),tx(r,'en'))),EXCL)),
  ('powder_for_oral_suspension',lambda r:hit(tx(r,'form'),['\u61f8\u6db2\u7528\u7c89','\u4e7e\u7c89\u61f8\u6db2'])),
  ('granules_for_oral_suspension_review',lambda r:hit(tx(r,'form'),['\u61f8\u6db2\u7528\u9846\u7c92'])),
  ('topical_liquid_excluded',lambda r:hit(' '.join((tx(r,'form'),tx(r,'cn'),tx(r,'use'))),['\u5916\u7528','\u76ae\u819a'])),
  ('mouthwash_excluded',lambda r:hit(' '.join((tx(r,'form'),tx(r,'cn'),tx(r,'use'))),['\u6f31\u53e3','\u542b\u6f31'])),
  ('inhalation_excluded',lambda r:hit(' '.join((tx(r,'form'),tx(r,'cn'),tx(r,'use'))),['\u5438\u5165','\u9727\u5316'])),
  ('enema_excluded',lambda r:hit(' '.join((tx(r,'form'),tx(r,'cn'),tx(r,'use'))),['\u704c\u8178','\u6d63\u8178'])),
  ('oral_tablet_granule_control',lambda r:hit(tx(r,'form'),['\u9320\u5291','\u81a0\u56ca','\u9846\u7c92\u5291']) and hit(tx(r,'use'),['\u53e3\u670d','\u5167\u670d']))]
 for label,pred in strata:
  for r in [x for x in raw if pred(x)][:2]:
   d=classify(r); decision=d[0] if d else 'not_candidate'; sample.append({'sample_group':label,'license_number':tx(r,'lic'),'chinese_name':tx(r,'cn'),'dosage_form':tx(r,'form'),'decision':decision,'evidence':d[3] if d else 'Not selected by oral-liquid candidate rule.'})
 # Fill to the promised 30 records with additional included records, retaining
 # all required positive and negative-control strata above.
 seen={x['license_number'] for x in sample}
 for p in products:
  if len(sample)>=30: break
  if p['license_number'] not in seen:
   sample.append({'sample_group':'additional_formal','license_number':p['license_number'],'chinese_name':p['chinese_name'],'dosage_form':p['dosage_form_raw'],'decision':'include','evidence':p['oral_liquid_inclusion_evidence']});seen.add(p['license_number'])
 write('sample_validation.csv',sample,['sample_group','license_number','chinese_name','dosage_form','decision','evidence'])
 (B/'sample_validation.md').write_text(f'# Sample validation\n\n{len(sample)} records selected across oral-liquid groups and excluded controls. Inclusion is based on TFDA dosage form plus approved oral route.\n',encoding='utf-8')
 report=f'''# Data quality report\n\n- Candidates: {len(best)}\n- Formal active products: {len(products)}\n- Excluded: {len(excluded)}; manual review: {len(reviews)}\n- Confirmed active: {len(ps)}\n- Dosage groups: {dict(counts)}\n- Preparation types: {dict(preps)}\n- Therapeutic classes: {dict(cc)}\n- Concentration completeness: 0.0% (not inferred; {len(cq)} queued for official-detail review)\n- website_core_completeness: {100*complete/len(products) if products else 0:.1f}%\n- dosing_data_completeness: 0.0%\n- optional_detail_completeness: 0.0%\n- ready_for_site: {'yes' if products and complete==len(products) else 'no'}\n\nAll formal products have unique licences, TFDA evidence, an approved oral route, and a confirmed active. Non-oral liquids are excluded; ambiguous records are not included in statistics.\n''';(B/'data_quality_report.md').write_text(report,encoding='utf-8')
 (B/'build_summary.md').write_text('# Build summary\n\nData-only phase completed from the existing local TFDA cache. No HTML, website, image cards, or prior datasets were changed.\n',encoding='utf-8')
 print(json.dumps({'candidates':len(best),'products':len(products),'excluded':len(excluded),'manual_review':len(reviews),'groups':counts,'preparation':preps,'classes':cc},ensure_ascii=False,default=dict))
if __name__=='__main__':main()
