"""Explicit EOL modes must never hide substantive report changes or missing evidence."""
import hashlib
from pathlib import Path
import sys,tempfile,unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import check_project_management as pm
class ReportHashTests(unittest.TestCase):
    def test_only_declared_lf_mode_accepts_crlf(self):
        with tempfile.TemporaryDirectory(dir=pm.ROOT/'outputs') as tmp:
            root=Path(tmp);p=root/'report';p.write_bytes(b'one\ntwo\n')
            row={'path':'report'};raw=pm.audit_report_hash(root,row)
            p.write_bytes(b'one\r\ntwo\r\n')
            self.assertNotEqual(pm.audit_report_hash(root,row),raw)
            row['sha256_normalization']='lf'
            self.assertEqual(pm.audit_report_hash(root,row),raw)
            p.write_bytes(b'one\r\nchanged\r\n')
            self.assertNotEqual(pm.audit_report_hash(root,row),raw)
    def test_missing_and_invalid_modes_cannot_pass(self):
        with tempfile.TemporaryDirectory(dir=pm.ROOT/'outputs') as tmp:
            root=Path(tmp);row={'path':'missing','sha256_normalization':'lf'}
            self.assertEqual(pm.audit_report_hash(root,row),'missing')
            (root/'missing').write_bytes(b'data');row['sha256_normalization']='ignore'
            self.assertEqual(pm.audit_report_hash(root,row),'invalid-normalization')

class HistoricalSnapshotTests(unittest.TestCase):
    def test_changed_archived_bytes_are_reported(self):
        import copy
        model=pm.load_model(pm.ROOT)
        live,errors=pm.machine_snapshot(pm.ROOT,'2026-11-02')
        row=next(a for a in model['audits']['reports'] if a['audit_id']=='AUD-007')
        prior=next(a for a in row['previous_versions'] if a.get('preserved_snapshot'))
        prior['sha256']='0'*64
        found,_=pm.validate(pm.ROOT,model,live)
        self.assertIn('AUD-007: historical snapshot hash mismatch',found)
