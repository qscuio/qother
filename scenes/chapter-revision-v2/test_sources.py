"""Fast source/archive checks; no scene imports, private assets, or network."""
import ast, hashlib, json, subprocess, sys, tempfile, unittest
from pathlib import Path
R = Path(__file__).resolve().parent
class Sources(unittest.TestCase):
    def test_python_and_json_parse(self):
        for p in R.rglob('*.py'): ast.parse(p.read_text(), filename=str(p.relative_to(R)))
        for p in R.rglob('*.json'): json.loads(p.read_text())
    def test_exact_source_hashes(self):
        for item in json.loads((R/'provenance.json').read_text())['sources']:
            self.assertEqual(hashlib.sha256((R/item['archive']).read_bytes()).hexdigest(), item['sha256'])
    def test_paragraph_source_bindings(self):
        manifest = json.loads((R/'paragraph-source-map.json').read_text())
        for row in manifest['sections'].values():
            for group in ['scene_sources','integration_sources']:
                for item in row[group].values():
                    self.assertEqual(hashlib.sha256((R/item['archive']).read_bytes()).hexdigest(),item['sha256'])
    def test_no_binary_payloads_or_private_identifiers(self):
        for p in R.rglob('*'):
            if not p.is_file() or '__pycache__' in p.parts: continue
            self.assertNotIn(p.suffix, ['.so','.o','.png','.jpg','.mp4','.wav','.npy','.npz'])
            # Construct tokens so the checker itself remains publishable.
            for token in ['/'+'workspace/', '/'+'tmp/', 'library_'+'file_id', 'cloud_browser_'+'handoff', 'sk-'+'proj-']:
                self.assertNotIn(token, p.read_text(), str(p.relative_to(R)))
    def test_public_frozen_text(self):
        ps=json.loads((R/'source/chapter_revision_v2/script/paragraphs.json').read_text())['paragraphs']
        script=(R/'source/chapter_revision_v2/script/script.md').read_text()
        self.assertEqual(len(ps),19)
        for row in ps: self.assertIn(row['text'].strip(),script)
        self.assertFalse((R/'source/chapter_revision_v2/timeline.json').exists())
        self.assertEqual(json.loads((R/'production-gate.template.json').read_text())['narration_cues'],{})
    def test_help_and_missing_input_failure(self):
        subprocess.run([sys.executable,str(R/'run.py'),'--help'],check=True,capture_output=True)
        with tempfile.TemporaryDirectory() as td:
            td=Path(td);f=td/'inputs.json';f.write_text('{}')
            result=subprocess.run([sys.executable,str(R/'run.py'),'setup','--private-inputs',str(f),'--repository-root',str(td/'missing-repository'),'--font',str(td/'missing-font'),'--runtime',str(td/'runtime')],capture_output=True)
            self.assertNotEqual(result.returncode,0)
            self.assertFalse((td/'runtime').exists())
if __name__=='__main__':unittest.main()
