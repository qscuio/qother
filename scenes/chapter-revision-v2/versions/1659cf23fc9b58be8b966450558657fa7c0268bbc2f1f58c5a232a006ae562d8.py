"""Render only reviewed sections; full assembly is separately gated."""
import json,subprocess,time,sys,hashlib
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
 out=R/'output/segments';out.mkdir(parents=True,exist_ok=True);target=out/f'{pid}.mp4';meta=out/f'{pid}.json'
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
 partial.replace(target);meta.write_text(json.dumps({**row,'approval_sha256':signature,'video_sha256':sha(target),'render_wall_seconds':time.monotonic()-start},ensure_ascii=False,indent=2));print('Rendered',pid,flush=True)
if __name__=='__main__':
 for pid in sys.argv[1:]:render(pid)
