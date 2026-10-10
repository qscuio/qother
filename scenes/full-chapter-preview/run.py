"""Explicit local full-chapter build or cheap single-frame inspection. No network/TTS."""
import argparse,hashlib,json,time
from pathlib import Path
import build

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('mode',choices=['frame','full'])
 p.add_argument('--output',type=Path,required=True,help='New output directory; no automatic resume')
 p.add_argument('--timeline',type=Path,required=True,help='Explicit 19-paragraph audio duration manifest; recorded example is bundled')
 p.add_argument('--audio-dir',type=Path,help='Required for full: nineteen local WAV files named in timeline')
 p.add_argument('--boundary-dir',type=Path,help='Optional local P01.edge.json … P19.edge.json with provider boundary lists')
 p.add_argument('--p10-video',type=Path,help='Required for full: original 551-frame 720p24 P10 clip; baked overlays remain')
 p.add_argument('--host',type=Path,help='Optional authorized prepared RGBA circular portrait; no asset bundled')
 p.add_argument('--font',type=Path,help='Installed Chinese font')
 p.add_argument('--bold-font',type=Path,help='Optional installed bold Chinese font; defaults to regular')
 p.add_argument('--paragraph',choices=[f'P{i:02d}' for i in range(1,20) if i!=10],default='P01')
 p.add_argument('--progress',type=float,default=.5)
 a=p.parse_args()
 if not 0<=a.progress<=1:p.error('--progress must be 0..1')
 try:build.configure(a,require_media=a.mode=='full')
 except (ValueError,FileNotFoundError) as e:p.error(str(e))
 if a.mode=='frame':
  pid=a.paragraph;raw=build.audio_info(pid)[0];text=next(x['text'] for x in build.PARAS if x['id']==pid)
  cues=build.cues(text,raw,pid);start=time.perf_counter()
  image=build.overlay(build.module(pid).render(pid,a.progress,1280,720),pid,a.progress*raw,raw,cues)
  path=build.OUT/f'frame-{pid}.png';image.save(path)
  report={'paragraph':pid,'progress':a.progress,'resolution':[1280,720],'host_enabled':build.HOST is not None,'render_and_save_seconds':time.perf_counter()-start,'frame_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'subtitle_timing':sorted(set(c['timing'] for c in cues)),'audio_rendered':False,'scope':'one frame only; not full playback'}
  (build.OUT/'frame-check.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));return
 for para in build.PARAS:
  if para['id']=='P10':build.p10()
  else:build.render_scene(para['id'])
 # Import after explicit configure so modules receive initialized local inputs.
 import assemble,qa
 assemble.assemble();qa.qa()
if __name__=='__main__':main()
