"""Full revision assembly, only after real input-bound assembly gate and root go."""
import json,math,wave,subprocess,sys,hashlib
from pathlib import Path
import numpy as np
from scipy.signal import resample_poly
from compositor import R,OLD,ROWS,CLIPS,FPS
GATE=R.parent/'workflow-gates-staging/scripts/validate_production_gate.py'
def run(a):subprocess.run(a,check=True)
def assemble():
 run([sys.executable,str(GATE),'check','--ledger',str(R/'production-gate.json'),'--script',str(R/'script/script.md'),'--paragraphs',str(R/'script/paragraphs.json'),'--manifest',str(R/'local-inputs.json'),'--evidence-manifest',str(R/'local-evidence.json'),'--gate','assembly'])
 go=json.loads((R/'qa/root-assembly-go.json').read_text());assert go.get('decision')=='proceed' and go.get('reviewer'), 'Root approval required'
 out=R/'output';parts=[];sr=24000;pcm=[np.zeros(sr*2)];cover=OLD/'cover-system/prologue-cover-candidate-v2.png'
 cover_clip=out/'segments/COVER.mp4';cover_meta=cover_clip.with_suffix('.json')
 if cover_clip.exists() and cover_meta.exists():
  cm=json.loads(cover_meta.read_text());assert cm['source_sha256']==hashlib.sha256(cover.read_bytes()).hexdigest() and cm['video_sha256']==hashlib.sha256(cover_clip.read_bytes()).hexdigest() and cm['frames']==48,'Cover changed after review'
 else:
  run(['ffmpeg','-v','error','-y','-loop','1','-i',str(cover),'-t','2','-vf','scale=1280:720','-r','24','-an','-c:v','libx264','-preset','veryfast','-crf','19','-pix_fmt','yuv420p','-video_track_timescale','12288',str(cover_clip)])
 parts.append(cover_clip)
 for row in CLIPS:
  pid=row['id']
  segment=out/'segments'/f'{pid}.mp4';assert segment.exists()
  recorded=json.loads(segment.with_suffix('.json').read_text());assert recorded['video_sha256']==hashlib.sha256(segment.read_bytes()).hexdigest(),f'{pid}: encoded clip bytes changed'
  assert recorded['frames']==row['frames'] and recorded['duration']==row['duration'],f'{pid}: scene timing changed after render'
  parts.append(segment)
  if pid=='INSERT-MW':pcm.append(np.zeros(sr*8));continue
  with wave.open(str(OLD/'audio'/f'{pid}.edge.wav')) as w:
   assert w.getsampwidth()==2
   x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(np.float64)/32768
   if w.getnchannels()>1:x=x.reshape(-1,w.getnchannels()).mean(axis=1)
   if w.getframerate()!=sr:
    g=math.gcd(sr,w.getframerate());x=resample_poly(x,sr//g,w.getframerate()//g)
  n=round(row['duration']*sr);assert len(x)<=n;pcm.append(np.pad(x*10**(-1/20),(0,n-len(x))))
 with wave.open(str(out/'narration.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(np.rint(np.clip(np.concatenate(pcm),-1,1)*32767).astype('<i2').tobytes())
 (out/'concat.txt').write_text(''.join(f"file '{p}'\n" for p in parts))
 target=out/'地球往事_序章_地球的来处_修订预览_v2.mp4'
 run(['ffmpeg','-v','warning','-y','-f','concat','-safe','0','-i',str(out/'concat.txt'),'-i',str(out/'narration.wav'),'-map','0:v:0','-map','1:a:0','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(target)])
 def stamp(t):
  n=round(t*1000);h,n=divmod(n,3600000);m,n=divmod(n,60000);s,n=divmod(n,1000);return f'{h:02}:{m:02}:{s:02},{n:03}'
 captions=[]
 for row in ROWS.values():
  for c in row['cues']:captions.append(f'{len(captions)+1}\n{stamp(row["start"]+c["start"])} --> {stamp(row["start"]+c["end"])}\n{c["text"]}\n')
 (out/'字幕_服务端词边界_未核听.srt').write_text('\n'.join(captions));print(target)
if __name__=='__main__':assemble()
