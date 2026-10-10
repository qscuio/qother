"""Deterministic checks; synthetic pass fixtures do not certify an actual film."""
import copy,json,tempfile,unittest,subprocess,sys
from pathlib import Path
import validate_production_gate as v

def fixture():
 ps=[{'id':f'P{i:02}','text':f'Claim {i}.'} for i in range(1,20)]
 script=('# Exact chapter title\n\n'+'\n\n'.join(p['text'] for p in ps)+'\n').encode()
 paragraphs=json.dumps({'paragraphs':ps}).encode()
 inputs={k:v.sha(k.encode()) for k in v.INPUT_KEYS};inputs.update(script=v.sha(script),paragraphs=v.sha(paragraphs));d=v.digest(inputs)
 def passed():return {'status':'pass','reviewer_kind':'agent','reviewer':'synthetic-test-only','scope':'unit fixture','evidence':['E'],'input_digest':d}
 l={'schema_version':1,'status':'reviewed','identity':{'title':'Exact chapter title','script_sha256':v.sha(script)},'input_digest':d,'evidence':{'E':{'artifact_ref':'synthetic-test-only','artifact_sha256':v.sha(b'fixture'),'scope':'unit test','input_digest':d}},'labels':{k:{'title':'Exact chapter title','review':passed()} for k in ['cover','video_header']},'shots':{},'narration_cues':{},'paragraphs':[],'quality':{'benchmark_ref':'test-only'}}
 for p in ps:
  pid=p['id'];sid=pid+'-shot';cid=pid+'-cue'
  l['shots'][sid]={'paragraph_ids':[pid],'version':'test','content':passed(),'visual':passed(),'continuity':passed()}
  l['narration_cues'][cid]={'paragraph_id':pid,'source_text':p['text']}
  l['paragraphs'].append({'id':pid,'narration_cue_ids':[cid],'claims':[{'id':pid+'-claim','source_text':p['text'],'concepts':['test concept'],'visual_explanation':'test explanation','narration_cue_ids':[cid],'shot_ids':[sid],'semantic_review':passed()}]})
 for k in ['benchmark_comparison','input_completeness','technical','playback','audio_content']:l['quality'][k]=passed()
 l['final_artifact_evidence']='E'
 return l,script,paragraphs,inputs

class Gates(unittest.TestCase):
 def setUp(self):self.l,self.s,self.p,self.i=fixture()
 def check(self,gate='assembly'):return v.validate(self.l,self.s,self.p,self.i,gate,{'E':v.sha(b'fixture')},v.sha(b'fixture'))
 def test_consistency_only(self):self.assertFalse(self.check('final')['semantic_or_visual_truth_verified_by_script'])
 def test_title(self):
  self.l['labels']['video_header']['title']='Wrong';self.assertRaises(v.GateError,self.check)
 def test_missing_paragraph(self):
  self.l['paragraphs'].pop();self.assertRaises(v.GateError,self.check)
 def test_missing_claim(self):
  self.l['paragraphs'][0]['claims']=[];self.assertRaises(v.GateError,self.check)
 def test_dangling_shot(self):
  self.l['paragraphs'][0]['claims'][0]['shot_ids']=['missing'];self.assertRaises(v.GateError,self.check)
 def test_cue_ownership(self):
  self.l['paragraphs'][0]['claims'][0]['narration_cue_ids']=['P02-cue'];self.assertRaises(v.GateError,self.check)
 def test_technical_cannot_override_visual(self):
  self.l['shots']['P01-shot']['visual']['status']='fail';self.assertRaises(v.GateError,self.check)
 def test_unknown_not_pass(self):
  self.l['quality']['benchmark_comparison']['status']='unknown';self.assertRaises(v.GateError,self.check)
 def test_all_dependency_changes_invalidate(self):
  for key in v.INPUT_KEYS:
   with self.subTest(key=key):
    changed=dict(self.i);changed[key]=v.sha(b'changed')
    self.assertRaises(v.GateError,v.validate,self.l,self.s,self.p,changed)
 def test_stale_review(self):
  self.l['shots']['P01-shot']['visual']['input_digest']=v.sha(b'old');self.assertRaises(v.GateError,self.check)
 def test_stale_evidence(self):
  self.l['evidence']['E']['input_digest']=v.sha(b'old');self.assertRaises(v.GateError,self.check)
 def test_missing_actual_review(self):
  self.l['quality']['playback']['status']='not-run'
  self.check('assembly');self.assertRaises(v.GateError,self.check,'final')
 def test_rejected_history(self):
  self.l['status']='rejected-quality';self.assertRaises(v.GateError,self.check)
 def test_paragraph_source_binding(self):
  self.s=self.s.replace(b'Claim 1.',b'Other 1.');self.i['script']=v.sha(self.s)
  self.assertRaises(v.GateError,self.check)
 def test_pass_needs_evidence(self):
  self.l['shots']['P01-shot']['visual']['evidence']=[];self.assertRaises(v.GateError,self.check)
 def test_wrong_output_bytes(self):
  self.assertRaises(v.GateError,v.validate,self.l,self.s,self.p,self.i,'final',{'E':v.sha(b'fixture')},v.sha(b'other'))
 def test_changed_evidence_bytes(self):
  self.assertRaises(v.GateError,v.validate,self.l,self.s,self.p,self.i,'assembly',{'E':v.sha(b'other')})
 def test_no_actual_evidence(self):
  self.assertRaises(v.GateError,v.validate,self.l,self.s,self.p,self.i)
 def test_cli_live_dependencies_and_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'script').write_bytes(self.s);(root/'paragraphs').write_bytes(self.p);(root/'other').write_bytes(b'input');(root/'evidence').write_bytes(b'fixture')
   manifest={k:[{'id':k,'path':k if k in {'script','paragraphs'} else 'other'}] for k in v.INPUT_KEYS}
   inputs=v.snapshot(manifest,root);old=self.l['input_digest'];new=v.digest(inputs)
   def rebind(x):
    if isinstance(x,dict):return {k:new if k=='input_digest' else rebind(val) for k,val in x.items()}
    if isinstance(x,list):return [rebind(val) for val in x]
    return x
   ledger=rebind(self.l)
   for name,data in [('manifest',manifest),('ledger',ledger),('evidence-manifest',{'E':'evidence'}),('old-inputs',inputs)]: (root/name).write_text(json.dumps(data))
   cmd=[sys.executable,str(Path(v.__file__).resolve()),'check','--ledger',str(root/'ledger'),'--script',str(root/'script'),'--paragraphs',str(root/'paragraphs'),'--manifest',str(root/'manifest'),'--evidence-manifest',str(root/'evidence-manifest'),'--gate','final','--output-artifact',str(root/'evidence')]
   self.assertEqual(subprocess.run(cmd,capture_output=True).returncode,0)
   (root/'other').write_bytes(b'changed audio/assets/timeline/code')
   self.assertNotEqual(subprocess.run(cmd,capture_output=True).returncode,0)
   stale=cmd[:];i=stale.index('--manifest');stale[i:i+2]=['--inputs',str(root/'old-inputs')]
   self.assertNotEqual(subprocess.run(stale,capture_output=True).returncode,0)
 def test_snapshot_reads_actual_bytes(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/'input').write_text('one');m={k:[{'id':'one','path':'input'}] for k in v.INPUT_KEYS}
   a=v.snapshot(m,root);(root/'input').write_text('two');b=v.snapshot(m,root)
   self.assertTrue(all(a[k]!=b[k] for k in v.INPUT_KEYS))
if __name__=='__main__':unittest.main()
