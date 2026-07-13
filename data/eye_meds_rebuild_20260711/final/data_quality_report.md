# Eye Meds Final Data Quality Report

- built_at: 2026-07-14T01:43:31+08:00
- products: 492
- JSON products: 492
- duplicate licenses: 0
- empty licenses: 0
- products missing substance relation: 0
- products missing indication relation: 0
- products missing source relation: 0
- confirmed active ingredient products: 461
- confirmed active ingredient products before unknown resolution: 449
- missing confirmed active products: 31
- missing confirmed active products before unknown resolution: 43
- unknown role relations resolved: 20
- unknown role relations remaining: 50
- unresolved due to role conflict/non-active support: 3
- only unknown ingredient products: 12
- only unknown ingredient products before unknown resolution: 24
- no ingredient relation products: 0
- indication raw completeness: 492/492
- dosage completeness: 492/492
- class completeness: 492/492
- license year completeness: 492/492
- conflict count: 0
- manual review count: 476
- substance role counts: {'active': 824, 'surfactant': 6, 'preservative': 154, 'tonicity_agent': 85, 'buffer': 88, 'unknown': 50, 'ph_adjuster': 22, 'vehicle': 46, 'ointment_base': 31, 'antioxidant': 5, 'viscosity_agent': 15, 'chelator': 14, 'other_excipient': 13}
- unknown resolution rule counts: {'D_same_formula_or_raw_component_pattern': 19, 'B_salt_or_base_group_active_only': 1}
- leaflet status counts: {'leaflet_unavailable': 426, 'available': 66}

## Conflict Handling
- Core product identity fields were retained unless enrichment had stronger confirmed evidence. No confirmed enrichment product-identity replacement was applied.
- OCR candidate values were not upgraded to confirmed.
- Unknown substance roles remain in the manual review queue unless the systematic confirmed-role dictionary resolved them with high confidence.
