import json,subprocess,time,wave,hashlib
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
from build import ROOT,OUT,FONT,PARAS
from validate_manifest import validate_manifest

def qa():
 start=time.monotonic();manifest=json.loads((OUT/'content_manifest.json').read_text());video=OUT/'地球往事_第一章_完整预览_v1.mp4';target=OUT/'qa';validate_manifest(manifest,PARAS)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(video)]));probe['format']['filename']=video.name;(target/'ffprobe.json').write_text(json.dumps(probe,indent=2))
 v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
 expected=sum(r['frames'] for r in manifest['paragraphs'])+8*24
 assert int(v['nb_read_frames'])==expected,(v['nb_read_frames'],expected)
 assert v['width']==1280 and v['height']==720 and v['r_frame_rate']=='24/1'
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
 assert decode.returncode==0 and not decode.stderr.strip(),decode.stderr
 samples=[]
 for row in manifest['paragraphs']:
  for fraction in [.15,.5,.85]:
   t=row['start']+row['narration_duration']*fraction;name=f'decoded-{row["id"]}-{round(fraction*100)}.png';path=target/name
   subprocess.run(['ffmpeg','-v','error','-n','-ss',str(t),'-i',str(video),'-frames:v','1',str(path)],check=True)
   arr=np.asarray(Image.open(path));samples.append({'paragraph':row['id'],'time':t,'file':name,'std':float(arr.std()),'mean':float(arr.mean())});assert arr.std()>8
 # All decoded frames hashed: repeated runs must be bounded except static credit card.
 md5=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-map','0:v:0','-f','framemd5','-']).decode();(target/'decoded_framemd5.txt').write_text(md5)
 hashes=[l.rsplit(',',1)[-1].strip() for l in md5.splitlines() if l and not l.startswith('#')]
 runs=[];begin=0
 for i in range(1,len(hashes)+1):
  if i==len(hashes) or hashes[i]!=hashes[begin]:
   if i-begin>1:runs.append({'start_frame':begin,'frames':i-begin,'start_seconds':begin/24})
   begin=i
 main_end=sum(r['frames'] for r in manifest['paragraphs']);main_runs=[r for r in runs if r['start_frame']<main_end-2]
 with wave.open(str(OUT/'full_narration.wav')) as w:
  x=np.frombuffer(w.readframes(w.getnframes()),'<i2')/32768;audioduration=len(x)/w.getframerate()
 report={'video':video.name,'complete_paragraphs':19,'frozen_text_coverage':'all 19 paragraphs exactly preserved in subtitle cue manifest','frame_count':len(hashes),'expected_frame_count':expected,'full_decode_errors':decode.stderr,'video_duration':float(v['duration']),'audio_duration':float(a['duration']),'master_pcm_duration':audioduration,'audio_peak':float(np.max(np.abs(x))),'audio_finite':bool(np.isfinite(x).all()),'audio_full_scale_samples':int(np.sum(np.abs(x)>=32767/32768)),'sampled_decoded_frames':samples,'repeated_frame_runs':runs,'longest_main_content_identical_run':max([r['frames'] for r in main_runs],default=1),'continuous_browser_playback':'Not performed by this decode-only utility','audio_listening':'Not independently verified; provider text/word boundaries and signal checked; user disliked previous timbre, present voice temporary','P10':'Visual-only reused and uniformly retimed, baked caption timing approximate; fresh unified voice','qa_wall_seconds':time.monotonic()-start}
 (OUT/'QA.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 for page in range(2):
  subset=manifest['paragraphs'][page*10:(page+1)*10];sheet=Image.new('RGB',(1280,math_ceil(len(subset)/2)*388),'#10141a');d=ImageDraw.Draw(sheet)
  for i,row in enumerate(subset):
   im=Image.open(target/f'decoded-{row["id"]}-50.png').resize((640,360));x=(i%2)*640;y=(i//2)*388;sheet.paste(im,(x,y));d.text((x+8,y+362),row['id']+' '+row['heading'],font=ImageFont.truetype(FONT,16),fill='white')
  sheet.save(target/f'decoded-contact-sheet-{page+1}.jpg',quality=90)
 print(json.dumps({k:v for k,v in report.items() if k not in ['sampled_decoded_frames','repeated_frame_runs']},ensure_ascii=False,indent=2))
def math_ceil(x):return int(np.ceil(x))
# Invoke via run.py after explicit local input configuration.
