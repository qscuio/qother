"""Source fingerprints and safe CLI failures; never encodes a complete preview."""
import ast,hashlib,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
D=Path(__file__).resolve().parent
ENV=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
class SourceTests(unittest.TestCase):
 def test_source_fingerprints(self):
  for item in json.loads((D/'provenance.json').read_text())['scripts']:
   data=(D/item['name']).read_bytes();ast.parse(data)
   self.assertEqual(hashlib.sha256(data).hexdigest(),item['portable_sha256'])
 def test_explicit_audio_required(self):
  with tempfile.TemporaryDirectory() as tmp:
   out=Path(tmp)/'new'
   r=subprocess.run([sys.executable,str(D/'render_preview.py'),'--output',str(out)],capture_output=True,text=True,env=ENV)
   self.assertEqual(r.returncode,2);self.assertIn('--audio is required',r.stderr);self.assertFalse(out.exists())
 def test_no_overwrite(self):
  with tempfile.TemporaryDirectory() as tmp:
   marker=Path(tmp)/'sentinel.txt';marker.write_text('keep')
   r=subprocess.run([sys.executable,str(D/'render_preview.py'),'--output',tmp,'--frame','288'],capture_output=True,text=True,env=ENV)
   self.assertEqual(r.returncode,2);self.assertEqual(marker.read_text(),'keep');self.assertEqual(len(list(Path(tmp).iterdir())),1)
 def test_estimated_cues_not_verified(self):
  j=json.loads((D/'estimated-timings.json').read_text())
  self.assertEqual(j['status'],'estimated_pause_based_not_ASR_verified');self.assertEqual(j['audio_speed'],1.0);self.assertEqual(j['audio_gain_db'],-1)
if __name__=='__main__':unittest.main()
