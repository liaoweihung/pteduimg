"""Read-only checks for the mechanical export and explorer contract."""
import json
from collections import Counter
from pathlib import Path

B=Path(__file__).resolve().parent; root=B.parent.parent
j=json.loads((B/'final'/'suppository_meds_final.json').read_text(encoding='utf-8')); p=j['products']
assert len(p)==148==j['product_count']
assert Counter(x['application_site'] for x in p)=={'rectal':85,'vaginal':63}
assert Counter(x['action_scope'] for x in p)=={'local':83,'systemic':33,'unclear':32}
assert all(x['active_ingredients'] for x in p)
assert all(x['application_site'] in {'rectal','vaginal'} for x in p)
for bad in ('軟膏','乳膏','凝膠','浣腸','灌腸','注射','植入'):
    assert not any(bad in x['dosage_form'] for x in p),bad
def filt(**q):
    return [x for x in p if all(not v or (v in x.get(k,[]) if isinstance(x.get(k),list) else x.get(k)==v) for k,v in q.items())]
assert len(filt(application_site='rectal'))==85
assert len(filt(application_site='vaginal'))==63
assert len(filt(action_scope='local'))==83
assert len(filt(action_scope='systemic'))==33
assert any(filt(therapeutic_classes=c) for c in {z for x in p for z in x['therapeutic_classes']})
assert any(filt(indication_category=c) for c in {x['indication_category'] for x in p})
assert any(filt(active_ingredients='DICLOFENAC SODIUM'))
assert any('CLOTRIMAZOLE' in a for x in p for a in x['active_ingredients'])
counts=Counter(a for x in p for a in set(x['active_ingredients']))
assert counts['DICLOFENAC SODIUM']==24 and counts['CLOTRIMAZOLE']==21
assert any(len(x['active_ingredients'])>1 for x in p), 'combination actives were not split'
for path in (root/'suppository_medicine_explorer.html',root/'css'/'suppository-medicine-explorer.css',root/'js'/'suppository-medicine-explorer.js'):
    assert path.exists(),path
print('PASS: export counts, filters, active ranking, combination splitting, and required explorer assets.')
