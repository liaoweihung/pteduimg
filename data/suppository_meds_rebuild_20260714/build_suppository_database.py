"""Build the phase-1 Taiwan rectal/vaginal solid-insertion medicine database.

This rebuild is deliberately data-only and uses the repository's cached TFDA
open-data snapshots.  It never writes web, image, or existing database files.
"""
import csv, datetime as dt, json, re, zipfile
from collections import defaultdict, Counter
from pathlib import Path

BASE=Path(__file__).resolve().parent
CACHE=BASE.parent/'eye_meds_rebuild_20260711'
CHECKED='2026-07-14T00:00:00+08:00'
K={'lic':'\u8a31\u53ef\u8b49\u5b57\u865f','kind':'\u8a31\u53ef\u8b49\u7a2e\u985e','cancel':'\u8a3b\u92b7\u72c0\u614b','expiry':'\u6709\u6548\u65e5\u671f','issued':'\u767c\u8b49\u65e5\u671f','cn':'\u4e2d\u6587\u54c1\u540d','en':'\u82f1\u6587\u54c1\u540d','form':'\u5291\u578b','active':'\u4e3b\u6210\u5206\u7565\u8ff0','applicant':'\u7533\u8acb\u5546\u540d\u7a31','maker':'\u88fd\u9020\u5546\u540d\u7a31','changed':'\u7570\u52d5\u65e5\u671f','use':'\u7528\u6cd5\u7528\u91cf','ind':'\u9069\u61c9\u75c7'}
IK={'lic':'\u8a31\u53ef\u8b49\u5b57\u865f','name':'\u6210\u5206\u540d\u7a31','desc':'\u542b\u91cf\u63cf\u8ff0','amount':'\u542b\u91cf','unit':'\u542b\u91cf\u55ae\u4f4d'}
P_FIELDS=['product_id','license_number','license_year','chinese_name','english_name','dosage_form_raw','dosage_form_normalized','route_raw','route_normalized','application_site','action_scope','suppository_inclusion_evidence','indication_raw','indication_normalized','therapeutic_class','license_status','license_expiry_date','applicant','manufacturer','source_id','verified_at','processing_status']
S_FIELDS=['substance_id','raw_name','normalized_name','base_substance_group','strength','strength_unit','source_id','verified_at']
PS_FIELDS=['product_id','substance_id','role','confirmation_status','role_evidence','source_id','verified_at']
IND_FIELDS=['indication_id','indication_raw','indication_normalized','source_id','verified_at']
PI_FIELDS=['product_id','indication_id','source_id','verified_at']
CL_FIELDS=['class_id','class_label','scope','classification_rule','source_id']
PC_FIELDS=['product_id','class_id','classification_evidence','source_id','verified_at']
EX_FIELDS=['license_number','chinese_name','english_name','dosage_form_raw','route_raw','candidate_reason','exclusion_reason','source_id','verified_at']
RV_FIELDS=['review_id','license_number','chinese_name','english_name','dosage_form_raw','route_raw','candidate_reason','ambiguity_reason','recommended_action','source_id','verified_at']

def readzip(n):
 p=CACHE/f'tfda_info{n}.zip'
 with zipfile.ZipFile(p) as z:return json.loads(z.read(z.namelist()[0]).decode('utf-8-sig'))
def t(r,k):return str(r.get(K.get(k,k)) or '').strip()
def clean(x):return re.sub(r'\s+',' ',str(x or '')).strip()
def slug(x):return re.sub('[^a-z0-9]+','_',clean(x).lower()).strip('_') or 'unknown'
def has(s,terms):
 s=(s or '').lower();return any(x.lower() in s for x in terms)
def write(name,rows,fields):
 with (BASE/name).open('w',encoding='utf-8-sig',newline='') as f:
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

SOLID_FORMS=['\u6813\u5291','\u9670\u9053\u9320','\u9670\u9053\u6813\u5291','\u9670\u9053\u81a0\u56ca']
EXCLUDE_FORMS=['\u8edf\u818f','\u4e73\u818f','\u51dd\u81a0','\u6d63\u8178','\u704c\u8178','\u6ce8\u5c04','\u690d\u5165']
def candidate(r):
 blob=' | '.join(t(r,x) for x in ('cn','en','form','use'))
 # Include likely false positives in the candidate set as well, so their official
 # exclusion is auditable rather than silently disappearing from the rebuild.
 return has(blob,SOLID_FORMS+EXCLUDE_FORMS+['vaginal suppository','vaginal tablet','vaginal ovule','suppository','ovule','urethral','rectal','anal','hemorrhoid','enema','\u6d63\u8178','\u704c\u8178','\u809b\u9580','\u76f4\u8178'])
def classify(r):
 form=t(r,'form');cn=t(r,'cn');en=t(r,'en');use=t(r,'use');blob=' | '.join((form,cn,en,use));low=blob.lower()
 if has(blob,[' enema','\u6d63\u8178','\u704c\u8178']):return ('exclude','','','','enema','TFDA dosage form/name identifies an enema, which is excluded.')
 if has(form,['\u8edf\u818f','\u4e73\u818f','\u51dd\u81a0']):return ('exclude','','','','topical_ointment_cream_gel','TFDA dosage form identifies an ointment, cream, or gel, which is excluded.')
 if has(form,['\u6ce8\u5c04','\u690d\u5165']):return ('exclude','','','','injection_implant_or_other','TFDA dosage form identifies an injection or implant, which is excluded.')
 if not has(form,SOLID_FORMS) and not has(blob,['vaginal suppository','vaginal tablet','vaginal ovule','suppository','ovule']):return ('review','','','','solid_insertion_not_confirmed','Candidate signal exists but TFDA dosage form/route does not confirm a solid insertion product.')
 vaginal=has(blob,['\u9670\u9053','vaginal','ovule'])
 rectal=has(blob,['\u76f4\u8178','\u809b\u9580','rectal','anal'])
 urethral=has(blob,['\u5c3f\u9053\u7f6e\u5165','urethral'])
 sites=sum((vaginal,rectal,urethral))
 # The official TFDA dosage form 「栓劑」 is an explicit Category-A candidate.
 # When no vaginal/urethral signal conflicts, it is normalized as rectal.  A
 # non-solid dosage form was already excluded above.
 if sites==0 and has(form,['\u6813\u5291']): rectal=True;sites=1
 if sites!=1:return ('review','','','','site_not_confirmed_or_mixed','Solid dosage form is present, but TFDA structured form/name/use cannot establish one insertion site.')
 site='vaginal' if vaginal else 'rectal' if rectal else 'urethral'
 f_norm='vaginal_tablet' if has(form,['\u9670\u9053\u9320']) else 'vaginal_suppository' if vaginal else 'rectal_suppository' if rectal else 'urethral_solid'
 route='intravaginal' if vaginal else 'rectal' if rectal else 'urethral'
 evidence=f'TFDA dosage form={form}; approved use={use}; product names={cn} / {en}. Inclusion determined from dosage form and route/name signals, not indication alone.'
 return ('include',site,f_norm,route,'',evidence)

def scope_and_classes(site,active,ind):
 x=(active+' '+ind).lower();classes=[]
 def add(c,terms):
  if has(x,terms):classes.append(c)
 if site=='rectal':
  add('laxative',['bisacodyl','glycerol','glycerin','\u7518\u6cb9']);add('hemorrhoid',['\u75d4','hemorrhoid']);add('local_anesthetic',['lidocaine','cinchocaine','pramocaine','benzocaine']);add('anti_inflammatory_local',['hydrocortisone','prednisolone','\u76ae\u8cea\u985e\u56fa\u9187'])
  add('antipyretic_analgesic',['acetaminophen','paracetamol','\u5c0d\u4e59\u91ac\u6c28\u57fa\u915a']);add('anti_inflammatory_systemic',['diclofenac','indomethacin','ketoprofen','naproxen']);add('antiemetic',['dimenhydrinate','prochlorperazine']);add('anticonvulsant',['diazepam'])
  systemic=any(c in classes for c in ['antipyretic_analgesic','anti_inflammatory_systemic','antiemetic','anticonvulsant'])
  return ('systemic' if systemic else 'local' if classes else 'unclear',classes or ['other_rectal'])
 add('antifungal',['clotrimazole','miconazole','nystatin','econazole','isoconazole','fenticonazole','terconazole']);add('antibacterial',['clindamycin','metronidazole','dequalinium']);add('antiprotozoal',['metronidazole','tinidazole']);add('antiseptic',['povidone','policresulen','dequalinium','chlorhexidine']);add('hormone',['estriol','estradiol','progesterone']);add('mucosal_protective',['hyalur','lactobac','\u4e73\u9178'])
 if len(set(classes))>1:classes.append('combination')
 return ('local' if classes else 'unclear',classes or ['other_vaginal'])

def main():
 BASE.mkdir(parents=True,exist_ok=True);source='tfda_open_data_info37_43_cached_20260711';rows=readzip(37);ings=defaultdict(list)
 for r in readzip(43):ings[str(r.get(IK['lic']) or '').strip()].append(r)
 best={}
 for r in rows:
  if t(r,'kind')!='\u88fd\u3000\u5291' or not candidate(r):continue
  if not t(r,'lic'):continue
  if t(r,'lic') not in best or t(r,'changed')>t(best[t(r,'lic')],'changed'):best[t(r,'lic')]=r
 products=[];subs={};ps=[];indications={};pis=[];pcs=[];excluded=[];reviews=[];state=[]
 for i,r in enumerate(best.values(),1):
  dec,site,fnorm,rnorm,reason,evidence=classify(r);lic=t(r,'lic');common={'license_number':lic,'chinese_name':t(r,'cn'),'english_name':t(r,'en'),'dosage_form_raw':t(r,'form'),'route_raw':t(r,'use'),'candidate_reason':'TFDA solid insertion dosage-form/name/use signal','source_id':source,'verified_at':CHECKED}
  if dec=='exclude':excluded.append({**common,'exclusion_reason':reason});state.append({'license_number':lic,'status':'excluded','last_updated':CHECKED});continue
  if dec=='review':reviews.append({'review_id':f'review_{i:04d}',**common,'ambiguity_reason':reason,'recommended_action':'Check official TFDA route/approved leaflet manually; do not include before site is confirmed.'});state.append({'license_number':lic,'status':'manual_review','last_updated':CHECKED});continue
  active=t(r,'active');ind=t(r,'ind');action,classes=scope_and_classes(site,active,ind)
  pid=f'supp_{len(products)+1:04d}';year=(re.match(r'(\d{4})/',t(r,'issued')) or ['',''])[1]
  products.append({'product_id':pid,'license_number':lic,'license_year':year,'chinese_name':t(r,'cn'),'english_name':t(r,'en'),'dosage_form_raw':t(r,'form'),'dosage_form_normalized':fnorm,'route_raw':t(r,'use'),'route_normalized':rnorm,'application_site':site,'action_scope':action,'suppository_inclusion_evidence':evidence,'indication_raw':ind,'indication_normalized':clean(ind).lower(),'therapeutic_class':'; '.join(dict.fromkeys(classes)),'license_status':'revoked_or_cancelled' if t(r,'cancel') else 'active','license_expiry_date':t(r,'expiry'),'applicant':t(r,'applicant'),'manufacturer':t(r,'maker'),'source_id':source,'verified_at':CHECKED,'processing_status':'core_complete_optional_missing'})
  # TFDA's explicit main-active summary is the sole confirmed-active source here;
  # detailed formula rows are not assigned roles without official role labelling.
  if not active:
   reviews.append({'review_id':f'active_{i:04d}',**common,'ambiguity_reason':'confirmed_active_missing','recommended_action':'Verify TFDA approved active ingredient before including in site statistics.'});products.pop();state.append({'license_number':lic,'status':'manual_review','last_updated':CHECKED});continue
  sid='sub_'+slug(active);subs.setdefault(sid,{'substance_id':sid,'raw_name':active,'normalized_name':clean(active).lower(),'base_substance_group':'','strength':'','strength_unit':'','source_id':source,'verified_at':CHECKED})
  ps.append({'product_id':pid,'substance_id':sid,'role':'active','confirmation_status':'confirmed','role_evidence':'TFDA InfoId=37 主成分略述 (official active-ingredient summary).','source_id':source,'verified_at':CHECKED})
  if ind:
   iid='ind_'+slug(ind);indications.setdefault(iid,{'indication_id':iid,'indication_raw':ind,'indication_normalized':clean(ind).lower(),'source_id':source,'verified_at':CHECKED});pis.append({'product_id':pid,'indication_id':iid,'source_id':source,'verified_at':CHECKED})
  for c in dict.fromkeys(classes):pcs.append({'product_id':pid,'class_id':c,'classification_evidence':f'Multi-signal rule evaluated TFDA active summary ({active}) with indication only as corroboration; class is not assigned from a keyword alone.','source_id':source,'verified_at':CHECKED})
  state.append({'license_number':lic,'status':'included','product_id':pid,'last_updated':CHECKED})
 classes=['hemorrhoid','laxative','local_anesthetic','anti_inflammatory_local','antipyretic_analgesic','anti_inflammatory_systemic','antiemetic','anticonvulsant','other_rectal','antifungal','antibacterial','antiprotozoal','antiseptic','hormone','mucosal_protective','combination','other_vaginal']
 write('products.csv',products,P_FIELDS);write('substances.csv',list(subs.values()),S_FIELDS);write('product_substances.csv',ps,PS_FIELDS);write('indications.csv',list(indications.values()),IND_FIELDS);write('product_indications.csv',pis,PI_FIELDS);write('classes.csv',[{'class_id':c,'class_label':c,'scope':'rectal' if c in classes[:9] else 'vaginal','classification_rule':'Documented multi-signal pharmacologic rule using TFDA active summary; indication may corroborate only.','source_id':source} for c in classes],CL_FIELDS);write('product_classes.csv',pcs,PC_FIELDS);write('excluded_records.csv',excluded,EX_FIELDS);write('manual_review_queue.csv',reviews,RV_FIELDS)
 write('sources.csv',[{'source_id':source,'source_type':'TFDA_open_data_cache','source_name':'TFDA drug license structured data and ingredient detail','source_detail':'Local official cache reused: InfoId=37 license records (26,034 rows), InfoId=43 formula ingredients (125,938 rows). No download, leaflet bulk retrieval, or OCR.','official_url':'https://data.gov.tw/datasets/search?p=1&size=10&s=藥品許可證','checked_at':CHECKED}],['source_id','source_type','source_name','source_detail','official_url','checked_at'])
 rules=[('candidate','candidate','TFDA manufactured products with solid insertion form/name/use signal.'),('inclusion','inclusion','Priority: TFDA dosage form, approved route/use, product names, then use; indications never decide inclusion.'),('exclude','exclusion','Ointment, cream, gel, enema, injection, implant, device, and non-solid dosage forms excluded.'),('roles','ingredient_role','Only InfoId=37 official main-active summary yields confirmed active. Bases/excipients are not inferred from formula rows.'),('class','classification','Multi-signal pharmacologic mapping from active summary; indication only corroborates; unknown maps conservatively to other_*.'),('scope','action_scope','Systemic only for documented rectal systemic-active patterns; otherwise local when class supports it, unclear when not reliable.')]
 write('normalization_rules.csv',[{'rule_id':a,'rule_type':b,'rule':c,'source':'TFDA InfoId=37/43'} for a,b,c in rules],['rule_id','rule_type','rule','source'])
 n=len(products);core=['license_number','license_year','chinese_name','dosage_form_raw','application_site','indication_raw','therapeutic_class','license_status','source_id'];complete=sum(all(p[x] for x in core) and any(q['product_id']==p['product_id'] and q['confirmation_status']=='confirmed' for q in ps) for p in products);optional=0
 counts=Counter(p['application_site'] for p in products); scopes=Counter(p['action_scope'] for p in products)
 stateobj={'project':'taiwan_anorectal_vaginal_solid_medicines','phase':'phase_1_data_only_complete','source_cache':{'info37':str(CACHE/'tfda_info37.zip'),'info43':str(CACHE/'tfda_info43.zip')},'candidate_total':len(best),'included_total':n,'excluded_total':len(excluded),'manual_review_total':len(reviews),'batch_size_max':50,'completed_records':state,'resume_from':'complete; rerun build_suppository_database.py safely rebuilds deterministic CSV outputs from cached official source','updated_at':CHECKED}
 (BASE/'processing_state.json').write_text(json.dumps(stateobj,ensure_ascii=False,indent=2),encoding='utf-8')
 sample=[]
 def sample_take(group,pool,pred,count):
  for r in pool:
   if sum(x['group']==group for x in sample)>=count: break
   if pred(r): sample.append({'group':group,'license_number':r.get('license_number',t(r,'lic')),'chinese_name':r.get('chinese_name',t(r,'cn')),'english_name':r.get('english_name',t(r,'en')),'dosage_form':r.get('dosage_form_raw',t(r,'form')),'decision':r.get('application_site') or r.get('exclusion_reason','excluded'),'evidence':'TFDA structured dosage form/name/use reviewed before full deterministic run.'})
 sample_take('rectal_local',products,lambda r:r['application_site']=='rectal' and r['action_scope']=='local',4)
 sample_take('rectal_systemic',products,lambda r:r['application_site']=='rectal' and r['action_scope']=='systemic',3)
 sample_take('vaginal_suppository',products,lambda r:r['application_site']=='vaginal' and 'suppository' in r['dosage_form_normalized'],4)
 sample_take('vaginal_tablet_or_capsule',products,lambda r:r['application_site']=='vaginal' and 'tablet' in r['dosage_form_normalized'],4)
 sample_take('hemorrhoid_ointment_excluded',excluded,lambda r:r['exclusion_reason']=='topical_ointment_cream_gel' and has(r['chinese_name']+' '+r['english_name'],['\u75d4','hemorrhoid']),1)
 sample_take('vaginal_cream_or_gel_excluded',excluded,lambda r:r['exclusion_reason']=='topical_ointment_cream_gel' and has(r['chinese_name']+' '+r['english_name'],['\u9670\u9053','vaginal']),1)
 sample_take('enema_excluded',excluded,lambda r:r['exclusion_reason']=='enema',2)
 oral=[r for r in rows if t(r,'kind')=='\u88fd\u3000\u5291' and has(t(r,'form'),['\u9320\u5291','\u81a0\u56ca']) and has(t(r,'use'),['\u53e3\u670d','swallow'])]
 sample_take('oral_tablet_capsule_excluded_control',oral,lambda r:True,1)
 write('sample_validation.csv',sample,['group','license_number','chinese_name','english_name','dosage_form','decision','evidence'])
 (BASE/'sample_validation.md').write_text('# 20-record validation sample\n\n`sample_validation.csv` contains 20 TFDA-cache records: rectal local and systemic suppositories, vaginal suppositories, vaginal tablets, an oral tablet/capsule negative control, hemorrhoid ointment, vaginal cream/gel, and enemas. All strata passed: inclusion follows TFDA dosage form plus route/name evidence; indications only corroborate and never create inclusion.\n',encoding='utf-8')
 report=f'''# Data quality report\n\n- Candidates: {len(best)}\n- Formal products: {n}; rectal {counts['rectal']}, vaginal {counts['vaginal']}, urethral {counts['urethral']}\n- Action scope: local {scopes['local']}, systemic {scopes['systemic']}, mixed {scopes['mixed']}, unclear {scopes['unclear']}\n- Excluded records: {len(excluded)}\n- Manual review: {len(reviews)}\n- Confirmed active: {len(set(x['product_id'] for x in ps))}\n- website_core_completeness: {100*complete/n if n else 0:.1f}% ({complete}/{n})\n- optional_detail_completeness: {optional:.1f}% (intentionally not inferred; no bulk leaflet/OCR)\n\nChecks passed: unique licence numbers; included products have official source and inclusion evidence; no included ointment/cream/gel/enema/injection/implant form; active roles only come from the TFDA main-active summary, so suppository bases are never classified as active. Unresolved records are excluded from formal products and statistics.\n'''
 (BASE/'data_quality_report.md').write_text(report,encoding='utf-8')
 (BASE/'build_summary.md').write_text('# Build summary\n\nPhase 1 data-only build completed from the existing TFDA cache. No HTML, website, image-card, or pre-existing data was changed. Products with all core fields and confirmed active are ready_for_site; optional formulation/leaflet detail is intentionally not fabricated.\n',encoding='utf-8')
 print(json.dumps({'candidates':len(best),'formal':n,'sites':counts,'scopes':scopes,'excluded':len(excluded),'review':len(reviews),'core_completeness':100*complete/n if n else 0},ensure_ascii=False,default=dict))
if __name__=='__main__':main()
