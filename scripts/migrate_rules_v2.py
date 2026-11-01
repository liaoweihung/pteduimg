"""One-time v1 -> v2 migration. Writes only rule columns and new evidence.

Run only after technical revalidation, with --apply. Never normalizes old CSV rows.
"""
import csv
import io
import json
from pathlib import Path
import subprocess
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import check_project_management as pm
from scripts import rule_fingerprints as rf


def migrate(root):
    path = root / pm.PM / 'page-inventory.csv'
    original = path.read_bytes()
    rows = list(csv.DictReader(io.StringIO(original.decode('utf-8-sig'))))
    if any('rules_version' in r for r in rows):
        raise ValueError('Already migrated; refusing to replace historical values')
    live, source_errors = pm.machine_snapshot(root, '2026-11-02')
    if source_errors:
        raise ValueError(source_errors)
    current = {r['page_id']:r for r in live}
    assert set(current) == {r['page_id'] for r in rows}
    values = rf.domains(root)
    cards = pm.read_json(root, 'cards.json')
    navigation = pm.read_json(root, 'data/acne_navigation.json')
    history = {r['page_id']:r['rules_sha256'] for r in rows}
    registry = {'version':2, 'source_revision':subprocess.check_output(
        ['git','rev-parse','HEAD'],cwd=root,text=True).strip(),
        'source_inventory_sha256': __import__('hashlib').sha256(original).hexdigest(),
        'v1_by_page':history,'v1_mapping_sha256':rf.digest(history),'domains':values}
    lines = original.splitlines(keepends=True)
    if len(lines) != len(rows)+1:
        raise ValueError('Multiline CSV requires reviewed cell-level migration')
    output=[]; changes=[]
    for index,line in enumerate(lines):
        ending=b'\r\n' if line.endswith(b'\r\n') else b'\n' if line.endswith(b'\n') else b''
        body=line[:-len(ending)] if ending else line
        if index==0:
            body+=b',rules_version,rules_v1_sha256'
        else:
            row=rows[index-1]; old=row['rules_sha256']
            new=rf.page_hash(current[row['page_id']],cards,navigation,root,values)
            token=b','+old.encode()+b','
            assert body.count(token)==1, row['page_id']
            body=body.replace(token,b','+new.encode()+b',',1)+b',2,'+old.encode()
            changes.append({'page_id':row['page_id'],'v1':old,'v2':new,
                            'domains':rf.applicable(current[row['page_id']],cards,navigation,root)})
        output.append(body+ending)
    proposed=b''.join(output)
    after=list(csv.DictReader(io.StringIO(proposed.decode('utf-8-sig'))))
    for before,next_row in zip(rows,after):
        assert all(before[k]==next_row[k] for k in before if k!='rules_sha256')
        assert next_row['rules_v1_sha256']==before['rules_sha256']
        assert next_row['rules_version']=='2'
    evidence=root/pm.PM/'evidence/rules-v2-migration-2026-11-02.json'
    assert not evidence.exists() and not (root/rf.MANIFEST).exists()
    (root/rf.MANIFEST).write_text(json.dumps(registry,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    path.write_bytes(proposed)
    evidence.write_text(json.dumps({'before_inventory_sha256':registry['source_inventory_sha256'],
        'source_revision':registry['source_revision'],'pages':len(rows),
        'changed_columns':['rules_sha256','rules_version','rules_v1_sha256'],
        'all_other_values_identical':True,'mapping':changes},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Migrated {len(rows)} pages; all pre-existing non-rule cells unchanged')

if __name__=='__main__':
    if sys.argv[1:]!=['--apply']:
        raise SystemExit('Requires --apply after technical revalidation')
    migrate(pm.ROOT)
