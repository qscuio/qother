"""Actual output technical checks. Never claims listening or continuous viewing."""
import json,subprocess,hashlib,wave,math
from pathlib import Path
import numpy as np
from scipy.signal import correlate,correlation_lags,resample_poly
from compositor import R,OLD,ROWS,CLIPS,FPS

def run(video):
 video=Path(video);out=R/'qa/decoded';out.mkdir(parents=True,exist_ok=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(video)]));vs=next(s for s in probe['streams'] if s['codec_type']=='video')
 decode=subprocess.run(['ffmpeg','-v','error','-i',str(video),'-f','null','-'],capture_output=True,text=True)
 data=subprocess.check_output(['ffmpeg','-v','error','-i',str(video),'-map','0:a:0','-f','s16le','-ac','1','-ar','24000','-']);actual=np.frombuffer(data,'<i2').astype(float)/32768;sr=24000
 checks=[]
 for pid,row in ROWS.items():
  with wave.open(str(OLD/'audio'/f'{pid}.edge.wav')) as w:
   src=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768
   if w.getnchannels()>1:src=src.reshape(-1,w.getnchannels()).mean(axis=1)
   if w.getframerate()!=sr:
    g=math.gcd(sr,w.getframerate());src=resample_poly(src,sr//g,w.getframerate()//g)
  pos=round(row['start']*sr);pad=2400;segment=actual[pos-pad:pos+len(src)+pad]
  corr=correlate(segment,src,mode='valid',method='fft');lag=int(np.argmax(corr))-pad
  aligned=actual[pos+lag:pos+lag+len(src)];coef=float(np.corrcoef(src,aligned)[0,1]);checks.append({'id':pid,'start_seconds':row['start'],'audio_lag_samples':lag,'audio_lag_seconds':lag/sr,'waveform_correlation':coef,'source_sha256':hashlib.sha256((OLD/'audio'/f'{pid}.edge.wav').read_bytes()).hexdigest()})
  for label,t in [('start',row['start']+.08),('mid',row['start']+row['narration_duration']/2),('end',row['end']-.12)]:
   subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1',str(out/f'{pid}-{label}.png')],check=True)
 for label,t in [('COVER-start',.05),('COVER-end',1.95)]+[(f'INSERT-MW-{position}',next(r['start'] for r in CLIPS if r['id']=='INSERT-MW')+dt) for position,dt in [('start',.05),('mid',4),('end',7.95)]]:
  subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(video),'-frames:v','1',str(out/f'{label}.png')],check=True)
 # Scan every decoded frame at reduced resolution for exact freezes and cuts.
 proc=subprocess.Popen(['ffmpeg','-v','error','-i',str(video),'-an','-vf','scale=160:90','-pix_fmt','gray','-f','rawvideo','-'],stdout=subprocess.PIPE);prev=None;diff=[];count=0
 while True:
  b=proc.stdout.read(160*90)
  if not b:break
  if len(b)!=160*90:raise RuntimeError('Incomplete frame')
  cur=np.frombuffer(b,'uint8').astype(np.int16)
  if prev is not None:diff.append(float(np.abs(cur-prev).mean()))
  prev=cur;count+=1
 assert proc.wait()==0
 freeze=[];start=None
 for i,v in enumerate(diff+[1]):
  if v==0 and start is None:start=i
  elif v!=0 and start is not None:
   if i-start>=12:freeze.append({'start':start/FPS,'end':(i+1)/FPS,'frames':i-start+1})
   start=None
 expected=48+sum(r['frames'] for r in CLIPS)
 report={'video_sha256':hashlib.sha256(video.read_bytes()).hexdigest(),'decoded_frames':count,'expected_frames':expected,'dimensions':[vs['width'],vs['height']],'frame_rate':vs['avg_frame_rate'],'full_decode_returncode':decode.returncode,'full_decode_stderr':decode.stderr,'audio_peak':float(np.abs(actual).max()),'audio_clipped_samples':int(np.sum(np.abs(actual)>=.9999)),'paragraph_audio_binding':checks,'downsampled_equal_runs_12_frames_or_more':freeze,'difference_resolution':[160,90],'difference_interpretation':'Reduced grayscale equality is a motion-screening flag, not exact full-resolution freeze proof','frame_difference_min_mean_max':[float(np.min(diff)),float(np.mean(diff)),float(np.max(diff))],'technical_checks_pass':decode.returncode==0 and count==expected and [vs['width'],vs['height']]==[1280,720] and vs['avg_frame_rate']=='24/1' and all(abs(c['audio_lag_seconds'])<.04 and c['waveform_correlation']>.98 for c in checks),'continuous_playback':'not-run','spoken_content_listening':'not-run','actual_decoded_still_visual_review':'pending independent inspection'}
 (R/'qa/technical-output.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 import sys;run(sys.argv[1])
