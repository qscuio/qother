"""Render only reviewed sections; full assembly is separately gated."""
import json,subprocess,time,sys,hashlib,os,shutil,uuid
from pathlib import Path
from compositor import R,ALL_ROWS,FPS,frame,module

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def render(pid):
 row=ALL_ROWS[pid];m=module(pid);approval_path=R/'qa'/f'{pid}-render-approval.json'
 if not approval_path.exists():raise RuntimeError(f'{pid}: no per-section actual-frame review approval')
 a=json.loads(approval_path.read_text())
 for k in ['content','visual','keyframe_sequence']:
  if a.get(k)!='pass':raise RuntimeError(f'{pid}: {k} not passed')
 if not a.get('reviewer') or not a.get('evidence'):raise RuntimeError('Missing accountable reviewer/evidence')
 if a.get('renderer_sha256')!=sha(m.__file__):raise RuntimeError('Scene changed since review')
 if a.get('compositor_sha256')!=sha(R/'compositor.py'):raise RuntimeError('Compositor changed since review')
 for f,h in a.get('dependency_hashes',{}).items():
  if sha(R/f)!=h:raise RuntimeError('Reviewed dependency changed: '+f)
 out=Path(os.environ.get('CHAPTER_OUTPUT_ROOT',str(R/'output')))/'segments';out.mkdir(parents=True,exist_ok=True);target=out/f'{pid}.mp4';meta=out/f'{pid}.json'
 signature=sha(approval_path)
 if target.exists() and meta.exists() and json.loads(meta.read_text()).get('approval_sha256')==signature:return
 partial=out/f'{pid}.partial.mp4';log=open(out/f'{pid}.log','w');start=time.monotonic()
 cmd=['ffmpeg','-v','warning','-y','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r','24','-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','12288','-movflags','+faststart',str(partial)]
 proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log)
 try:
  for f in range(row['frames']):
   proc.stdin.write(frame(pid,f/FPS).tobytes())
   if f%120==0:(out/f'{pid}-progress.json').write_text(json.dumps({'frame':f,'frames':row['frames'],'elapsed':time.monotonic()-start}))
  proc.stdin.close();rc=proc.wait();assert rc==0,rc
 except:proc.kill();raise
 partial.replace(target);meta.write_text(json.dumps({**row,'approval_sha256':signature,'video_sha256':sha(target),'render_wall_seconds':time.monotonic()-start,'source_snapshot':os.environ.get('CHAPTER_SOURCE_SNAPSHOT'),'review_scope':'keyframes approved; motion/audio/adjacent boundaries independently pending'},ensure_ascii=False,indent=2));print('Rendered',pid,flush=True)
def freeze_and_render(pid):
 approval=R/'qa'/f'{pid}-render-approval.json'
 if not approval.exists():raise RuntimeError(f'{pid}: missing actual-frame review approval')
 base=R/'qa/render-sources'/f'{pid}-{sha(approval)[:10]}-{uuid.uuid4().hex[:6]}'/'root'
 frozen=base/'chapter_revision_v2'
 paths=list(R.glob('*.py'))+[R/'timeline.json',R/'style-config.json',approval]+[p for p in (R/'scenes').rglob('*') if p.is_file() and p.suffix in {'.py','.cpp','.so','.h','.c','.npy','.npz'}]+[p for p in (R/'scenes').rglob('*.png') if 'keyframes' not in p.parts or p.name=='P05-entry-gas.png']
 old=R.parent/'full_chapter_v1';paths+=list((old/'audio').glob('P??.edge.wav'))+list((old/'audio').glob('P??.edge.json'))+[old/'audio/timeline.json',old/'assets/host-circle.png',old/'cover-system/prologue-cover-candidate-v2.png']
 records={}
 for source in paths:
  rel=source.relative_to(R.parent);target=base/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);records[str(rel)]=sha(target)
 a=json.loads(approval.read_text())
 if a.get('renderer_source_override'):
  override=R/a['renderer_source_override'];assert sha(override)==a['renderer_sha256'],'Approved preserved source changed'
  folder='early' if int(pid[1:])<5 else 'stellar' if int(pid[1:])<10 else 'p10' if int(pid[1:])==10 else 'planet'
  target=frozen/'scenes'/folder/'renderer.py';shutil.copyfile(override,target);records[str(target.relative_to(base))]=sha(target)
 manifest=base.parent/'source-snapshot.json';manifest.write_text(json.dumps({'paragraph':pid,'snapshot_saved_before_render':True,'files':records,'reason':'Immutable source tree protects rendering from concurrent working-source edits.'},indent=2))
 env=dict(os.environ,CHAPTER_OUTPUT_ROOT=str(R/'output'),CHAPTER_SOURCE_SNAPSHOT=str(manifest))
 subprocess.run([sys.executable,str(frozen/'render.py'),'--frozen',pid],env=env,check=True)
if __name__=='__main__':
 if '--frozen' in sys.argv:render(sys.argv[-1])
 else:
  for pid in sys.argv[1:]:freeze_and_render(pid)
