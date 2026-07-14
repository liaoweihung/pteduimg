"""Read-only invariant checks for the oral-liquid phase-2 export."""
import csv
from decimal import Decimal
from pathlib import Path
B=Path(__file__).resolve().parent
def rows(n):
 with (B/n).open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
p=rows('products.csv'); ps=rows('product_substances.csv')
resolutions=rows('manual_review_resolution.csv'); reviews=rows('manual_review_queue.csv')
assert len(p)==len({x['license_number'] for x in p}), 'duplicate licences'
assert all(x['route_normalized']=='oral' and x['oral_liquid_inclusion_evidence'] for x in p)
assert all(x['preparation_type'] in {'ready_to_use','requires_reconstitution'} for x in p)
assert all(x['product_id'] in {s['product_id'] for s in ps if s['role']=='active' and s['confirmation_status']=='confirmed'} for x in p)
assert not any(x['dosage_form_group']=='unclear' for x in p)
assert not any(any(term in x['dosage_form_raw'] for term in ('\u9320\u5291','\u81a0\u56ca')) for x in p), 'solid oral dosage form leaked into formal products'
required={'strength_raw','display_concentration','normalized_value_per_ml','normalization_status','parsing_rule','confidence'}
assert required <= set(ps[0]), 'phase-2 concentration fields missing'
assert len(resolutions)==439, 'phase-1 review baseline was not preserved'
assert sum(x['decision']=='unresolved' for x in resolutions)==len(reviews), 'unresolved queue mismatch'
assert not any(x['denominator_unit'] in {'bottle','sachet'} and x['normalized_value_per_ml'] for x in ps), 'container total converted to per mL'
products={x['product_id']:x for x in p}
assert not any(
 products[x['product_id']]['preparation_type']=='requires_reconstitution'
 and x['normalized_value_per_ml']
 and x['parsing_rule']!='explicit_post_reconstitution_volume'
 for x in ps
), 'reconstituted product normalized without explicit post-reconstitution evidence'
for x in ps:
 if x['normalization_status']=='parsed_per_ml' and x['denominator_unit']=='mL':
  expected=Decimal(x['numerator_value'])/Decimal(x['denominator_value'])
  assert expected==Decimal(x['normalized_value_per_ml']), 'incorrect per-mL arithmetic'
  if Decimal(x['denominator_value'])==5:
   assert '/5 mL' in x['display_concentration'], 'official 5-mL display basis was not preserved'
print(f'PASS: {len(p)} formal products, 439 review decisions, and concentration invariants verified.')
