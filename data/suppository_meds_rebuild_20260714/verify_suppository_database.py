"""Read-only quality checks for the phase-1 suppository dataset."""
import csv
from pathlib import Path

B=Path(__file__).resolve().parent
def rows(name):
    with (B/name).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
p=rows('products.csv'); ps=rows('product_substances.csv')
assert len(p)==len({x['license_number'] for x in p}), 'duplicate licence number'
assert all(x['application_site'] in {'rectal','vaginal','urethral','unclear'} for x in p)
assert all(x['action_scope'] in {'local','systemic','mixed','unclear'} for x in p)
assert all(x['suppository_inclusion_evidence'] and x['source_id'] for x in p)
assert all(not any(t in x['dosage_form_raw'] for t in ('軟膏','乳膏','凝膠','浣腸','灌腸','注射','植入')) for x in p)
active={x['product_id'] for x in ps if x['role']=='active' and x['confirmation_status']=='confirmed'}
assert all(x['product_id'] in active for x in p), 'formal product lacks confirmed active'
assert not any(any(t in x['role_evidence'].lower() for t in ('cocoa butter','hard fat','polyethylene glycol')) and x['role']=='active' for x in ps)
print(f'PASS: {len(p)} formal products, {len(active)} with confirmed active; no duplicate licences or excluded dosage forms.')
