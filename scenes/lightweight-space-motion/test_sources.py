"""Cheap source and CLI checks; no full video or image rendering."""
import ast, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
D=Path(__file__).resolve().parent
class SourceTests(unittest.TestCase):
    def test_syntax_and_hash(self):
        source=(D/'render_motion.py').read_bytes()
        ast.parse(source)
        self.assertEqual(hashlib.sha256(source).hexdigest(),json.loads((D/'validation.json').read_text())['portable_source_sha256'])
    def test_help(self):
        p=subprocess.run([sys.executable,str(D/'render_motion.py'),'--help'],capture_output=True,text=True)
        self.assertEqual(p.returncode,0)
        self.assertIn('--host-image',p.stdout)
    def test_output_guard(self):
        with tempfile.TemporaryDirectory() as tmp:
            sentinel=Path(tmp)/'keep.txt';sentinel.write_text('unchanged')
            p=subprocess.run([sys.executable,str(D/'render_motion.py'),'--output',tmp,'--frame','36'],capture_output=True,text=True)
            self.assertEqual(p.returncode,2)
            self.assertEqual(sentinel.read_text(),'unchanged')
            self.assertEqual(len(list(Path(tmp).iterdir())),1)
if __name__=='__main__':unittest.main()
