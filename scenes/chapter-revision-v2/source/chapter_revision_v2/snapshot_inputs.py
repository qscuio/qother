"""Freeze actual dependencies. Does not grant any review or reuse stale evidence."""
import json,sys,hashlib
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R.parent/'workflow-gates-staging/scripts'))
from validate_production_gate import snapshot,digest

def main():
 files=lambda ps:[{'id':str(p.relative_to(R)) if p.is_relative_to(R) else str(p),'path':str(p)} for p in ps]
 used_snapshots=[];used_snapshot_code=[]
 for meta in sorted((R/'output/segments').glob('*.json')):
  data=json.loads(meta.read_text())
  if not data.get('source_snapshot'):continue
  snap=Path(data['source_snapshot']);used_snapshots.append(snap);used_snapshot_code.extend(p for p in snap.parent.rglob('*') if p.is_file() and p.suffix in {'.py','.cpp','.so','.h','.c'})
 old=R.parent/'full_chapter_v1';manifest={'script':files([R/'script/script.md']),'paragraphs':files([R/'script/paragraphs.json']),'audio':files(sorted((old/'audio').glob('P??.edge.wav'))+sorted((old/'audio').glob('P??.edge.json'))),'assets':files(sorted((R/'output/segments').glob('P??.mp4'))+sorted((R/'output/segments').glob('INSERT-MW.mp4'))+sorted((R/'output/segments').glob('COVER.mp4'))+[old/'assets/host-circle.png',old/'cover-system/prologue-cover-candidate-v2.png',R.parent/'deliverables/P10-section-preview-v2.mp4',Path('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc')]+[p for p in sorted((R/'scenes').rglob('*.png')) if 'keyframes' not in p.parts or p.name=='P05-entry-gas.png']),'timeline':files([R/'timeline.json',R/'style-config.json',R/'qa/runtime-capability.json',old/'audio/timeline.json']+sorted((R/'output/segments').glob('P??.json'))+sorted((R/'output/segments').glob('INSERT-MW.json'))+sorted((R/'output/segments').glob('COVER.json'))+used_snapshots),'storyboard':files([R/'storyboard.json',R/'qa/source-binding-audit.json']),'render_code':files(sorted(R.glob('*.py'))+sorted(p for p in (R/'scenes').rglob('*') if p.is_file() and p.suffix in {'.py','.cpp','.so','.h','.c','.npy','.npz'})+sorted(set(used_snapshot_code)))}
 (R/'local-inputs.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2));snap=snapshot(manifest,R);dg=digest(snap);(R/f'input-snapshot-{dg[:12]}.json').write_text(json.dumps(snap,indent=2))
 ledger=json.loads((R/'production-gate.json').read_text())
 if ledger['input_digest']!=dg and ledger['evidence']:raise RuntimeError('Inputs changed after evidence. Re-review affected scene/records; no automatic reassignment.')
 ledger['input_digest']=dg;(R/'production-gate.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2));(R/'local-evidence.json').write_text('{}');print(dg)
if __name__=='__main__':main()
