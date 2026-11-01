import importlib.util
from pathlib import Path
import os
import tempfile
import unittest
spec = importlib.util.spec_from_file_location("repository_check", Path(__file__).with_name("verify_incremental_repository.py"))
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

class PreservationTests(unittest.TestCase):
    def test_unrelated_bytes_change_with_preserved_mtime(self):
        self.verify_rejection(True)

    def test_unrelated_mtime_change(self):
        self.verify_rejection(False)

    def verify_rejection(self, content):
        with tempfile.TemporaryDirectory(dir=check.build.ROOT / "outputs") as directory:
            root = Path(directory)
            (root / "cards").mkdir()
            page = root / "cards/unrelated.html"
            page.write_bytes(b"original")
            before = check.snapshot(root)
            stamp = before[page.name][1]
            if content:
                page.write_bytes(b"tampered")
            else:
                stamp += 2000000000
            os.utime(page, ns=(stamp, stamp))
            with self.assertRaisesRegex(AssertionError, "unrelated.html"):
                check.assert_unchanged(root, before, {"dependent.html"})
