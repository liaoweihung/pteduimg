"""Mutation tests for scoped rule invalidation; all writes are disposable."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import rule_fingerprints as rf
ROOT = Path(__file__).resolve().parents[1]
FILES = ['build.py', 'scripts/rule_fingerprints.py', 'scripts/incremental_build.py',
         'scripts/card_archive.py', 'scripts/site_header.py', 'scripts/site_footer.py',
         'scripts/acne_pilot.py', 'templates/site-footer.html', 'data/acne_navigation.json', 'css/base.css']

class ScopedRulesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / 'outputs')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for name in FILES:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        self.before = rf.domains(self.root)

    def change(self, name, old, new):
        path = self.root / name
        text = path.read_text(encoding='utf-8')
        self.assertIn(old, text)
        path.write_text(text.replace(old, new, 1), encoding='utf-8')
        return rf.domains(self.root)

    def test_sitemap_only_invalidates_global(self):
        after = self.change('build.py', '("", "weekly", "1.0")', '("", "daily", "1.0")')
        self.assertNotEqual(self.before['global'], after['global'])
        self.assertEqual(self.before['page'], after['page'])
        self.assertEqual(self.before['pilot'], after['pilot'])

    def test_footer_invalidates_actual_consumers(self):
        after = self.change('templates/site-footer.html', '<footer', '<footer data-test="changed"')
        self.assertNotEqual(self.before['footer'], after['footer'])
        row = {'page_id':'ordinary', 'page_path':'cards/ordinary.html', 'primary_series_id':'s', 'visibility':'current'}
        cards = {'s':{'showFooter':True}}
        nav = {'pages':[]}
        self.assertNotEqual(rf.page_hash(row,cards,nav,self.root,self.before),rf.page_hash(row,cards,nav,self.root,after))
        cards['s']['showFooter'] = False
        self.assertEqual(rf.page_hash(row,cards,nav,self.root,self.before),rf.page_hash(row,cards,nav,self.root,after))

    def test_pilot_does_not_invalidate_general_or_acne_topic(self):
        after = self.change('scripts/acne_pilot.py', '.acne-next { margin:22px', '.acne-next { margin:23px')
        self.assertNotEqual(self.before['pilot'], after['pilot'])
        self.assertEqual(self.before['acne_topic'], after['acne_topic'])
        self.assertEqual(self.before['page'], after['page'])
        row={'page_id':'p','page_path':'cards/p.html','primary_series_id':'s','visibility':'current'}
        cards={'s':{}}; nav={'pages':[]}
        self.assertEqual(rf.page_hash(row,cards,nav,self.root,self.before),rf.page_hash(row,cards,nav,self.root,after))
        nav['pages']=[{'page_id':'p'}]
        self.assertNotEqual(rf.page_hash(row,cards,nav,self.root,self.before),rf.page_hash(row,cards,nav,self.root,after))

    def test_page_renderer_change_is_not_missed(self):
        after=self.change('build.py','<nav class="page-nav"','<nav data-test="changed" class="page-nav"')
        self.assertNotEqual(self.before['page'],after['page'])

    def test_transitive_helper_change_is_not_missed(self):
        after=self.change('build.py','def esc(value):','def esc(value):\n    value = str(value)')
        self.assertNotEqual(self.before['page'],after['page'])

    def test_missing_root_fails_closed(self):
        with self.assertRaises(ValueError):
            rf.closure(self.root,'build.py',['missing_function'])


class MigrationTests(unittest.TestCase):
    def test_only_rule_cells_change_and_reentry_is_rejected(self):
        from unittest.mock import patch
        from scripts import migrate_rules_v2 as migration
        from scripts import check_project_management as pm
        import io
        with tempfile.TemporaryDirectory(dir=ROOT/'outputs') as directory:
            root=Path(directory)
            (root/pm.PM/'evidence').mkdir(parents=True)
            (root/'data').mkdir()
            (root/'cards.json').write_text('{"s":{}}',encoding='utf-8')
            (root/'data/acne_navigation.json').write_text('{"pages":[]}',encoding='utf-8')
            row={'page_id':'p','page_path':'cards/p.html','visibility':'current',
                 'primary_series_id':'s','rules_sha256':'a'*64,
                 'medical_review_status':'conflict','content_sha256':'content',
                 'source_sha256':'source','known_issue_ids':'CR-2026-001'}
            target=root/pm.PM/'page-inventory.csv'
            buf=io.StringIO(newline=''); writer=csv.DictWriter(buf,fieldnames=list(row));writer.writeheader();writer.writerow(row)
            target.write_bytes(b'\xef\xbb\xbf'+buf.getvalue().encode())
            values={'page':'p','engine':'e'}
            with patch.object(pm,'machine_snapshot',return_value=([row],[])), \
                 patch.object(rf,'domains',return_value=values), \
                 patch.object(migration.subprocess,'check_output',return_value='revision\n'):
                migration.migrate(root)
                after=list(csv.DictReader(io.StringIO(target.read_text(encoding='utf-8-sig'))))[0]
                self.assertTrue(all(after[k]==v for k,v in row.items() if k!='rules_sha256'))
                self.assertEqual(after['rules_v1_sha256'],row['rules_sha256'])
                self.assertEqual(after['rules_version'],'2')
                registry=json.loads((root/rf.MANIFEST).read_text(encoding='utf-8'))
                self.assertEqual(registry['v1_by_page'],{'p':'a'*64})
                with self.assertRaisesRegex(ValueError,'Already migrated'):
                    migration.migrate(root)

class RegistryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from scripts import check_project_management as pm
        cls.pm=pm
        cls.model=pm.load_model(ROOT)
        cls.live,cls.source_errors=pm.machine_snapshot(ROOT,'2026-11-02')

    def test_all_v1_values_match_original_git_revision(self):
        import io,subprocess
        registry=json.loads((ROOT/rf.MANIFEST).read_text(encoding='utf-8'))
        raw=subprocess.check_output(['git','show',registry['source_revision']+':docs/project-management/page-inventory.csv'],cwd=ROOT)
        import hashlib
        # The archive records exact pre-migration checkout bytes, while Git stores LF.
        lf = raw.replace(b'\r\n', b'\n')
        self.assertIn(registry['source_inventory_sha256'],
                      {hashlib.sha256(lf).hexdigest(), hashlib.sha256(lf.replace(b'\n', b'\r\n')).hexdigest()})
        original={r['page_id']:r['rules_sha256'] for r in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))}
        self.assertEqual(original,registry['v1_by_page'])
        self.assertEqual(original,{r['page_id']:r['rules_v1_sha256'] for r in self.model['inventory']})

    def test_global_domain_drift_is_a_real_validation_error(self):
        from unittest.mock import patch
        values=rf.domains(ROOT);values['global']='changed'
        with patch.object(rf,'domains',return_value=values):
            errors,_=self.pm.validate(ROOT,self.model,self.live)
        self.assertIn('rules-v2: domain drift: global',errors)

    def test_history_cell_tampering_is_rejected(self):
        model=copy.deepcopy(self.model)
        model['inventory'][0]['rules_v1_sha256']='0'*64
        errors,_=self.pm.validate(ROOT,model,self.live)
        self.assertIn(model['inventory'][0]['page_id']+': machine field drift: rules_v1_sha256',errors)

if __name__ == '__main__': unittest.main()
