"""Build the compact, browser-ready relationship analysis for the TCM explorer."""
from __future__ import annotations
import json, re
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]; DATA=ROOT/'data'/'tcm_formula_explorer'
RULES={
 '婦科相關':['月經','經期','白帶','產後','胎','婦人','乳'],
 '消化不適':['胃','脾','腹','食少','嘔','吐','瀉','便','消化','腸'],
 '感冒／呼吸道':['感冒','咳','喘','痰','鼻','咽','喉','肺','氣管'],
 '睡眠／神經':['失眠','睡','神經','頭暈','眩暈','頭痛','驚悸','癲','癇'],
 '筋骨疼痛':['痛','痠','腰','關節','風濕','跌打','骨','筋'],
 '泌尿／腎臟':['尿','腎','膀胱','水腫','淋'],
 '皮膚／外傷':['皮','瘡','癢','疹','傷','腫','燙'],
}
EXCLUDE={'乳糖','澱粉','硬脂酸鎂','蜂蜜','蔗糖','膠囊殼','明膠','二氧化矽','賦形劑','色素','香料'}
ALIASES={'甘草':'炙甘草','生薑':'薑','炮附子':'附子','製半夏':'半夏','山梔子':'梔子','北五味子':'五味子'}
def cats(text): return [k for k,words in RULES.items() if any(w in text for w in words)] or ['其他／待整理']
def norm(v):
 v=re.sub(r'（.*?）|\(.*?\)','',v); v=re.sub(r'\s*\d+(?:\.\d+)?\s*(?:mg|g|公克).*','',v,flags=re.I).strip(' ：:、,;；')
 return ALIASES.get(v,v)
def meds(text):
 out=[]
 for line in text.splitlines():
  v=norm(line.split('(')[0])
  if v and len(v)<16 and not any(x in v for x in EXCLUDE) and not v.startswith(('處方','每','本品')): out.append(v)
 return list(dict.fromkeys(out))
def main():
 formulas=json.loads((DATA/'formulas.json').read_text(encoding='utf-8'))['formulas']
 formula_ings={k:meds(v.get('ingredients','').replace('、','\n')) for k,v in formulas.items()}
 cat=defaultdict(lambda:{'products':set(),'formulas':set(),'ingredients':Counter(),'combos':Counter(),'evidence':[]})
 ing=defaultdict(lambda:{'products':set(),'formulas':set(),'categories':Counter(),'co':Counter(),'evidence':[],'representatives':[]})
 for f in sorted(DATA.glob('products-*.json')):
  for p in json.loads(f.read_text(encoding='utf-8'))['products']:
   cs=cats(p.get('indications','')); xs=meds(p.get('prescription','')) or formula_ings.get(p.get('formulaId'),[])
   fid=p.get('formulaId'); key=p['license']; combo='＋'.join(sorted(xs)[:4])
   for c in cs:
    x=cat[c]; x['products'].add(key); x['formulas'].add(fid) if fid else None; x['ingredients'].update(xs); x['combos'][combo]+=1 if combo else 0
    if len(x['evidence'])<5:x['evidence'].append({'license':key,'name':p.get('name',''),'indications':p.get('indications','')})
   for a in xs:
    x=ing[a];x['products'].add(key);x['formulas'].add(fid) if fid else None;x['categories'].update(cs);x['co'].update(b for b in xs if b!=a)
    if len(x['evidence'])<4:x['evidence'].append(p.get('indications',''))
    if len(x['representatives'])<4:x['representatives'].append({'name':p.get('name',''),'license':key,'formula':p.get('formula','')})
 def top(c,n=12):return [{'name':a,'count':b} for a,b in c.most_common(n) if a]
 result={'metadata':{'productCount':21196,'formulaCount':204,'notice':'適應症大類與藥材關聯為透明規則的資料分析，不取代官方適應症或處方原文。'},'rules':RULES,'categories':{},'ingredients':{}}
 for k,v in cat.items():result['categories'][k]={'productCount':len(v['products']),'formulaCount':len(v['formulas']),'ingredients':top(v['ingredients']),'combinations':top(v['combos'],8),'evidence':v['evidence']}
 for k,v in ing.items():result['ingredients'][k]={'productCount':len(v['products']),'formulaCount':len(v['formulas']),'categories':top(v['categories'],6),'cooccurring':top(v['co'],10),'evidence':v['evidence'],'representatives':v['representatives']}
 (DATA/'relationship_analysis.json').write_text(json.dumps(result,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
 print(len(result['ingredients']),len(result['categories']))
if __name__=='__main__':main()
