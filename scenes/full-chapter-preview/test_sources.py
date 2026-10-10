"""Cheap text/provenance/CLI checks; no full video generation."""
import ast,copy,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
from validate_manifest import validate_manifest
D=Path(__file__).resolve().parent
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
class SourceTests(unittest.TestCase):
 def test_frozen_script(self):
  b=(D/'script/script.md').read_bytes();self.assertEqual(hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest(),'13a35f2b6a484c7ff33acd815611b68454a95e6f')
 def test_source_hashes(self):
  for row in json.loads((D/'provenance.json').read_text())['source_files']:
   data=(D/row['path']).read_bytes();ast.parse(data);self.assertEqual(hashlib.sha256(data).hexdigest(),row['portable_sha256'])
 def test_recorded_coverage(self):
  m=json.loads((D/'recorded/content_manifest.json').read_text());p=json.loads((D/'script/paragraphs.json').read_text())['paragraphs'];self.assertEqual(validate_manifest(m,p)['total_frames'],8584)
  bad=copy.deepcopy(m);bad['paragraphs'][0]['cues'][0]['text']='wrong'
  with self.assertRaises(ValueError):validate_manifest(bad,p)
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   sentinel=Path(tmp)/'keep.txt';sentinel.write_text('keep')
   p=subprocess.run([sys.executable,str(D/'run.py'),'frame','--output',tmp,'--timeline',str(D/'recorded-timeline.json')],capture_output=True,text=True,env=ENV)
   self.assertEqual(p.returncode,2);self.assertEqual(sentinel.read_text(),'keep');self.assertEqual(len(list(Path(tmp).iterdir())),1)
 def test_explicit_media_required(self):
  with tempfile.TemporaryDirectory() as tmp:
   output=Path(tmp)/'new'
   p=subprocess.run([sys.executable,str(D/'run.py'),'full','--output',str(output),'--timeline',str(D/'recorded-timeline.json')],capture_output=True,text=True,env=ENV)
   self.assertEqual(p.returncode,2);self.assertFalse(output.exists());self.assertIn('explicit --audio-dir and --p10-video',p.stderr)
if __name__=='__main__':unittest.main()
