"""Mechanical production-ledger consistency. Never evaluates image quality or spoken meaning."""
import argparse,hashlib,json,re
from pathlib import Path

INPUT_KEYS={'script','paragraphs','audio','assets','timeline','storyboard','render_code'}
STATUSES={'pass','fail','not-run','blocked'}
class GateError(ValueError):pass

def sha(data):return hashlib.sha256(data).hexdigest()
def require(ok,message):
 if not ok:raise GateError(message)
def text(value):return isinstance(value,str) and bool(value.strip())
def digest(inputs):
 require(isinstance(inputs,dict) and set(inputs)==INPUT_KEYS,'inputs must name exactly script, paragraphs, audio, assets, timeline, storyboard, render_code')
 require(all(isinstance(v,str) and re.fullmatch('[0-9a-f]{64}',v) for v in inputs.values()),'each input fingerprint must be lowercase SHA-256')
 return sha(json.dumps(inputs,sort_keys=True,separators=(',',':')).encode())
def snapshot(manifest,root):
 """Hash explicit local dependencies by stable logical IDs. No network or credential lookup."""
 require(isinstance(manifest,dict) and set(manifest)==INPUT_KEYS,'snapshot manifest needs all input groups')
 result={}
 for group,files in manifest.items():
  require(isinstance(files,list) and files,'input group is empty: '+group)
  rows=[];ids=set()
  for item in files:
   require(isinstance(item,dict) and text(item.get('id')) and text(item.get('path')),'invalid input-file entry')
   require(item['id'] not in ids,'duplicate dependency id');ids.add(item['id'])
   path=Path(item['path']);path=path if path.is_absolute() else root/path
   require(path.is_file(),'missing declared input: '+item['id'])
   rows.append((item['id'],sha(path.read_bytes())))
  if group in {'script','paragraphs'}:
   require(len(rows)==1,group+' must identify one actual source file');result[group]=rows[0][1]
  else:result[group]=sha(json.dumps(sorted(rows),separators=(',',':')).encode())
 return result

def validate(ledger,script_bytes,paragraph_bytes,current_inputs,gate='assembly',actual_evidence=None,output_sha256=None):
 require(gate in {'structural','assembly','final'},'unknown gate')
 current=digest(current_inputs)
 require(current_inputs['script']==sha(script_bytes),'current input snapshot does not match actual script')
 require(current_inputs['paragraphs']==sha(paragraph_bytes),'current input snapshot does not match actual paragraph file')
 source=json.loads(paragraph_bytes);paragraphs=source['paragraphs']
 require(isinstance(paragraphs,list) and paragraphs,'no source paragraphs')
 ids=[p['id'] for p in paragraphs];require(len(set(ids))==len(ids),'duplicate source paragraph ids')
 titles=[x[2:].strip() for x in script_bytes.decode().splitlines() if x.startswith('# ')]
 require(len(titles)==1,'expected exactly one source H1 title');title=titles[0]
 body=script_bytes.decode().split('\n',1)[1].strip()
 require([x.strip() for x in re.split(r'\n\s*\n',body)]==[p['text'].strip() for p in paragraphs],'paragraph file does not match frozen script body')
 require(isinstance(ledger,dict) and ledger.get('schema_version')==1,'unsupported ledger schema')
 identity=ledger.get('identity',{})
 require(identity.get('title')==title and identity.get('script_sha256')==sha(script_bytes),'frozen script identity mismatch')
 require(ledger.get('input_digest')==current,'stale or missing top-level input digest')
 require(ledger.get('status') in {'candidate','rejected-quality','superseded','reviewed'},'unknown ledger status')
 evidence=ledger.get('evidence');require(isinstance(evidence,dict),'evidence registry missing')
 for key,item in evidence.items():
  require(text(key) and isinstance(item,dict) and text(item.get('artifact_ref')) and text(item.get('scope')),'invalid evidence record')
  require(isinstance(item.get('artifact_sha256'),str) and re.fullmatch('[0-9a-f]{64}',item['artifact_sha256']),'evidence needs artifact SHA-256')
  require(item.get('input_digest')==current,'stale evidence dependency digest: '+key)
 if gate!='structural':
  require(isinstance(actual_evidence,dict),'actual evidence files must be rehashed for assembly/final')
  require(set(actual_evidence)==set(evidence),'actual evidence file IDs must match ledger')
  require(all(actual_evidence[k]==evidence[k]['artifact_sha256'] for k in evidence),'evidence artifact bytes changed')
 if gate=='final':
  final_id=ledger.get('final_artifact_evidence')
  require(isinstance(final_id,str) and final_id in evidence,'final artifact evidence ID missing')
  require(output_sha256 is not None and output_sha256==evidence[final_id]['artifact_sha256'],'final output does not match reviewed artifact')
  for name in ['technical','playback','audio_content']:
   require(final_id in ledger.get('quality',{}).get(name,{}).get('evidence',[]),'final review does not reference actual output: '+name)
 blockers=[]
 def review(record,label,needed=False):
  require(isinstance(record,dict) and record.get('status') in STATUSES,'unknown/missing review status: '+label)
  status=record['status'];refs=record.get('evidence',[])
  require(isinstance(refs,list) and all(isinstance(x,str) and x in evidence for x in refs),'dangling evidence: '+label)
  if status=='pass':
   require(record.get('reviewer_kind') in {'human','agent'} and text(record.get('reviewer')),'pass lacks accountable reviewer: '+label)
   require(text(record.get('scope')) and refs,'pass lacks scope or evidence: '+label)
   require(record.get('input_digest')==current,'stale passed review: '+label)
  if needed and status!='pass':blockers.append(label+': '+status)
 labels=ledger.get('labels',{})
 for name in ['cover','video_header']:
  item=labels.get(name,{})
  require(item.get('title')==title,name+' title does not match frozen script')
  review(item.get('review'),name,gate!='structural')
 shots=ledger.get('shots');cues=ledger.get('narration_cues')
 require(isinstance(shots,dict) and shots,'no shot registry');require(isinstance(cues,dict) and cues,'no narration-cue registry')
 for sid,shot in shots.items():
  require(text(sid) and isinstance(shot,dict),'invalid shot record')
  owners=shot.get('paragraph_ids');require(isinstance(owners,list) and owners and len(owners)==len(set(owners)) and all(x in ids for x in owners),'invalid shot paragraph refs')
  require(text(shot.get('version')),'shot version missing')
  for kind in ['content','visual','continuity']:review(shot.get(kind),sid+'/'+kind,gate!='structural')
 for cid,cue in cues.items():
  require(text(cid) and isinstance(cue,dict) and cue.get('paragraph_id') in ids and text(cue.get('source_text')),'invalid cue')
 rows=ledger.get('paragraphs');require(isinstance(rows,list) and [p.get('id') for p in rows]==ids,'paragraph IDs missing, extra or reordered')
 used_shots=set();used_cues=set();claim_ids=set()
 for row,para in zip(rows,paragraphs):
  pid=para['id'];claims=row.get('claims');require(isinstance(claims,list) and claims,'no claims: '+pid)
  require(''.join(c.get('source_text','') for c in claims)==para['text'].strip(),'claim source coverage mismatch: '+pid)
  cueids=row.get('narration_cue_ids');require(isinstance(cueids,list) and cueids and len(cueids)==len(set(cueids)),'invalid paragraph cue IDs')
  require(all(x in cues and cues[x]['paragraph_id']==pid for x in cueids),'dangling/misowned paragraph cue')
  require(''.join(cues[x]['source_text'] for x in cueids)==para['text'].strip(),'narration cue text coverage mismatch: '+pid)
  used_cues.update(cueids)
  for claim in claims:
   cid=claim.get('id');require(text(cid) and cid not in claim_ids,'duplicate or missing claim ID');claim_ids.add(cid)
   concepts=claim.get('concepts');require(isinstance(concepts,list) and concepts and all(text(x) for x in concepts),'claim concepts missing: '+cid)
   require(text(claim.get('visual_explanation')),'visual explanation missing: '+cid)
   refs=claim.get('narration_cue_ids');require(isinstance(refs,list) and refs and all(x in cueids for x in refs),'dangling claim cue: '+cid)
   require(claim['source_text'] in ''.join(cues[x]['source_text'] for x in refs),'claim cue text does not contain its source: '+cid)
   refs=claim.get('shot_ids');require(isinstance(refs,list) and refs and all(x in shots and pid in shots[x]['paragraph_ids'] for x in refs),'dangling/misowned claim shot: '+cid)
   used_shots.update(refs);review(claim.get('semantic_review'),cid+'/semantic',gate!='structural')
 require(used_shots==set(shots),'unmapped shot registry entries');require(used_cues==set(cues),'unmapped cue registry entries')
 quality=ledger.get('quality',{})
 require(text(quality.get('benchmark_ref')),'task-specific quality benchmark missing')
 for name in ['benchmark_comparison','input_completeness']:review(quality.get(name),name,gate!='structural')
 for name in ['technical','playback','audio_content']:review(quality.get(name),name,gate=='final')
 if gate!='structural' and ledger['status'] in {'rejected-quality','superseded'}:blockers.append('historical ledger is '+ledger['status'])
 require(not blockers,'blocked: '+'; '.join(blockers))
 return {'mechanical_consistency':'pass','gate':gate,'paragraphs':len(ids),'claims':len(claim_ids),'shots':len(shots),'input_digest':current,'semantic_or_visual_truth_verified_by_script':False,'meaning':'Declared reviews and references are consistent; inspect actual evidence before production decisions.'}

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
 s=sub.add_parser('snapshot');s.add_argument('--manifest',type=Path,required=True);s.add_argument('--output',type=Path,required=True)
 c=sub.add_parser('check');c.add_argument('--ledger',type=Path,required=True);c.add_argument('--script',type=Path,required=True);c.add_argument('--paragraphs',type=Path,required=True);c.add_argument('--inputs',type=Path);c.add_argument('--manifest',type=Path);c.add_argument('--evidence-manifest',type=Path);c.add_argument('--output-artifact',type=Path);c.add_argument('--gate',choices=['structural','assembly','final'],default='assembly')
 a=p.parse_args()
 try:
  if a.command=='snapshot':
   result=snapshot(json.loads(a.manifest.read_text()),a.manifest.parent)
   with a.output.open('x') as f:f.write(json.dumps(result,indent=2)+'\n')
  else:
   require(a.gate=='structural' or a.manifest is not None,'assembly/final requires --manifest to rehash current dependencies')
   require(a.manifest is not None or a.inputs is not None,'provide --manifest or structural --inputs')
   inputs=snapshot(json.loads(a.manifest.read_text()),a.manifest.parent) if a.manifest else json.loads(a.inputs.read_text())
   actual=None
   if a.gate!='structural':
    require(a.evidence_manifest is not None,'assembly/final requires --evidence-manifest with actual evidence files')
    paths=json.loads(a.evidence_manifest.read_text());require(isinstance(paths,dict),'evidence manifest must map IDs to file paths')
    actual={key:sha((a.evidence_manifest.parent/Path(path)).read_bytes()) for key,path in paths.items()}
   require(a.gate!='final' or a.output_artifact is not None,'final requires --output-artifact')
   result=validate(json.loads(a.ledger.read_text()),a.script.read_bytes(),a.paragraphs.read_bytes(),inputs,a.gate,actual,sha(a.output_artifact.read_bytes()) if a.output_artifact else None)
  print(json.dumps(result,ensure_ascii=False,indent=2))
 except (GateError,KeyError,TypeError,ValueError,OSError) as e:print(json.dumps({'mechanical_consistency':'fail','reason':str(e)},ensure_ascii=False));raise SystemExit(1)
if __name__=='__main__':main()
