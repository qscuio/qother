import ast, hashlib, json, unittest
from pathlib import Path
D=Path(__file__).resolve().parent
class SourceTests(unittest.TestCase):
    def test_chain_hashes(self):
        data=json.loads((D/'provenance.json').read_text())
        self.assertEqual(data['seed'],46109)
        for item in data['source_chain']:
            self.assertEqual(hashlib.sha256((D/item['file']).read_bytes()).hexdigest(),item['portable_sha256'])
    def test_syntax_and_no_private_payloads(self):
        for f in D.rglob('*.py'):
            s=f.read_text();ast.parse(s)
            for forbidden in ['/work'+'space/','library'+'_file_id','sk'+'-proj-']:
                self.assertNotIn(forbidden,s)
    def test_cameras(self):
        s=json.loads((D/'expected-settings.json').read_text())
        self.assertEqual(s['external_bitmaps_in_scene'],0)
        self.assertEqual(set(s['camera_views']),{'hero observer','independent side observer'})
        self.assertEqual(s['seed'],46109)
if __name__=='__main__': unittest.main()
